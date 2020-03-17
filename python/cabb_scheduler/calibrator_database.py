# A library to handle dealing with v3 of the ATCA calibrator database.
from requests import Session
from xml.dom import minidom
import json
import numpy as np
import cabb_scheduler.errors

arrayNames = { '6A': "6km", '6B': "6km", '6C': "6km", '6D': "6km",
               '1.5A': "1.5km", '1.5B': "1.5km", '1.5C': "1.5km", '1.5D': "1.5km",
               '750A': "750m", '750B': "750m", '750C': "750m", '750D': "750m",
               'EW367': "375m", 'EW352': "375m",
               'H214': "375m", 'H168': "375m", 'H75': "375m" }

class calibrator:
    def __init__(self, details=None):
        # This is a single calibrator from the database.
        self.__calibratorDetails = {
            'name': "",
            'rightAscension': "",
            'declination': "",
            'fluxDensities': [],
            'measurements': None,
            'qualities': None
        }
        if details is not None:
            if 'name' in details:
                self.setName(details['name'])
            if 'rightAscension' in details:
                self.setRightAscension(details['rightAscension'])
            if 'declination' in details:
                self.setDeclination(details['declination'])
            if 'fluxDensities' in details:
                for i in range(0, len(details['fluxDensities'])):
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
            for i in range(0, len(self.__calibratorDetails['fluxDensities'])):
                if (self.__calibratorDetails['fluxDensities'][i]['frequency'] == int(frequency)):
                    self.__calibratorDetails['fluxDensities'][i]['fluxDensity'] = float(fluxDensity)
                    foundFrequency = True
            if foundFrequency == False:
                self.__calibratorDetails['fluxDensities'].append({ 'frequency': int(frequency),
                                                                   'fluxDensity': float(fluxDensity) })
        return self

    def getFluxDensities(self, frequency=None):
        if frequency is not None:
            for i in range(0, len(self.__calibratorDetails['fluxDensities'])):
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

    def fetchQualities(self):
        # Get the quality metric for this calibrator.
        if self.__calibratorDetails['qualities'] is not None:
            # We already have the qualities.
            return self

        data = { 'action': "source_quality", 'source': self.__calibratorDetails['name'] }
        response = __communications(data, "json")
        if response is not None and self.__calibratorDetails['name'] in response:
            self.__calibratorDetails['qualities'] = response[self.__calibratorDetails['name']]
            for a in self.__calibratorDetails['qualities']:
                for b in self.__calibratorDetails['qualities'][a]:
                    if self.__calibratorDetails['qualities'][a][b] is not None:
                        self.__calibratorDetails['qualities'][a][b] = int(self.__calibratorDetails['qualities'][a][b])
        return self

    def getQuality(self, array=None, band=None):
        if array is None:
            return self.__calibratorDetails['qualities']
        elif band is None:
            if array in self.__calibratorDetails['qualities']:
                return self.__calibratorDetails['qualities'][array]
            return self.__calibratorDetails['qualities']
        if array in self.__calibratorDetails['qualities']:
            if band in self.__calibratorDetails['qualities'][array]:
                return self.__calibratorDetails['qualities'][array][band]
            return self.__calibratorDetails['qualities'][array]
        return self.__calibratorDetails['qualities']
    
    def collateDetails(self):
        # Take all the measurements and determine some secondary properties from them.
        if self.__calibratorDetails['measurements'] is None:
            # No measurements.
            return self

        # Go through all of the measurements.
        bandNames = [ "16cm", "4cm", "15mm", "7mm", "3mm" ]
        bandEvals = { "16cm": 2100, "4cm": 5500, "15mm": 17000, "7mm": 33000, "3mm": 93000 }
        arraySpecs = {}
        for a in arrayNames:
            if arrayNames[a] not in arraySpecs:
                arraySpecs[arrayNames[a]] = {}
                for i in range(0, len(bandNames)):
                    arraySpecs[arrayNames[a]][bandNames[i]] = {
                        'closurePhases': [], 'defects': [],
                        'fluxDensities': [],
                        'closurePhaseMedian': None, 'defectMedian': None,
                        'fluxDensityMedian': None, 'fluxDensityStdDev': None,
                        'qualityFlag': None
                    }
        for i in range(0, len(self.__calibratorDetails['measurements'])):
            # Work out closure phase and defect as a function of band and array.
            r = self.__calibratorDetails['measurements'][i]
            a = r['array'].split()[0]
            b = r['frequency_band']
            if a in arrayNames:
                arr = arrayNames[a]
                for j in range(0, len(r['frequencies'])):
                    r2 = r['frequencies'][j]
                    for k in range(0, len(r2['closure_phases'])):
                        r3 = r2['closure_phases'][k]
                        arraySpecs[arr][b]['closurePhases'].append(float(r3['closure_phase_average']))
                for j in range(0, len(r['fluxdensities'])):
                    r2 = r['fluxdensities'][j]
                    arraySpecs[arr][b]['defects'].append((float(r2['fluxdensity_scalar_averaged']) /
                                                          float(r2['fluxdensity_vector_averaged'])) - 1)
                    arraySpecs[arr][b]['fluxDensities'].append(__model2FluxDensity(r2['fluxdensity_fit_coeff'],
                                                                                   bandEvals[b]))
        # The collation is done, we make some evaluations.
        for a in arraySpecs:
            for b in bandNames:
                r = arraySpecs[a][b]
                if len(r['closurePhases']) > 0:
                    r['closurePhaseMedian'] = np.median(r['closurePhases'])
                if len(r['defects']) > 0:
                    r['defectMedian'] = np.median(r['defects'])
                if len(r['fluxDensities']) > 0:
                    r['fluxDensityMedian'] = np.median(r['fluxDensities'])
                    r['fluxDensityStdDev'] = np.std(r['fluxDensities'])
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
        self.__calibrators = { 'list': [], 'bestIndex': None }

    def addCalibrator(self, calibratorDetails=None, distance=None):
        # Create a new calibrator.
        if (calibratorDetails is not None and distance is not None):
            nc = calibrator(calibratorDetails)
            self.__calibrators['list'].append({ 'calibrator': nc, 'distance': float(distance) })
            return nc
        else:
            return None

    def getCalibrator(self, index=None):
        if index is not None and index >= 0 and index < len(self.__calibrators['list']):
            return self.__calibrators['list'][index]
        return None

    def numCalibrators(self):
        return len(self.__calibrators['list'])

    def getAllCalibrators(self):
        return self.__calibrators['list']

    def selectBest(self, array=None):
        # Choose the best calibrator from this list.
        # We do this by looking for the nearest calibrator with quality 4 in the
        # band that we are using.
        # We need to know the array.
        if array is None:
            array = "6km"
        elif array in arrayNames:
            array = arrayNames[array]
        else:
            # The array name might have a version letter at the end.
            tarray = array[:-1]
            if tarray in arrayNames:
                array = arrayNames[tarray]
        
        # Work out the band first.
        firstFrequency = self.__calibrators['list'][0]['calibrator'].getFluxDensities()[0]['frequency']
        bandName = __frequency2BandName(firstFrequency)
        desiredScore = 4
        calFound = False
        calFd = None
        while (calFound == False and desiredScore > 1):
            for i in range(0, len(self.__calibrators['list'])):
                tcal = self.__calibrators['list'][i]['calibrator']
                tFd = tcal.getFluxDensities(firstFrequency)[0]['fluxDensity']
                if tcal is not None and (calFound == False or
                                         (calFound == True and tFd >= 2 * calFd and
                                          self.__calibrators['list'][i]['distance'] < 10)):
                    tcal.fetchQualities()
                    tqual = tcal.getQuality(array, bandName)
                    if (tqual == desiredScore):
                        if self.__calibrators['bestIndex'] is None:
                            self.__calibrators['bestIndex'] = i
                            calFd = tFd
                            calFound = True
                        elif (tFd >= (2 * calFd) and self.__calibrators['list'][i]['distance'] < 10):
                            # We will accept a calibrator further away, if it is much brighter.
                            self.__calibrators['bestIndex'] = i
                            calFd = tFd
            desiredScore -= 1
                                
        return self

    def getBestCalibrator(self, array=None):
        if self.__calibrators['bestIndex'] is None:
            self.selectBest(array)

        if self.__calibrators['bestIndex'] is not None:
            return self.getCalibrator(self.__calibrators['bestIndex'])

        return None

def __frequency2BandName(frequency=None):
    # Take a frequency in MHz and return the band it would be in.
    if frequency is not None:
        if frequency < 3100:
            return "16cm"
        if frequency < 12000:
            return "4cm"
        if frequency < 27000:
            return "15mm"
        if frequency < 52000:
            return "7mm"
        if frequency < 106000:
            return "3mm"
        return None

def _calibratorSearchResponse__frequency2BandName(frequency=None):
    return __frequency2BandName(frequency)
    
def __model2FluxDensity(model=None, frequency=None):
    # Convert an array of model parameters into a flux density.
    # The frequency should be given in MHz.
    if model is not None and frequency is not None:
        logS = float(model[0])
        logF = np.log10(float(frequency) / 1000)
        for i in range(1, len(model) - 1):
            logS += float(model[i]) * logF**i
        return 10**logS

def _calibrator__model2FluxDensity(model=None, frequency=None):
    return __model2FluxDensity(model, frequency)    
    
def __getValue(xmlNode=None, tagName=None):
    if (xmlNode is not None and tagName is not None):
        return xmlNode.getElementsByTagName(tagName)[0].childNodes[0].data

def __communications(data=None, parseType=None):
    serverName = "www.narrabri.atnf.csiro.au"
    serverProtocol = "https://"
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
    for i in range(0, len(frequencies)):
        frequencies[i] = str(frequencies[i])
        
    data = { 'mode': "cals" }
    if (ra is not None and dec is not None and radius is not None):
        data['radec'] = ra + "," + dec
        data['theta'] = radius
        data['frequencies'] = ",".join(frequencies)
        data['flimit'] = fluxLimit
        
    xmlresponse = __communications(data, "xml")
    sourceList = xmlresponse.getElementsByTagName('source')
    calList = calibratorSearchResponse()
    for i in range(0, len(sourceList)):
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
