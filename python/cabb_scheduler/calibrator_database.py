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

    def setName(self, name=None):
        if name is not None:
            self.__calibratorDetails['name'] = name
        return self

    def setRightAscension(self, ra=None):
        if ra is not None:
            self.__calibratorDetails['rightAscension'] = ra
        return self

    def setDeclination(self, dec=None):
        if dec is not None:
            self.__calibratorDetails['declination'] = dec
        return self

class calibratorSearchResponse:
    def __init__(self):
        # A list of sources returned from a calibrator search.
        self.__calibratorList = []

    def addCalibrator(self, calibratorDetails=None, distance=None):
        # Create a new calibrator.
        if (calibratorDetails is not None and distance is not None):
            nc = calibrator(calibratorDetails)
            self.__calibratorList.append({ 'calibrator': nc, 'distance': distance })
            return nc
        else:
            return None
        
# A routine to search for a calibrator, given an RA and Dec and a search radius.
def coneSearch(ra=None, dec=None, radius=None, fluxLimit=None, frequencies=None):
    # Form the request to the calibrator database server.
    session = Session()

    if fluxLimit is None:
        fluxLimit = 0.2
    
    serverName = "www.narrabri.atnf.csiro.au"
    serverProtocol = "http://"
    serverScript = "/cgi-bin/Calibrators/new/caldb_v3.pl"

    data = { 'mode': "cals" }
    if (ra is not None and dec is not None and radius is not None):
        data['radec'] = ra + "," + dec
        data['theta'] = radius
        data['frequencies'] = "5500,8000"
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
        sourceName = sourceList[i].getElementsByTagName('name')[0].childNodes[0].data
        distance = sourceList[i].getElementsByTagName('distance')[0].childNodes[0].data
        print sourceName + " (" + distance + ")"
    
