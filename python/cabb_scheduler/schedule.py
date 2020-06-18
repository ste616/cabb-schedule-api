# A schedule is a collection of scans, so the schedule class
# doesn't do much. But we do keep track of certain constants.
from cabb_scheduler.scan import scan
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

        'Environment': { 'format': "integer", 'get': "getEnvironment", 'set': "setEnvironment",
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
        self.autoCals = True
        self.calFirst = True
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

    def getNumberOfScans(self):
        return len(self.scans)

    def getObservedBands(self):
        # Work out which bands will be observed by this schedule.
        observedBands = []
        for i in range(0, len(self.scans)):
            tband = self.scans[i].IF1().getFrequencyBand()
            if tband not in observedBands:
                observedBands.append(tband)
        return observedBands
    
    def enableAutoCalibrators(self):
        # Enable the calibrator scan checking function.
        self.autoCals = True
        return self

    def disableAutoCalibrators(self):
        # Disable the calibrator scan checking function.
        self.autoCals = False
        return self

    def enablePriorCalibration(self):
        # Ensure a calibrator is placed before the first source instance
        # in the schedule.
        self.calFirst = True
        return self

    def disablePriorCalibration(self):
        # Don't automatically put a calibrator before the first source
        # instance in the schedule.
        self.calFirst = False
        return self
    
    def autoCalibrators(self):
        # Return the state of the auto calibration mode.
        return self.autoCals
    
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

        # We do zooms differently.
        for f in range(1, 3):
            freqObject = "IF%d" % f
            for z in range(1, 17):
                option = "zoom%d-%d" % (z, f)
                if (option in options):
                    val = self.__prepareValue(options[option], "integer")
                    getattr(getattr(scan_new, freqObject)(), "setZoomChannel")(z, val)
                
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
        for i in range(0, len(self.scans)):
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
        toptions = refScan.IF1().getAllZooms()
        for z in toptions:
            noptions[z + '-1'] = toptions[z]
        toptions = refScan.IF2().getAllZooms()
        for z in toptions:
            noptions[z + '-2'] = toptions[z]
        noptions['calCode'] = "C"

        # We place the calibrator scan before each of the matched scans.
        # Or afterwards if we don't want to get to the calibrator first.
        nscan = None
        for i in range(0, len(matchedScans)):
            # Remember, the index of the matched scan will go up by one every time
            # we put a new scan in before it.
            ni = i + matchedScans[i]
            noptions['insertIndex'] = ni
            if self.calFirst == False:
                noptions['insertIndex'] = ni + 1
            nscan = self.addScan(noptions)
            if i == 0:
                # Associate the calibrator to the scan.
                self.calibratorAssociations[refScan.getId()] = nscan.getId()
            else:
                # Put the same ID on all the calibrators.
                nscan.setId(self.calibratorAssociations[refScan.getId()])
        return nscan
    
    def deleteScan(self, idx=None):
        # Delete a scan from the schedule, using the Python del indexing standard.
        if idx is not None:
            del self.scans[idx]

    def getScan(self, idx=None):
        # Return the scan specified.
        if idx is not None:
            return self.scans[idx]

    def getScanById(self, id=None):
        # Return the scan specified.
        if id is not None:
            for i in range(0, len(self.scans)):
                if self.scans[i].getId() == id:
                    return self.scans[i]
        return None

    def scanToOptions(self, scan=None):
        # Turn a scan into an options object.
        oopts = {}
        if scan is not None:
            for f in self.__scanHandlers:
                oopts[self.__scanHandlers[f]['option']] = getattr(scan, self.__scanHandlers[f]['get'])()
            for f in self.__freqHandlers:
                oopts[self.__freqHandlers[f]['option']] = getattr(getattr(scan, self.__freqHandlers[f]['object'])(), self.__freqHandlers[f]['get'])()
            for f in range(1, 3):
                freqObject = "IF%d" % f
                for z in range(1, 17):
                    option = "zoom%d-%d" % (z, f)
                    oopts[option] = getattr(getattr(scan, freqObject)(), "getZoomChannel")(z)
        return oopts
    
    def copyScans(self, ids=[], pos=None, calCheck=True):
        # Copy the scans specified by their IDs and put the copies beginning at
        # the nominated position (or at the end by default).
        if len(ids) == 0:
            return None
        # Try to find the scans.
        j = 0
        for i in range(0, len(ids)):
            cscan = self.getScanById(ids[i])
            if cscan is not None:
                copts = self.scanToOptions(cscan)
                copts['nocopy'] = True
                if pos is not None and pos >= 0 and pos < len(self.scans):
                    copts['insertIndex'] = pos + j
                nscan = self.addScan(copts)
                # Set its ID.
                nscan.setId(cscan.getId())
                # We do this because j only increments when a scan is found.
                j += 1
        if calCheck == True:
            # Now run the calibrator assignment checks.
            self.checkCalibrators()

    def checkCalibrators(self):
        # Check that a calibrator scan is assigned to each of the associated
        # sources, and add a scan if it isn't.
        if self.autoCals == False:
            # The user doesn't want us to do this.
            return
        i = 0
        while (i < len(self.scans)):
            # We loop like this because the length of the array may change as
            # we go through.
            tId = self.scans[i].getId()
            # Check if this is a source with an associated calibrator.
            if tId in self.calibratorAssociations:
                # It is. Check if there is a calibrator scan before it.
                if self.calFirst == True:
                    if i == 0:
                        # Nope, first scan, we add a calibrator scan.
                        self.copyScans([ self.calibratorAssociations[tId] ], 0, False)
                    else:
                        pId = self.scans[i - 1].getId()
                        if pId != self.calibratorAssociations[tId]:
                            # Nope, the scan before this one is not the calibrator.
                            self.copyScans([ self.calibratorAssociations[tId] ], i, False)
                    # Otherwise it is the calibrator scan.
                # Check if there needs to be a calibrator scan after it.
                if i == (len(self.scans) - 1):
                    # We're at the end of the list.
                    if self.looping == False or self.calFirst == False:
                        # We do need a cal scan at the end, because it won't go around, or when
                        # it does there won't be a calibrator there.
                        self.copyScans([ self.calibratorAssociations[tId] ], (i + 1), False)
                    else:
                        # Check that the first scan is a calibrator scan.
                        pId = self.scans[0].getId()
                        if pId != self.calibratorAssociations[tId]:
                            # The first scan is not a calibrator scan, so we add one here.
                            self.copyScans([ self.calibratorAssociations[tId] ], (i + 1), False)
                        # Otherwise, it will loop back around to the calibrator.
                else:
                    # Check the ID of the next scan.
                    nId = self.scans[i + 1].getId()
                    if nId != self.calibratorAssociations[tId] and nId != tId:
                        # There is another scan after us, but it isn't the same as us, and
                        # it isn't our calibrator. We add a cal scan.
                        self.copyScans([ self.calibratorAssociations[tId] ], (i + 1), False)
            i += 1
        return

    def completeSchedule(self):
        # Go through the schedule and make the schedule "work".
        # First, we work out if the schedule wants more than one band.
        observedBands = self.getObservedBands()
        # Check 1: add focus scans when the frequency configuration changes.
        # We will only need to do focus scans if we change to or from 4cm.
        if len(observedBands) > 1 and "4cm" in observedBands:
            # Find the transition points.
            i = 1
            while i < len(self.scans):
                print("[completeSchedule] schedule now has %d scans" % len(self.scans))
                tband = self.scans[i - 1].IF1().getFrequencyBand()
                nband = self.scans[i].IF1().getFrequencyBand()
                if tband != nband and (tband == "4cm" or nband == "4cm"):
                    print("[completeSchedule] found band change between %d and %d" % ((i - 1), i))
                    # Check first to see if a focus command is already present.
                    ncmd = self.scans[i].getCommand()
                    print("[completeSchedule] command in current scan [%s]" % ncmd)
                    if "foc" not in ncmd:
                        # Add a focus scan after this scan.
                        nscanId = self.scans[i].getId()
                        print("[completeSchedule] copying scan %d" % i)
                        self.copyScans(ids=[nscanId], pos=i, calCheck=False)
                        # Change the name of this scan and add a focus command.
                        self.scans[i].setSource("focus")
                        self.scans[i].setCommand("focus default")
                        # Change it to be 90 seconds long and a Normal type.
                        self.scans[i].setScanType("Normal")
                        self.scans[i].setScanLength("00:01:30")
                        self.scans[i].setComment("bandchange")
                i += 1
        # If we're looping, we may need to add a focus scan at the start as well.
        if self.looping:
            tband = self.scans[0].IF1().getFrequencyBand()
            nband = self.scans[len(self.scans) - 1].IF1().getFrequencyBand()
            if tband != nband and (tband == "4cm" or nband == "4cm"):
                nscanId = self.scans[0].getId()
                self.copyScans(ids=[nscanId], pos=0, calCheck=False)
                self.scans[0].setSource("focus")
                self.scans[0].setCommand("focus default")
                self.scans[0].setScanType("Normal")
                self.scans[0].setScanLength("00:01:30")
    
    def __outputScheduleLine(self, s, o, p, fn, fm):
        # Generic checker for line output to schedule.
        if (p is None) or (getattr(o, fn)() !=
                           getattr(p, fn)()):
            s.write(fm % getattr(o, fn)())

    def __prepareScheduleLine(self, thisScan, previousScan, scanHandler, outFormat, garg=None):
        # We decide whether we need to make a string for this.
        if (((garg is not None) and ((previousScan is None) or (getattr(thisScan, scanHandler)(garg) !=
                                                               getattr(previousScan, scanHandler)(garg)))) or
            ((garg is None) and ((previousScan is None) or (getattr(thisScan, scanHandler)() !=
                                                            getattr(previousScan, scanHandler)())))):
            # We do want to output this line.
            if (garg is not None):
                outString = outFormat % getattr(thisScan, scanHandler)(garg)
            else:
                outString = outFormat % getattr(thisScan, scanHandler)()
            return outString
        # Otherwise we don't need this line.
        return None
            
    def __formatSpecifier(self, fmt):
        if fmt == "string":
            return "%s"
        elif fmt == "float":
            return "%.3f"
        elif fmt == "integer":
            return "%d"
        else:
            return "%s"

    def toString(self):
        # Make the schedule into a string.
        # Check we have all our calibrator scans.
        self.checkCalibrators()
        outputStrings = []
        for i in range(0, len(self.scans)):
            # Every scan starts the same way.
            outputStrings.append("$SCAN*V5")
            for h in self.__scanHandlers:
                outf = h + "=" + self.__formatSpecifier(self.__scanHandlers[h]['format'])
                prevScan = None
                if i > 0:
                    prevScan = self.scans[i - 1]
                nString = self.__prepareScheduleLine(self.scans[i], prevScan,
                                                    self.__scanHandlers[h]['get'], outf)
                if nString is not None:
                    outputStrings.append(nString)
            for h in self.__freqHandlers:
                outf = h + "=" + self.__formatSpecifier(self.__freqHandlers[h]['format'])
                prevScan = None
                if i > 0:
                    prevScan = getattr(self.scans[i - 1], self.__freqHandlers[h]['object'])()
                nString = self.__prepareScheduleLine(getattr(self.scans[i], self.__freqHandlers[h]['object'])(),
                                                     prevScan, self.__freqHandlers[h]['get'], outf)
                if nString is not None:
                    outputStrings.append(nString)
            for f in range(1, 3):
                freqObject = "IF%d" % f
                for z in range(1, 17):
                    outf = "Zoom%d-%d=" % (z, f)
                    outf += self.__formatSpecifier("integer")
                    prevScan = None
                    if i > 0:
                        prevScan = getattr(self.scans[i - 1], freqObject)()
                    nString = self.__prepareScheduleLine(getattr(self.scans[i], freqObject)(),
                                                         prevScan, "getZoomChannel", outf, z)
                    if nString is not None:
                        outputStrings.append(nString)
            # And every scan ends the same way.
            outputStrings.append("$SCANEND")
        # Make the output string by joining the elements with the newline character.
        return "\n".join(outputStrings) + "\n"
        
    def write(self, name=None):
        # Write out the schedule to disk.
        if name is not None:
            with open(name, 'w') as schedFile:
                schedFile.write(self.toString())
        return self

    def parse(self, string=None):
        # Take a schedule represented in string form (with \n as the line
        # separator) and return the scans.
        scanDetails = {}
        if string is not None:
            # Reset our current scans.
            self.clear()
            stringLines = [ s.strip() for s in string.splitlines() ]
            if len(stringLines) > 0:
                for i in range(0, len(stringLines)):
                    line = stringLines[i]
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
        return self.getNumberOfScans()
                    
    
    def read(self, name=None):
        # Read in a schedule file.
        if name is not None:
            with open(name, 'r') as schedFile:
                self.parse(schedFile.read())
        return self.getNumberOfScans()
