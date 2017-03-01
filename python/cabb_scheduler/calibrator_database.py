# A library to handle dealing with v3 of the ATCA calibrator database.
from requests import Session
from xml.dom import minidom
import errors

class calibrator:
    def __init__(self):
        # This is a single calibrator from the database.
        self.__calibratorDetails = {}

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
    for i in xrange(0, len(sourceList)):
        sourceName = sourceList[i].getElementsByTagName('name')[0].childNodes[0].data
        distance = sourceList[i].getElementsByTagName('distance')[0].childNodes[0].data
        print sourceName + " (" + distance + ")"
    
