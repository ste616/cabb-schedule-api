# A library to handle dealing with v3 of the ATCA calibrator database.
from requests import Session
from xml.dom import minidom
import json
import numpy as np
import errors

class calibrator:
    def __init__(self, details=None):
        # This is a single calibrator from the database.
        self.__calibratorDetails = {
            'name': "",
            'rightAscension': "",
            'declination': "",
            'fluxDensities': [],
            'measurements': None
        }
        if details is not None:
            if 'name' in details:
                self.setName(details['name'])
            if 'rightAscension' in details:
                self.setRightAscension(details['rightAscension'])
            if 'declination' in details:
                self.setDeclination(details['declination'])
            if 'fluxDensities' in details:
                for i in xrange(0, len(details['fluxDensities'])):
                    self.addFluxDensity(details['fluxDensities'][i]['frequency'],
                                        details['fluxDensities'][i]['fluxDensity'])

    def setName(self, name=None):
        if name is not None:
            self.__calibratorDetails['name'] = name
        return self

    def getName(self):
        return self.__calibratorDetails['name']
    
    def setRightAscension(self, ra=None):
        if ra is not None:
            self.__calibratorDetails['rightAscension'] = ra
        return self

    def getRightAscension(self):
        return self.__calibratorDetails['rightAscension']
    
    def setDeclination(self, dec=None):
        if dec is not None:
            self.__calibratorDetails['declination'] = dec
        return self

    def getDeclination(self):
        return self.__calibratorDetails['declination']
    
    def addFluxDensity(self, frequency=None, fluxDensity=None):
        if frequency is not None and fluxDensity is not None:
            # Check we don't already have an element with this frequency.
            foundFrequency = False
            for i in xrange(0, len(self.__calibratorDetails['fluxDensities'])):
                if (self.__calibratorDetails['fluxDensities'][i]['frequency'] == int(frequency)):
                    self.__calibratorDetails['fluxDensities'][i]['fluxDensity'] = float(fluxDensity)
                    foundFrequency = True
            if foundFrequency == False:
                self.__calibratorDetails['fluxDensities'].append({ 'frequency': int(frequency),
                                                                   'fluxDensity': float(fluxDensity) })
        return self

    def getFluxDensities(self, frequency=None):
        if frequency is not None:
            for i in xrange(0, len(self.__calibratorDetails['fluxDensities'])):
                if (self.__calibratorDetails['fluxDensities'][i]['frequency'] == int(frequency)):
                    return [ self.__calibratorDetails['fluxDensities'][i] ]
            return None
        return self.__calibratorDetails['fluxDensities']

    def fetchDetails(self):
        # Get all the measurements from the database.
        if self.__calibratorDetails['measurements'] is not None:
            # We already have the measurements.
            return self
        
        data = { 'action': "source_all_details", 'source': self.__calibratorDetails['name'] }
        response = __communications(data, "json")
        if response is not None and response['source_name'] == self.__calibratorDetails['name']:
            self.__calibratorDetails['measurements'] = response['measurements']
        return self

    def collateDetails(self):
        # Take all the measurements and determine some secondary properties from them.
        if self.__calibratorDetails['measurements'] is None:
            # No measurements.
            return self

        # Go through all of the measurements.
        arrayNames = { '6A': "6km", '6B': "6km", '6C': "6km", '6D': "6km",
                       '1.5A': "1.5km", '1.5B': "1.5km", '1.5C': "1.5km", '1.5D': "1.5km",
                       '750A': "750m", '750B': "750m", '750C': "750m", '750D': "750m",
                       'EW367': "small", 'EW352': "small",
                       'H214': "small", 'H168': "small", 'H75': "small" }
        bandNames = [ "16cm", "4cm", "15mm", "7mm", "3mm" ]
        bandEvals = { "16cm": 2100, "4cm": 5500, "15mm": 17000, "7mm": 33000, "3mm": 93000 }
        arraySpecs = {}
        for a in arrayNames:
            if arrayNames[a] not in arraySpecs:
                arraySpecs[arrayNames[a]] = {}
                for i in xrange(0, len(bandNames)):
                    arraySpecs[arrayNames[a]][bandNames[i]] = {
                        'closurePhases': [], 'defects': [],
                        'fluxDensities': [],
                        'closurePhaseMedian': None, 'defectMedian': None,
                        'fluxDensityMedian': None, 'fluxDensityStdDev': None,
                        'qualityFlag': None
                    }
        for i in xrange(0, len(self.__calibratorDetails['measurements'])):
            # Work out closure phase and defect as a function of band and array.
            r = self.__calibratorDetails['measurements'][i]
            a = r['array'].split()[0]
            b = r['frequency_band']
            if a in arrayNames:
                arr = arrayNames[a]
                for j in xrange(0, len(r['frequencies'])):
                    r2 = r['frequencies'][j]
                    for k in xrange(0, len(r2['closure_phases'])):
                        r3 = r2['closure_phases'][k]
                        arraySpecs[arr][b]['closurePhases'].append(float(r3['closure_phase_average']))
                for j in xrange(0, len(r['fluxdensities'])):
                    r2 = r['fluxdensities'][j]
                    arraySpecs[arr][b]['defects'].append((float(r2['fluxdensity_scalar_averaged']) /
                                                          float(r2['fluxdensity_vector_averaged'])) - 1)
                    arraySpecs[arr][b]['fluxDensities'].append(__model2FluxDensity(r2['fluxdensity_fit_coeff'],
                                                                                   bandEvals[b]))
                if len(arraySpecs[arr][b]['closurePhases']) > 0:
                    arraySpecs[arr][b]['closurePhaseMedian'] = np.median(arraySpecs[arr][b]['closurePhases'])
                if len(arraySpecs[arr][b]['defects']) > 0:
                    arraySpecs[arr][b]['defectMedian'] = np.median(arraySpecs[arr][b]['defects'])
                if len(arraySpecs[arr][b]['fluxDensities']) > 0:
                    arraySpecs[arr][b]['fluxDensityMedian'] = np.median(arraySpecs[arr][b]['fluxDensities'])
                    arraySpecs[arr][b]['fluxDensityStdDev'] = np.std(arraySpecs[arr][b]['fluxDensities'])
        # The collation is done, we make some evaluations.
        for a in arraySpecs:
            for b in bandNames:
                r = arraySpecs[a][b]
                if (r['closurePhaseMedian'] is not None and r['defectMedian'] is not None and
                    r['fluxDensityMedian'] is not None and r['fluxDensityStdDev'] is not None):
                    r['qualityFlag'] = 4 # The maximum value.
                    if r['closurePhaseMedian'] > 3:
                        r['qualityFlag'] -= 1
                    if r['closurePhaseMedian'] > 10:
                        r['qualityFlag'] -= 1
                    if r['defectMedian'] > 1.05:
                        r['qualityFlag'] -= 1
                    if r['fluxDensityStdDev'] > (r['fluxDensityMedian'] / 2):
                        r['qualityFlag'] -= 1
        return self
        
class calibratorSearchResponse:
    def __init__(self):
        # A list of sources returned from a calibrator search.
        self.__calibratorList = []

    def addCalibrator(self, calibratorDetails=None, distance=None):
        # Create a new calibrator.
        if (calibratorDetails is not None and distance is not None):
            nc = calibrator(calibratorDetails)
            self.__calibratorList.append({ 'calibrator': nc, 'distance': float(distance) })
            nc.fetchDetails().collateDetails()
            return nc
        else:
            return None

    def getCalibrator(self, index=None):
        if index is not None and index >= 0 and index < len(self.__calibratorList):
            return self.__calibratorList[index]
        return None

    def numCalibrators(self):
        return len(self.__calibratorList)

    def getAllCalibrators(self):
        return self.__calibratorList

def __model2FluxDensity(model=None, frequency=None):
    # Convert an array of model parameters into a flux density.
    # The frequency should be given in MHz.
    if model is not None and frequency is not None:
        logS = float(model[0])
        logF = np.log10(float(frequency) / 1000)
        for i in xrange(1, len(model) - 1):
            logS += float(model[i]) * logF**i
        return 10**logS

def _calibrator__model2FluxDensity(model=None, frequency=None):
    return __model2FluxDensity(model, frequency)    
    
def __getValue(xmlNode=None, tagName=None):
    if (xmlNode is not None and tagName is not None):
        return xmlNode.getElementsByTagName(tagName)[0].childNodes[0].data

def __communications(data=None, parseType=None):
    serverName = "www.narrabri.atnf.csiro.au"
    serverProtocol = "http://"
    serverScript = "/cgi-bin/Calibrators/new/caldb_v3.pl"

    if data is None:
        return None

    session = Session()
    postResponse = session.post(
        url=serverProtocol + serverName + serverScript,
        data=data
    )

    response = {}
    if parseType is None or parseType == "json":
        response = json.loads(postResponse.text)
    elif parseType == "xml":
        response = minidom.parseString(postResponse.text)
    return response

def _calibrator__communications(data=None, parseType=None):
    return __communications(data, parseType)

# A routine to search for a calibrator, given an RA and Dec and a search radius.
def coneSearch(ra=None, dec=None, radius=None, fluxLimit=None, frequencies=None):
    # Form the request to the calibrator database server.
    if fluxLimit is None:
        fluxLimit = 0.2
    if frequencies is None:
        frequencies = [ 5500, 9000 ]
    for i in xrange(0, len(frequencies)):
        frequencies[i] = str(frequencies[i])
        
    data = { 'mode': "cals" }
    if (ra is not None and dec is not None and radius is not None):
        data['radec'] = ra + "," + dec
        data['theta'] = radius
        data['frequencies'] = ",".join(frequencies)
        data['flimit'] = fluxLimit
    print data
        
    xmlresponse = __communications(data, "xml")
    sourceList = xmlresponse.getElementsByTagName('source')
    calList = calibratorSearchResponse()
    for i in xrange(0, len(sourceList)):
        distance = __getValue(sourceList[i], 'distance')
        j = 1
        fluxDensities = []
        while (j > 0):
            try:
                freq = __getValue(sourceList[i], 'ffreq' + str(j))
            except IndexError:
                break

            flux = __getValue(sourceList[i], 'fflux' + str(j))
            fluxDensities.append({ 'frequency': freq, 'fluxDensity': flux })
            j += 1

        calDetails = { 'name': __getValue(sourceList[i], 'name'),
                       'rightAscension': __getValue(sourceList[i], 'rightascension'),
                       'declination': __getValue(sourceList[i], 'declination'),
                       'fluxDensities': fluxDensities
        }
        calList.addCalibrator(calDetails, distance)
    return calList
