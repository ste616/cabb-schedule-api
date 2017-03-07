# A schedule is a collection of scans, so the schedule class
# doesn't do much. But we do keep track of certain constants.
from scan import scan
import re

class schedule:
    # A list of all the fields we need to know about.
    __scanHandlers = {
        'Source': { 'format': "string", 'get': "getSource", 'set': "setSource", 'option': "source" },

        'RA': { 'format': "string", 'get': "getRightAscension", 'set': "setRightAscension",
                'option': "rightAscension" },

        'Dec': { 'format': "string", 'get': "getDeclination", 'set': "setDeclination",
                 'option': "declination" },

        'Epoch': { 'format': "string", 'get': "getEpoch", 'set': "setEpoch", 'option': "epoch" },

        'CalCode': { 'format': "string", 'get': "getCalCode", 'set': 'setCalCode', 'option': "calCode" },

        'ScanLength': { 'format': "string", 'get': "getScanLength", 'set': "setScanLength",
                        'option': "scanLength" },

        'ScanType': { 'format': "string", 'get': "getScanType", 'set': "setScanType",
                      'option': "scanType" },

        'Pointing': { 'format': "string", 'get': "getPointing", 'set': "setPointing",
                      'option': "pointing" },

        'Observer': { 'format': "string", 'get': "getObserver", 'set': "setObserver",
                      'option': "observer" },

        'Project': { 'format': "string", 'get': "getProject", 'set': "setProject",
                     'option': "project" },

        'Time': { 'format': "string", 'get': "getTime", 'set': "setTime", 'option': "time" },

        'TimeCode': { 'format': "string", 'get': "getTimeCode", 'set': "setTimeCode",
                      'option': "timeCode" },

        'Date': { 'format': "string", 'get': "getDate", 'set': "setDate", 'option': "date" },

        'Averaging': { 'format': "string", 'get': "getAveraging", 'set': "setAveraging",
                       'option': "averaging" },

        'Environment': { 'format': "string", 'get': "getEnvironment", 'set': "setEnvironment",
                         'option': "environment" },

        'PointingOffset1': { 'format': "float", 'get': "getPointingOffset1", 'set': "setPointingOffset1",
                             'option': "pointingOffset1" },

        'PointingOffset2': { 'format': "float", 'get': "getPointingOffset2", 'set': "setPointingOffset2",
                             'option': "pointingOffset2" },

        'TVChan': { 'format': "string", 'get': "getTvChannels", 'set': "setTvChannels",
                    'option': "tvChannels" },

        'Cmd': { 'format': "string", 'get': "getCommand", 'set': "setCommand", 'option': "command" },

        'CatVel': { 'format': "string", 'get': "getCatVel", 'set': "setCatVel", 'option': "catVel" },

        'FreqConfig': { 'format': "string", 'get': "getFreqConfig", 'set': "setFreqConfig",
                        'option': "freqConfig" },

        'Comment': { 'format': "string", 'get': "getComment", 'set': "setComment", 'option': "comment" },

        'Wrap': { 'format': "string", 'get': "getWrap", 'set': "setWrap", 'option': "wrap" }
    }

    __freqHandlers = {
        'Freq-1': { 'format': "integer", 'get': "getFreq", 'set': "setFreq", 'object': "IF1", 'option': "freq1" },
        'Freq-2': { 'format': "integer", 'get': "getFreq", 'set': "setFreq", 'object': "IF2", 'option': "freq2" }
    }
    
    def __init__(self):
        # This is the list of scans, in order.
        self.scans = []
        self.looping = True
        self.calibratorAssociations = {}
        return None

    def clear(self):
        # Clear the schedule.
        self.scans = []
        self.calibratorAssociations = {}
        return self

    def setLooping(self, looping=None):
        # This flag lets the library know whether the schedule will be looping in caobs.
        # This will change the way the library writes out the schedule, to make sure a
        # calibrator is observed at the end.
        if looping is not None and (looping == True or looping == False):
            self.looping = looping
        return self

    def getLooping(self):
        return self.looping

    def __prepareValue(self, value, vtype):
        if vtype == "integer":
            return int(value)
        elif vtype == "float":
            return float(value)
        return value
    
    def addScan(self, options={}):
        # Add a scan to the schedule.
        scan_new = scan()
        
        # By default, we copy the details from the previous scan.
        if (not ('nocopy' in options and options['nocopy'] == True)) and (len(self.scans) > 0):
            scan_old = self.scans[-1]
            for f in self.__scanHandlers:
                # We don't copy the CalCode.
                if (f != "CalCode"):
                    getattr(scan_new, self.__scanHandlers[f]['set'])(getattr(scan_old, self.__scanHandlers[f]['get'])())
            for f in self.__freqHandlers:
                getattr(getattr(scan_new, self.__freqHandlers[f]['object'])(), self.__freqHandlers[f]['set'])(
                    getattr(getattr(scan_old, self.__freqHandlers[f]['object'])(), self.__freqHandlers[f]['get'])())
        
        # Check for options for the scan.
        for f in self.__scanHandlers:
            if self.__scanHandlers[f]['option'] in options:
                val = self.__prepareValue(options[self.__scanHandlers[f]['option']], self.__scanHandlers[f]['format'])
                getattr(scan_new, self.__scanHandlers[f]['set'])(val)

        for f in self.__freqHandlers:
            if self.__freqHandlers[f]['option'] in options:
                val = self.__prepareValue(options[self.__freqHandlers[f]['option']], self.__freqHandlers[f]['format'])
                getattr(getattr(scan_new, self.__freqHandlers[f]['object'])(), self.__freqHandlers[f]['set'])(val)
                
        # Add the scan to the list.
        if ('insertIndex' in options and options['insertIndex'] >= 0):
            # We have been asked to insert the scan at a particular position.
            # Check if the insertIndex is too large.
            if (options['insertIndex'] >= len(self.scans)):
                self.scans.append(scan_new)
            else:
                self.scans.insert(options['insertIndex'], scan_new)
        else:
            self.scans.append(scan_new)
            
        return scan_new

    def addCalibrator(self, calibrator=None, refScan=None, options={}):
        # Add a calibrator database calibrator to the schedule.
        if calibrator is None or refScan is None:
            return None

        # We attach the calibrator to the source scans that match the details
        # passed in as the refScan. So we first find which scans match.
        # We match only on source name, position and frequency configuration.
        matchedScans = []
        for i in xrange(0, len(self.scans)):
            if (self.scans[i].getSource() == refScan.getSource() and
                self.scans[i].getRightAscension() == refScan.getRightAscension() and
                self.scans[i].getDeclination() == refScan.getDeclination() and
                self.scans[i].IF1().getFreq() == refScan.IF1().getFreq() and
                self.scans[i].IF2().getFreq() == refScan.IF2().getFreq()):
                matchedScans.append(i)
                # Ensure the ID of each of the matched scans is the same.
                self.scans[i].setId(refScan.getId())

        # Craft the calibrator scan.
        noptions = options
        noptions['source'] = calibrator.getName()
        noptions['rightAscension'] = calibrator.getRightAscension()
        noptions['declination'] = calibrator.getDeclination()
        noptions['freq1'] = refScan.IF1().getFreq()
        noptions['freq2'] = refScan.IF2().getFreq()
        noptions['calCode'] = "C"

        # We place the calibrator scan before each of the matched scans.
        for i in xrange(0, len(matchedScans)):
            # Remember, the index of the matched scan will go up by one every time
            # we put a new scan in before it.
            ni = i + matchedScans[i]
            noptions['insertIndex'] = ni
            nscan = self.addScan(noptions)
            if i == 0:
                # Associate the calibrator to the scan.
                self.calibratorAssociations[refScan.getId()] = nscan.getId()
            else:
                # Put the same ID on all the calibrators.
                nscan.setId(self.calibratorAssociations[refScan.getId()])
        return None
    
    def deleteScan(self, idx=None):
        # Delete a scan from the schedule, using the Python del indexing standard.
        if idx is not None:
            del self.scans[idx]

    def getScan(self, idx=None):
        # Return the scan specified.
        if idx is not None:
            return self.scans[idx]

    def __outputScheduleLine(self, s, o, p, fn, fm):
        # Generic checker for line output to schedule.
        if (p is None) or (getattr(o, fn)() !=
                           getattr(p, fn)()):
            s.write(fm % getattr(o, fn)())

    def __formatSpecifier(self, fmt):
        if fmt == "string":
            return "%s"
        elif fmt == "float":
            return "%.3f"
        elif fmt == "integer":
            return "%d"
        else:
            return "%s"
            
    def write(self, name=None):
        # Write out the schedule to disk.
        if name is not None:
            with open(name, 'w') as schedFile:
                for i in xrange(0, len(self.scans)):
                    schedFile.write("$SCAN*V5\n")
                    for h in self.__scanHandlers:
                        outf = h + "=" + self.__formatSpecifier(self.__scanHandlers[h]['format']) + "\n"
                        prevScan = None
                        if i > 0:
                            prevScan = self.scans[i - 1]
                        self.__outputScheduleLine(schedFile, self.scans[i], prevScan,
                                                  self.__scanHandlers[h]['get'], outf)
                    for h in self.__freqHandlers:
                        outf = h + "=" + self.__formatSpecifier(self.__freqHandlers[h]['format']) + "\n"
                        prevScan = None
                        if i > 0:
                            prevScan = getattr(self.scans[i - 1], self.__freqHandlers[h]['object'])()
                        self.__outputScheduleLine(schedFile,
                                                  getattr(self.scans[i], self.__freqHandlers[h]['object'])(),
                                                  prevScan, self.__freqHandlers[h]['get'], outf)
                    schedFile.write("$SCANEND\n")
        return self

    def read(self, name=None):
        # Read in a schedule file.
        scanDetails = {}
        if name is not None:
            with open(name, 'r') as schedFile:
                # Reset our current scans.
                self.clear()
                for line in schedFile:
                    line = line.strip()
                    if line == "$SCAN*V5":
                        # A new scan.
                        scanDetails = {}
                    elif line == "$SCANEND":
                        # Make the new scan.
                        self.addScan(scanDetails)
                    else:
                        # Add to the scan options object.
                        els = line.split("=")
                        if els[0] in self.__scanHandlers:
                            scanDetails[self.__scanHandlers[els[0]]['option']] = els[1]
                        elif els[0] in self.__freqHandlers:
                            scanDetails[self.__freqHandlers[els[0]]['option']] = els[1]
