# A schedule is a collection of scans, so the schedule class
# doesn't do much. But we do keep track of certain constants.
from scan import scan

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
    
    def __init__(self):
        # This is the list of scans, in order.
        self.scans = []
        return None

    def clear(self):
        # Clear the schedule.
        self.scans = []
        return self
    
    def addScan(self, options={}):
        # Add a scan to the schedule.
        scan_new = scan()

        # By default, we copy the details from the previous scan.
        if (not ('nocopy' in options and options['nocopy'] == True)) and (len(self.scans) > 0):
            scan_old = self.scans[-1]
            for f in self.__scanHandlers:
                getattr(scan_new, self.__scanHandlers[f]['set'])(getattr(scan_old, self.__scanHandlers[f]['get'])())
        
        # Check for options for the scan.
        for f in self.__scanHandlers:
            if self.__scanHandlers[f]['option'] in options:
                getattr(scan_new, self.__scanHandlers[f]['set'])(options[self.__scanHandlers[f]['option']])
            
        # Add the scan to the list.
        self.scans.append(scan_new)
            
        return scan_new

    def deleteScan(self, idx=None):
        # Delete a scan from the schedule, using the Python del indexing standard.
        if idx is not None:
            del self.scans[idx]

    def getScan(self, idx=None):
        # Return the scan specified.
        if idx is not None:
            return self.scans[idx]
            
    def __outputScheduleLine(self, s, n, fn, fm):
        # Generic checker for line output to schedule.
        if (n == 0) or (getattr(self.scans[n], fn)() !=
                        getattr(self.scans[n - 1], fn)()):
            s.write(fm % getattr(self.scans[n], fn)())

            
    def write(self, name=None):
        # Write out the schedule to disk.
        if name is not None:
            with open(name, 'w') as schedFile:
                for i in xrange(0, len(self.scans)):
                    schedFile.write("$SCAN*V5\n")
                    for h in self.__scanHandlers:
                        outf = h + "="
                        if self.__scanHandlers[h]['format'] == "string":
                            outf += "%s"
                        elif self.__scanHandlers[h]['format'] == "float":
                            outf += "%.3f"
                        outf += "\n"
                        self.__outputScheduleLine(schedFile, i, self.__scanHandlers[h]['get'], outf)

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
                        
