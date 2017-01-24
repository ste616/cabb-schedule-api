# A scan has several required fields.
from frequency_setup import frequency_setup

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

    def setSource(self, source_name=None):
        if source_name is not None:
            self.__scanDetails['source'] = source_name
        return self

    def setRightAscension(self, ra=None):
        if ra is not None:
            self.__scanDetails['rightAscension'] = ra
        return self
