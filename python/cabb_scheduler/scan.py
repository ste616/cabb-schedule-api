# A scan has several required fields.
from frequency_setup import frequency_setup
import errors
import re

class scan:
    def __init__(self):
        # We put all the properties of the scan in a dictionary, and store
        # some necessary defaults.
        self.__scanDetails = { 'source': "",
                               'rightAscension': "00:00:00",
                               'declination': "00:00:00",
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

    def setPointing(self, pointing=None):
        if pointing is not None:
            if pointing == "Global" or pointing == "Offset" or pointing == "Offpnt" or pointing == "Refpnt" or pointing == "Update":
                self.__scanDetails['pointing'] = pointing
            else:
                raise errors.ScanError("Unrecognised Pointing specified.")
        return self

    def setObserver(self, observer=None):
        if observer is not None:
            self.__scanDetails['observer'] = observer
        return self

    def setProject(self, project=None):
        if project is not None:
            self.__scanDetails['project'] = project
        return self

    def setTime(self, intTime=None):
        if intTime is not None:
            self.__scanDetails['time'] = intTime
        return self

    def setTimeCode(self, timeCode=None):
        if timeCode is not None:
            if timeCode == "LST" or timeCode == "UTC":
                self.__scanDetails['timeCode'] = timeCode
            else:
                raise errors.ScanError("Unrecognised TimeCode specified.")
        return self

    def setDate(self, startDate=None):
        if startDate is not None:
            self.__scanDetails['startDate'] = startDate
        return self

    def setAveraging(self, averaging=None):
        if averaging is not None:
            if averaging > 0:
                self.__scanDetails['averaging'] = averaging
            else:
                raise errors.ScanError("Averaging must be a positive, non-zero number.")
        return self

    def setEnvironment(self, environment=None):
        if environment is not None:
            if environment >= 0 and environment < 128:
                self.__scanDetails['environment'] = environment
            else:
                raise errors.ScanError("Environment must be an integer between 0 and 127 inclusive.")
        return self

    def setPointingOffset1(self, offset=None):
        if offset is not None:
            self.__scanDetails['pointingOffset1'] = offset
        return self

    def setPointingOffset2(self, offset=None):
        if offset is not None:
            self.__scanDetails['pointingOffset2'] = offset
        return self

    def setTvChannels(self, tvchan=None):
        if tvchan is not None:
            r = re.compile('^\d+\,\d+\,\d+\,\d+$')
            if (r.match(tvchan) is not None) or (tvchan == 'default') or (tvchan == '') or (tvchan == 'null'):
                self.__scanDetails['tvChannels'] = tvchan
            else:
                raise errors.ScanError("TV Channel specification is incorrect.")
        return self

    def setCommand(self, cmd=None):
        if cmd is not None:
            self.__scanDetails['command'] = cmd
        return self

    def setCatVel(self, vel=None):
        if vel is not None:
            self.__scanDetails['catVel'] = vel
        return self

    def setFreqConfig(self, config=None):
        if config is not None:
            r1 = re.compile('^Master\d+$')
            r2 = re.compile('^Slave-\d+$')
            if (r1.match(config) is not None) or (r2.match(config) is not None) or (config == "null"):
                self.__scanDetails['freqConfig'] = config
            else:
                raise errors.ScanError("Frequency configuration is incorrectly specified.")
        return self

    def setComment(self, comment=None):
        if comment is not None:
            self.__scanDetails['comment'] = comment
        return self

    def setWrap(self, wrap=None):
        if wrap is not None:
            if (wrap == "North") or (wrap == "South") or (wrap == "Closest"):
                self.__scanDetails['wrap'] = wrap
            else:
                raise errors.ScanError("Wrap is incorrectly specified.")
        return self

    
