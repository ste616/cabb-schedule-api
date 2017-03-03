# A library to handle dealing with v3 of the ATCA calibrator database.
from requests import Session
from xml.dom import minidom
import errors

class calibrator:
    def __init__(self, details=None):
        # This is a single calibrator from the database.
        self.__calibratorDetails = {
            'name': "",
            'rightAscension': "",
            'declination': "",
            'fluxDensities': []
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
                if (self.__calibratorDetails['fluxDensities'][i]['frequency'] == frequency):
                    self.__calibratorDetails['fluxDensities'][i]['fluxDensity'] = fluxDensity
                    foundFrequency = True
            if foundFrequency == False:
                self.__calibratorDetails['fluxDensities'].append({ 'frequency': int(frequency),
                                                                   'fluxDensity': float(fluxDensity) })
        return self

    def getFluxDensities(self, frequency=None):
        if frequency is not None:
            for i in xrange(0, len(self.__calibratorDetails['fluxDensities'])):
                if (self.__calibratorDetails['fluxDensities'][i]['frequency'] == frequency):
                    return [ self.__calibratorDetails['fluxDensities'][i] ]
            return None
        return self.__calibratorDetails['fluxDensities']
    
class calibratorSearchResponse:
    def __init__(self):
        # A list of sources returned from a calibrator search.
        self.__calibratorList = []

    def addCalibrator(self, calibratorDetails=None, distance=None):
        # Create a new calibrator.
        if (calibratorDetails is not None and distance is not None):
            nc = calibrator(calibratorDetails)
            self.__calibratorList.append({ 'calibrator': nc, 'distance': float(distance) })
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
        
def __getValue(xmlNode=None, tagName=None):
    if (xmlNode is not None and tagName is not None):
        return xmlNode.getElementsByTagName(tagName)[0].childNodes[0].data
        
# A routine to search for a calibrator, given an RA and Dec and a search radius.
def coneSearch(ra=None, dec=None, radius=None, fluxLimit=None, frequencies=None):
    # Form the request to the calibrator database server.
    session = Session()

    if fluxLimit is None:
        fluxLimit = 0.2
    if frequencies is None:
        frequencies = [ 5500, 9000 ]
    for i in xrange(0, len(frequencies)):
        frequencies[i] = str(frequencies[i])
        
    serverName = "www.narrabri.atnf.csiro.au"
    serverProtocol = "http://"
    serverScript = "/cgi-bin/Calibrators/new/caldb_v3.pl"

    data = { 'mode': "cals" }
    if (ra is not None and dec is not None and radius is not None):
        data['radec'] = ra + "," + dec
        data['theta'] = radius
        data['frequencies'] = ",".join(frequencies)
        data['flimit'] = fluxLimit
    print data
        
    response = session.post(
        url=serverProtocol + serverName + serverScript,
        data=data
    )

    #print response.text
    xmlresponse = minidom.parseString(response.text)
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
