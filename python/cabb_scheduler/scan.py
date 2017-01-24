# A scan has several required fields.
from frequency_setup import frequency_setup
import errors

class scan:
    def __init__(self):
        # We put all the properties of the scan in a dictionary.
        self.__scanDetails = { 'source': "",
                               'rightAscension': "",
                               'declination': "",
                               'epoch': "J2000",
                               'calCode': "",
                               'scanLength': "00:10:00",
                               'scanType': "Normal",
                               'pointing': "Global",
                               'observer': "",
                               'project': "C999",
                               'time': "00:00:00",
                               'timeCode': "LST",
                               'date': "24/01/2017",
                               'config': "null",
                               'averaging': 1,
                               'environment': 0,
                               'pointingOffset1': 0,
                               'pointingOffset2': 0,
                               'tvChannels': "null",
                               'command': "",
                               'catVel': "",
                               'freqConfig': "null",
                               'comment': "",
                               'wrap': "Closest",
                               'setupF1': frequency_setup(),
                               'setupF2': frequency_setup() }

    def getSource(self):
        return self.__scanDetails['source']

    def getRightAscension(self):
        return self.__scanDetails['rightAscension']

    def getDeclination(self):
        return self.__scanDetails['declination']

    def getEpoch(self):
        return self.__scanDetails['epoch']

    def getCalCode(self):
        return self.__scanDetails['calCode']
    
    def getScanLength(self):
        return self.__scanDetails['scanLength']

    def getScanType(self):
        return self.__scanDetails['scanType']

    def getPointing(self):
        return self.__scanDetails['pointing']

    def getObserver(self):
        return self.__scanDetails['observer']

    def getProject(self):
        return self.__scanDetails['project']

    def getTime(self):
        return self.__scanDetails['time']

    def getTimeCode(self):
        return self.__scanDetails['timeCode']

    def getDate(self):
        return self.__scanDetails['date']

    # We skip the config getter, it is not useful.

    def getAveraging(self):
        return self.__scanDetails['averaging']

    def getEnvironment(self):
        return self.__scanDetails['environment']

    def getPointingOffset1(self):
        return self.__scanDetails['pointingOffset1']

    def getPointingOffset2(self):
        return self.__scanDetails['pointingOffset2']

    def getTvChannels(self):
        return self.__scanDetails['tvChannels']

    def getCommand(self):
        return self.__scanDetails['command']

    def getCatVel(self):
        return self.__scanDetails['catVel']

    def getFreqConfig(self):
        return self.__scanDetails['freqConfig']

    def getComment(self):
        return self.__scanDetails['comment']

    def getWrap(self):
        return self.__scanDetails['wrap']

    def IF1(self):
        return self.__scanDetails['setupF1']

    def IF2(self):
        return self.__scanDetails['setupF2']
    
    def setSource(self, source_name=None):
        if source_name is not None:
            # Check for maximum length.
            if len(source_name) <= 10:
                self.__scanDetails['source'] = source_name
            else:
                raise errors.ScanError("Specified source name is too long.")
        return self

    def setRightAscension(self, ra=None):
        if ra is not None:
            self.__scanDetails['rightAscension'] = ra
        return self

    def setDeclination(self, dec=None):
        if dec is not None:
            self.__scanDetails['declination'] = dec
        return self

    def setEpoch(self, epoch=None):
        if epoch is not None:
            if epoch == "J2000" or epoch == "B1950" or epoch == "AzEl" or epoch == "Galactic":
                self.__scanDetails['epoch'] = epoch
            else:
                raise errors.ScanError("Unrecognised epoch specified.")
        return self
        
    def setCalCode(self, calCode=None):
        if calCode is not None:
            if calCode == "" or calCode == "C" or calCode == "B":
                self.__scanDetails['calCode'] = calCode
            else:
                raise errors.ScanError("Unrecognised CalCode specified.")
        return self

    def setScanLength(self, scanLength=None):
        if scanLength is not None:
            self.__scanDetails['scanLength'] = scanLength
        return self

    def setScanType(self, scanType=None):
        if scanType is not None:
            if scanType == "Normal" or scanType == "Dwell" or scanType == "Mosaic" or scanType == "Point" or scanType == "Paddle" or scanType == "OTFMos":
                self.__scanDetails['scanType'] = scanType
            else:
                raise errors.ScanError("Unrecognised ScanType specified.")
        return self

    
