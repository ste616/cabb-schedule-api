# A schedule is a collection of scans, so the schedule class
# doesn't do much. But we do keep track of certain constants.
from cabb_scheduler.scan import scan
import re
import math

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
        # Indicator of if the schedule is to be executed like 1/99 (True) or not.
        self.looping = True
        # Indicator of whether this library might need to check and determine
        # calibrator positions.
        self.autoCals = True
        # Indicator of if a calibrator needs to be observed before the first
        # observation of a source.
        self.calFirst = True
        # The dictionary of source/calibrator associations.
        self.calibratorAssociations = {}
        # Indicator of if we need to insert a preparatory scan before the first
        # scan.
        self.prepScans = False
        # Indicator of if we are to insert our automatic delay calibration
        # scans at the appropriate points.
        self.delayScans = False
        # The lowest frequency band nominated to use pointing scans.
        self.pointingLowBand = "7mm"
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

    def enablePrepScans(self):
        # Ensure any focus commands etc. are done at the start.
        self.prepScans = True
        return self

    def disablePrepScans(self):
        self.prepScans = False
        return self

    def enableDelayCal(self):
        # Insert automatic delay calibration scans before each
        # frequency.
        self.delayScans = True
        return self

    def disableDelayCal(self):
        self.delayScans = False
        return self

    def setPointingLowBand(self, band=None):
        if band is not None and (band == "16cm" or band == "4cm" or
                                 band == "15mm" or band == "7mm" or band == "3mm"):
            self.pointingLowBand = band
        return self

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
    
    def copyScans(self, ids=[], pos=None, calCheck=True, keepId=True):
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
                if keepId:
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
        # Check 1: If we're looping, we may need to add a focus scan at the start.
        # But first, we don't need to do a prep focus scan if we're also doing delay calibration
        # scans.
        if self.prepScans and self.delayScans:
            self.prepScans = False
        
        if self.looping or self.prepScans:
            tband = self.scans[0].IF1().getFrequencyBand()
            nband = self.scans[len(self.scans) - 1].IF1().getFrequencyBand()
            if (tband != nband and (tband == "4cm" or nband == "4cm")) or self.prepScans:
                nscanId = self.scans[0].getId()
                self.copyScans(ids=[nscanId], pos=0, calCheck=False, keepId=False)
                self.scans[0].setSource("focus")
                self.scans[0].setCommand("focus default")
                self.scans[0].setScanType("Normal")
                self.scans[0].setScanLength("00:01:30")

        # Check 2: If we've been asked, we put automatic calibration scans before each
        # frequency's first instance.
        if self.delayScans:
            # We start by putting calibration scans in.
            insertCalScans = True
            i = 0
            while i < len(self.scans):
                # Do a check to see if scans should go here.
                if i > 0:
                    tband1 = self.scans[i].IF1().getFreq()
                    tband2 = self.scans[i].IF2().getFreq()
                    lband1 = self.scans[i - 1].IF1().getFreq()
                    lband2 = self.scans[i - 1].IF2().getFreq()
                    if tband1 != lband1 or tband2 != lband2:
                        insertCalScans = True
                if insertCalScans:
                    tscanId = self.scans[i].getId()
                    # Ideally, we'd check that this is a calibrator with sufficient flux
                    # density, but we will have to rely on the user to ensure this is
                    # the case.
                    # What we do depends on which CABB mode we are in.
                    cWidth = self.scans[i].IF1().getChannelWidth()
                    if cWidth == 1:
                        # We insert 4 scans to do the calibration.
                        # Scan 1.
                        self.copyScans(ids=[tscanId], pos=0, calCheck=False, keepId=False)
                        self.scans[0].setSource("delscan1")
                        self.scans[0].setScanType("Normal")
                        # We need 9 cycles, assuming 10s cycles for the 00:01:30.
                        self.scans[0].setScanLength("00:01:30")
                        self.scans[0].setCommand("foc def;set ref ca03;cor tvmed on on;cor tatts 20;wait 2;cor atts on")
                        # Scan 2.
                        self.copyScans(ids=[tscanId], pos=1, calCheck=False, keepId=False)
                        self.scans[1].setSource("delscan2")
                        self.scans[1].setScanType("Normal")
                        # We need 4 cycles.
                        self.scans[1].setScanLength("00:00:40")
                        self.scans[1].setCommand("cor atts off;wait 2;cor reset delays;cor delavg 1;cor tvch 1140 1220 1140 1220")
                        # Scan 3.
                        self.copyScans(ids=[tscanId], pos=2, calCheck=False, keepId=False)
                        self.scans[2].setSource("delscan3")
                        self.scans[2].setScanType("Dwell")
                        # We need 4 cycles, and need the antennas on source for the next scan.
                        self.scans[2].setScanLength("00:00:40")
                        self.scans[2].setCommand("cor fflag f1 def;cor fflag f2 def;cor fflag f1 birdies;cor fflag f2 birdies")
                        # Scan 4.
                        self.copyScans(ids=[tscanId], pos=3, calCheck=False, keepId=False)
                        self.scans[3].setSource("delscan4")
                        self.scans[3].setScanType("Dwell")
                        # We need 21 cycles.
                        self.scans[3].setScanLength("00:03:30")
                        self.scans[3].setCommand("wait 7;cor dcal;wait 11;cor tvch def;waot 12;cor delavg 64;wait 17;cor dcal")
                    elif cWidth == 64:
                        # We insert 4 scans to do the calibration.
                        # Scan 1.
                        self.copyScans(ids=[tscanId], pos=0, calCheck=False, keepId=False)
                        self.scans[0].setSource("delscan1")
                        self.scans[0].setScanType("Normal")
                        # We need 4 cycles, assuming 10s cycles for the 00:00:40.
                        self.scans[0].setScanLength("00:00:40")
                        self.scans[0].setCommand("foc def;set ref ca03;cor tvmed on on;cor tatts 20;wait 2;cor atts on")
                        # Scan 2.
                        self.copyScans(ids=[tscanId], pos=1, calCheck=False, keepId=False)
                        # We need to set up a width-1 zoom band in this scan which will be used for initial
                        # delay calibration. Using channel 56 normally works fine.
                        # But first we get rid of any zooms that are configured.
                        for j in range(1, 16):
                            self.scans[1].IF1().setZoomChannel(zoomnum=j, chan=0)
                            self.scans[1].IF2().setZoomChannel(zoomnum=j, chan=0)
                        self.scans[1].IF1().setZoomChannel(zoomnum=1, chan=56)
                        self.scans[1].IF2().setZoomChannel(zoomnum=1, chan=56)
                        self.scans[1].setSource("delscan2")
                        self.scans[1].setScanType("Dwell")
                        # We need 5 cycles, and need the antennas on source for the next scan.
                        self.scans[1].setScanLength("00:00:40")
                        self.scans[1].setCommand("cor atts off;wait 2;cor reset delays;cor delavg 1;")
                        # We want to now copy this scan with its zoom configuration for the next scans.
                        tscanId = self.scans[1].getId()
                        # Scan 3.
                        self.copyScans(ids=[tscanId], pos=2, calCheck=False, keepId=False)
                        self.scans[2].setSource("delscan3")
                        self.scans[2].setScanType("Dwell")
                        # We need 4 cycles, and need the antennas on source for the next scan.
                        self.scans[2].setScanLength("00:00:40")
                        self.scans[2].setCommand("cor fflag f1 def;cor fflag f2 def;cor fflag f1 birdies;cor fflag f2 birdies")
                        # Scan 4.
                        self.copyScans(ids=[tscanId], pos=3, calCheck=False, keepId=False)
                        self.scans[3].setSource("delscan4")
                        self.scans[3].setScanType("Dwell")
                        # We need 21 cycles.
                        self.scans[3].setScanLength("00:03:30")
                        self.scans[3].setCommand("wait 7;cor dcal;wait 11;cor tvch def;waot 12;cor delavg 64;wait 17;cor dcal")

        # Check 3: add pointing scans when required and change the pointing type for the
        # scans that need it.
        i = 0
        lastBand = None
        lastPointings = {}
        while i < len(self.scans):
            # Find a transition to a band that requires pointing corrections.
            currentBand = self.scans[i].IF1().getFrequencyBand()
            needsPointing = False
            bandNeedsPointing = False
            if self.needsPointing(band=currentBand):
                needsPointing = True
                bandNeedsPointing = True
            if needsPointing:
                # Check this scan isn't already a pointing scan.
                if self.scans[i].getScanType() == "Point":
                    needsPointing = False
            if needsPointing:
                # Check if we've recently had a pointing scan.
                pointingChecks = []
                for s in lastPointings:
                    pointCheck = False
                    # Check that this scan is within a certain distance of the pointing scan.
                    angDist = self.__angularDistance(scanOrig=lastPointings[s]["scan"],
                                                     scanDest=i)
                    if angDist > 20.0:
                        # Too far away.
                        pointCheck = True
                    # Check if it has been too long since that scan.
                    if lastPointings[s]["timeDelta"] > (70 * 60):
                        # Too long ago.
                        pointCheck = True
                    pointingChecks.append(pointCheck)
                if False in pointingChecks:
                    # At least one pointing should be usable for this scan.
                    needsPointing = False
            if needsPointing:
                # We add a pointing scan, if we are looking at a calibrator.
                if self.scans[i].getCalCode() == "C":
                    # This is a calibrator, but we check that its associated
                    # source is next in the schedule.
                    if i < (len(self.scans) - 1):
                        nscanId = self.scans[i + 1].getId()
                        if ((nscanId in self.calibratorAssociations and
                             self.calibratorAssociations[nscanId] == self.scans[i].getId()) or
                            (nscanId not in self.calibratorAssociations)):
                            # Pointing will actually be useful here.
                            self.copyScans(ids=[self.scans[i].getId()], pos=i, calCheck=False, keepId=False)
                            self.scans[i].setScanType("Point")
                            self.scans[i].setPointing("Update")
                            self.scans[i].setScanLength("00:02:00")
                            lastPointings[self.scans[i].getSource()] = { "scan": i, "timeDelta": 0 }
            elif bandNeedsPointing:
                # Check this isn't a pointing already.
                if self.scans[i].getScanType == "Point":
                    # We just update the pointing  dictionary.
                    lastPointings[self.scans[i].getSource()] = { "scan": i, "timeDelta": 0 }
                else:
                    # We change this scan to use "OffPnt" pointing type.
                    self.scans[i].setPointing("Offpnt")
            # Increment the time since last pointing.
            for j in lastPointings:
                lastPointings[j]['timeDelta'] += self.__durationSeconds(scan=i)
            i += 1
                
                        
        
        # Check 4: add focus scans when the frequency configuration changes.
        # We will only need to do focus scans if we change to or from 4cm.
        if len(observedBands) > 1 and "4cm" in observedBands:
            # Find the transition points.
            i = 1
            while i < len(self.scans):
                #print("[completeSchedule] schedule now has %d scans" % len(self.scans))
                tband = self.scans[i - 1].IF1().getFrequencyBand()
                nband = self.scans[i].IF1().getFrequencyBand()
                if tband != nband and (tband == "4cm" or nband == "4cm"):
                    #print("[completeSchedule] found band change between %d and %d" % ((i - 1), i))
                    #pscan = self.scans[i - 1]
                    #nscan = self.scans[i]
                    #print("[completeSchedule] scan %d: %s %d/%d <%s> [%s] '%s'" % ((i - 1), pscan.getSource(),
                    #                                                               pscan.IF1().getFreq(),
                    #                                                               pscan.IF2().getFreq(),
                    #                                                               pscan.getId(), pscan.getCommand(),
                    #                                                               pscan.getComment()))
                    #print("[completeSchedule] scan %d: %s %d/%d <%s> [%s] '%s'" % (i, nscan.getSource(),
                    #                                                               nscan.IF1().getFreq(),
                    #                                                               nscan.IF2().getFreq(),
                    #                                                               nscan.getId(), nscan.getCommand(),
                    #                                                               nscan.getComment()))
                    
                    # Check first to see if a focus command is already present.
                    ncmd = self.scans[i].getCommand()
                    #print("[completeSchedule] command in current scan [%s]" % ncmd)
                    if "foc" not in ncmd:
                        # Add a focus scan after this scan.
                        # We have to keep the frequencies here, because of the way IDs work.
                        nf1 = self.scans[i].IF1().getFreq()
                        nf2 = self.scans[i].IF2().getFreq()
                        nscanId = self.scans[i].getId()
                        #print("[completeSchedule] copying scan %d" % i)
                        self.copyScans(ids=[nscanId], pos=i, calCheck=False, keepId=False)
                        # Change the name of this scan and add a focus command.
                        self.scans[i].setSource("focus")
                        self.scans[i].setCommand("focus default")
                        # Ensure the right frequencies.
                        self.scans[i].IF1().setFreq(nf1)
                        self.scans[i].IF2().setFreq(nf2)
                        # Change it to be 90 seconds long and a Normal type.
                        self.scans[i].setScanType("Normal")
                        self.scans[i].setPointing("Global")
                        self.scans[i].setScanLength("00:01:30")
                        #self.scans[i].setComment("bandchange")
                i += 1


    
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

    def __durationSeconds(self, scan=None):
        # Return the duration of the nominated scan in seconds.
        durSeconds = 0
        if scan is not None and scan >= 0 and scan < len(self.scans):
            durString = self.scans[scan].getScanLength()
            durEls = durString.split(":")
            durSeconds = int(durEls[0]) * 3600 + int(durEls[1]) * 60 + int(durEls[2])
        return durSeconds

    def __angleRadians(self, scan=None):
        # Return the right ascension and declination as radian angles.
        if scan is not None and scan >= 0 and scan < len(self.scans):
            raString = self.scans[scan].getRightAscension()
            decString = self.scans[scan].getDeclination()
            raEls = raString.split(":")
            decEls = decString.split(":")
            raRads = (math.pi / 180.0) * 15.0 * (float(raEls[0]) + float(raEls[1]) / 60.0 +
                                                 float(raEls[2]) / 3600.0)
            decSign = 1.0
            decPattern = re.compile("^\-")
            if decPattern.match(decString):
                decSign = -1.0
            decRads = decSign * (math.pi / 180.0) * (decSign * float(decEls[0]) +
                                                     float(decEls[1]) / 60.0 + float(decEls[2]) / 3600.0)
            return { "rightAscension": raRads, "declination": decRads }
        return { "rightAscension": None, "declination": None }

    def __angularDistance(self, scanOrig=None, scanDest=None):
        # Return the angular distance between the original scan and the destination
        # scan, in degrees.
        if (scanOrig is not None and scanOrig >= 0 and scanOrig < len(self.scans) and
            scanDest is not None and scanDest >= 0 and scanDest < len(self.scans)):
            # We don't need to be particularly sophisticated in our approach here,
            # because we just need a rough estimate of the distance.
            if scanOrig == scanDest:
                # Obviously 0.
                return 0
            scanOrigCoord = self.__angleRadians(scan=scanOrig)
            scanDestCoord = self.__angleRadians(scan=scanDest)
            if (scanOrigCoord["rightAscension"] is not None and
                scanDestCoord["rightAscension"] is not None):
                try:
                    angDist = math.acos(math.sin(scanOrigCoord["declination"]) *
                                        math.sin(scanDestCoord["declination"]) +
                                        math.cos(scanOrigCoord["declination"]) *
                                        math.cos(scanDestCoord["declination"]) *
                                        math.cos(scanDestCoord["rightAscension"] -
                                                 scanOrigCoord["rightAscension"]))
                except ValueError as e:
                    print ("got value error")
                    print ("original coordinates RA = %.4f (%s) Dec = %.4f (%s)" %
                           (scanOrigCoord["rightAscension"], self.scans[scanOrig].getRightAscension(),
                            scanOrigCoord["declination"], self.scans[scanOrig].getDeclination()))
                    print ("destination coordinates RA = %.4f (%s) Dec = %.4f (%s)" %
                           (scanDestCoord["rightAscension"], self.scans[scanDest].getRightAscension(),
                            scanDestCoord["declination"], self.scans[scanDest].getDeclination()))
                    angDist = 0.0
                return angDist * 180.0 / math.pi
        return None
    
    def needsPointing(self, band=None):
        # Return indication of whether the specified band needs a pointing in this
        # schedule.
        if band is None:
            return False
        if (band is not "16cm" and band is not "4cm" and band is not "15mm" and
            band is not "7mm" and band is not "3mm"):
            # Unrecognised band name.
            return False
        if ((self.pointingLowBand == "16cm") or
            ((self.pointingLowBand == "4cm") and (band != "16cm")) or
            ((self.pointingLowBand == "15mm") and (band != "16cm" and band != "4cm")) or
            ((self.pointingLowBand == "7mm") and (band == "7mm" or band == "3mm")) or
            ((self.pointingLowBand == "3mm") and (band == "3mm"))):
            return True
        return False
    
