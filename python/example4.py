# example4.py
# Jamie Stevens
# Part of the ATCA scheduler Python library.

# This example illustrates how the rapid response system creates a schedule
# for a request for multiple frequencies.
# Example 4:
# Suppose an event trigger has been received for a flaring magnetar at
# coordinates RA = 01:00:43.1, Dec = -23:11:33.8.
# You send a request to the 2022 ATCA rapid response system, asking for
# observations of this magnetar at 4cm and 15mm.

# Include the library.
import cabb_scheduler as cabb
import datetime
import ephem
import math
    

def createAtcaObject(*args):
    # The location of the ATCA observatory as an PyEphem observer.
    atca = ephem.Observer()
    atca.lon = '149.56394'
    atca.lat = '-30.31498'
    atca.elevation = 240
    atcaHorizon = 12 # in degrees.
    atca.horizon = str(atcaHorizon)

    return atca

def coordsToFixedBody(ra, dec):
    fixedBody = ephem.FixedBody()
    fixedBody._epoch = '2000'
    fixedBody._ra = ra
    fixedBody._dec = dec
    return fixedBody

def stringTimeToDelta(l):
    stringTimes = l.split(":")
    stringDelta = datetime.timedelta(hours=int(stringTimes[0]),
                                     minutes=int(stringTimes[1]),
                                     seconds=int(stringTimes[2]))
    return stringDelta

def stringTimeToHours(l):
    stringTimes = l.split(":")
    stringHours = (float(stringTimes[0]) + float(stringTimes[1]) / 60.0 +
                   float(stringTimes[2]) / 3600.0)
    return stringHours

def stringTimeToDegrees(l):
    stringEls = l.split(":")
    nfac = 1.0
    if '-' in stringEls[0]:
        nfac = -1.0
    stringDegs = nfac * (nfac * float(stringEls[0]) +
                         float(stringEls[1]) / 60.0 +
                         float(stringEls[2]) / 3600.0)
    return stringDegs

def setTimes(ra=None, dec=None, lat=None, el=None):
    # Work out the setting below el LST of an object with RA, Dec and at
    # an observatory at specified latitude (RA specified in HH:MM:SS,
    # Dec specified in DD:MM:SS, and lat and el specified in decimal deg).
    if ra is None or dec is None or lat is None or el is None:
        return None
    raH = stringTimeToHours(ra)
    decR = stringTimeToDegrees(dec) * math.pi / 180.0
    latR = lat * math.pi / 180.0
    elR = el * math.pi / 180.0
    cosHaSet = ((math.cos((math.pi / 2.0 ) - elR) -
                 math.sin(latR) * math.sin(decR)) /
                (math.cos(decR) * math.cos(latR)))
    if cosHaSet > 1 or cosHaSet < -1:
        # Never sets, or never rises.
        return { 'rise': None, 'set': None }
    haSetH = math.acos(cosHaSet) * 180.0 / (math.pi * 15.0)
    raRiseH = raH - haSetH
    if raRiseH < 0:
        raRiseH += 24.0
    raSetH = raH + haSetH
    if raSetH > 24:
        raSetH -= 24.0
    return { 'rise': raRiseH, 'set': raSetH }
    

if __name__ == "__main__":
    # Set up the dictionary for the request.
    requestDict = {
        "source": "magnetar", "rightAscension": "01:00:43.1",
        "declination": "-23:11:33.8", "project": "C006",
        "maxExposureLength": "12:00:00", "minExposureLength": "03:00:00",
        "4cm": { "use": True, "exposureLength": "00:30:00",
                 "freq1": 5500, "freq2": 9000 },
        "15mm": { "use": True, "exposureLength": "00:30:00",
                  "freq1": 17000, "freq2": 19000 }
    }

    # Make some objects for later.
    lstToHours = 0.9972222
    sourceTimes = setTimes(ra=requestDict["rightAscension"],
                           dec=requestDict["declination"],
                           lat=-30.31498, el=12.0)
    
    # We will make several schedules to illustrate how the schedule will
    # be generated in different circumstances.

    # We will assume a 6km array for convenience.
    arrayName = "6A"
    # Some parameters that control the schedule building process.
    # Information about maximum scan lengths between calibrators per band, in seconds.
    bandMaxScanLengths = {
        # 40 minutes at 16cm.
        '16cm': 2400,
        # 20 minutes at 4cm.
        '4cm': 1200,
        # 15 minutes at 15mm.
        '15mm': 900,
        # 10 minutes at 7mm.
        '7mm': 600
    }
    # Calibrator scan length, in seconds.
    # Always 2 minutes.
    calibratorScanLengths = 120

    # Do some preparation.
    bandsAvailable = [ "16cm", "4cm", "15mm", "7mm" ]
    bandsFrequencyRanges = { "16cm": [ 1729, 2300 ],
                             "4cm": [ 4928, 10928 ],
                             "15mm": [ 16000, 24000 ],
                             "7mm": [ 30000, 50000 ] }
    bandsRequested = []
    for b in bandsAvailable:
        if (b in requestDict and "use" in requestDict[b] and
            requestDict[b]["use"] == True):
            bandsRequested.append(b)

    # First, the easiest circumstance. The source is above the horizon and
    # CABB is in 1 MHz continuum mode. 
    correlatorConfig = "ca_2048_2048_2f"
    cabb64 = False
    doCalibration = False

    schedule1 = cabb.schedule()
    schedule1.setLooping(False)
    schedule1.enablePrepScans()
    schedule1.setPointingLowBand("15mm")

    # Set the LST at the start. In this case, we set it to be just after the
    # source rises at 19:10.
    startLst = "19:10:00"
    startLstHours = stringTimeToHours(startLst)
    # How long can we run?
    maxLengthHours = stringTimeToHours(requestDict["maxExposureLength"])
    # Or before the source sets.
    if sourceTimes['set'] is None:
        # We assume we can go for the full duration since the source doesn't set.
        untilSetHours = maxLengthHours
    else :
        untilSetHours = sourceTimes['set'] - startLstHours
        if untilSetHours < 0:
            untilSetHours += 24.0
        untilSetHours *= lstToHours
    timeRemainingHours = untilSetHours
    if maxLengthHours < untilSetHours:
        timeRemainingHours = maxLengthHours
    # Set aside 10 minutes per band for flux density calibration.
    # This should account for slewing time and focusing time etc.
    maxLengthHours -= len(bandsRequested) * (10.0 / 60.0)
    # We need to work out how long we can wait until we visit our flux
    # density calibrator.
    # We only try to get 1934-638, as it is not worth getting 0823-500.
    # We also try to get 1934-638 above 35 degrees, so we have good quality
    # data and a bit of leeway if the schedule runs differently to what we
    # expect.
    fluxcalRiseLst12 = stringTimeToHours("11:01:00")
    fluxcalRiseLst35 = stringTimeToHours("14:53:00")
    fluxcalSetLst35 = stringTimeToHours("00:25:00")
    fluxcalSetLst12 = stringTimeToHours("04:18:00")
    hoursLeft35 = 0
    checkRise = False
    addFluxCal = True
    # Check if the cal is up at the start.
    if (startLstHours > fluxcalRiseLst12 or startLstHours < fluxcalSetLst12):
        # It is up. We work out if we have time before it goes below 35 degrees.
        if (startLstHours > fluxcalRiseLst35 or startLstHours < fluxcalSetLst35):
            # OK, we have some time. How much time until it drops below 35 degrees?
            hoursLeft35 = fluxcalSetLst35 - startLstHours
            if hoursLeft35 < 0:
                hoursLeft35 += 24.0
            # We will go to the flux density calibrator within this time.
            hoursLeft35 *= lstToHours
        else:
            # Are we rising or setting?
            if (startLstHours > fluxcalRiseLst12 and startLstHours < fluxcalRiseLst35):
                # We are rising, we can wait for a long time.
                hoursLeft35 = fluxcalSetLst35 - startLstHours
                if hoursLeft35 < 0:
                    hoursLeft35 += 24.0
                hoursLeft35 *= lstToHours
            else:
                # We are setting. Do we have enough time to go now?
                checkLeft = fluxcalSetLst12 - startLstHours
                if checkLeft < 0:
                    checkLeft += 24.0
                if checkLeft >= 0.5:
                    # We can go now.
                    hoursLeft35 = 0
                else:
                    # We may need to wait until it next rises.
                    checkRise = True
    else:
        checkRise = True
    if checkRise:
        # It is not up yet. How long until it rises above 35 degrees?
        hoursLeft35 = fluxcalRiseLst35 - startLstHours
        if hoursLeft35 < 0:
            hoursLeft35 += 24.0
        hoursLeft35 *= lstToHours
        # Check if we will have finished by then?
        if hoursLeft35 > timeRemainingHours:
            # We will have to compromise. Can we get the flux cal below 35 degrees?
            hoursLeft12 = fluxcalRiseLst12 - startLstHours
            if hoursLeft12 < timeRemainingHours:
                # OK, we'll go at the end
                hoursLeft35 = timeRemainingHours
            else:
                # We can't get flux calibration.
                addFluxCal = False
        # else we will go just after the flux cal rises above 35 degrees; we do it
        # that way so that we don't get caught out by an experiment that might go
        # all the way past the flux cal rising and then setting again; we don't need
        # to do anything here because hoursLeft35 is already set correctly at this
        # point.
        
    bandScans1 = []
    bandCals1 = []
    bandReps1 = []
    # This is the amount of time consumed so far, in hours.
    timeConsumed = 0
    fluxCalAdded = not addFluxCal
    while True:
        # Check if we've exceeded the time.
        if timeConsumed >= timeRemainingHours:
            # We're done.
            break
        if timeConsumed >= hoursLeft35 and not fluxCalAdded:
            # Time to put in the flux density calibrators.
            for i in range(0, len(bandsRequested)):
                b = bandsRequested[i]
                if (b in requestDict and "use" in requestDict[b] and
                    requestDict[b]["use"] == True):
                    schedule1.addScan(
                        { "source": "1934-638",
                          "rightAscension": "19:39:25.026",
                          "declination": "-63:42:45.63",
                          "freq1": requestDict[b]["freq1"],
                          "freq2": requestDict[b]["freq2"],
                          "project": requestDict["project"],
                          "calCode": "C",
                          "scanType": "Dwell", "scanLength": "00:05:00" })
            fluxCalAdded = True
            # Allow for slewing, focus, pointing.
            timeConsumed += len(bandsRequested) * 15.0 / 60.0
        for i in range(0, len(bandsRequested)):
            b = bandsRequested[i]
            if (b in requestDict and "use" in requestDict[b] and
                requestDict[b]["use"] == True):
                # Check if we've already worked out how to schedule this.
                bandComplete = False
                bandCompleteId = None
                freqLength = stringTimeToDelta(requestDict[b]["exposureLength"])
                for j in range(0, len(bandScans1)):
                    if (bandScans1[j].getSource() == requestDict["source"] and
                        bandScans1[j].IF1().getFreq() == requestDict[b]["freq1"] and
                        bandScans1[j].IF2().getFreq() == requestDict[b]["freq2"]):
                        bandComplete = True
                        nReps = bandReps1[j]
                        bandCompleteId = bandScans1[j].getId()
                        break
                if bandComplete:
                    # We just need to copy some scans.
                    for j in range(0, nReps):
                        schedule1.copyScans([ bandCompleteId ])
                else:
                    # We need to work out how long to make each scan.
                    nReps = 1
                    compLength = ((nReps * datetime.timedelta(seconds=bandMaxScanLengths[b]) +
                                   (nReps * 2) * datetime.timedelta(seconds=calibratorScanLengths)))
                    while (freqLength > compLength):
                        nReps += 1
                        compLength = ((nReps * datetime.timedelta(seconds=bandMaxScanLengths[b]) +
                                       (nReps * 2) * datetime.timedelta(seconds=calibratorScanLengths)))
                    dwellLength = str(freqLength / nReps)
                    bandScans1.append(schedule1.addScan(
                        { "source": requestDict["source"],
                          "rightAscension": requestDict["rightAscension"],
                          "declination": requestDict["declination"],
                          "freq1": requestDict[b]["freq1"],
                          "freq2": requestDict[b]["freq2"],
                          "project": requestDict["project"],
                          "scanType": "Dwell", "scanLength": dwellLength }
                    ))
                    bandReps1.append(nReps)
                    # Find a calibrator for this scan.
                    calList = bandScans1[-1].findCalibrator()
                    bestCal = calList.getBestCalibrator(arrayName)
                    bandCals1.append(schedule1.addCalibrator(
                        bestCal['calibrator'], bandScans1[-1],
                        { 'scanLength': str(datetime.timedelta(seconds=calibratorScanLengths)) }))
                    # Repeat this the appropriate number of times.
                    for j in range(1, nReps):
                        schedule1.copyScans([ bandScans1[-1].getId() ])
                # Allow for 20s slews.
                timeConsumed += ((nReps * stringTimeToHours(dwellLength)) +
                                 (nReps * 2 * 20.0 / 3600.0) +
                                 ((nReps + 1) * calibratorScanLengths / 3600.0))
                # If we're in a pointing band, allow a bit of extra time per hour.
                if schedule1.needsPointing(b):
                    timeConsumed += (2.0 / 60.0)
                # Add some time for focusing.
                timeConsumed += 2.0 / 60.0
                
    if not fluxCalAdded:
        # We have to put the flux calibrators at the end.
        for i in range(0, len(bandsRequested)):
            b = bandsRequested[i]
            if (b in requestDict and "use" in requestDict[b] and
                requestDict[b]["use"] == True):
                schedule1.addScan(
                    { "source": "1934-638",
                      "rightAscension": "19:39:25.026",
                      "declination": "-63:42:45.63",
                      "freq1": requestDict[b]["freq1"],
                      "freq2": requestDict[b]["freq2"],
                      "project": requestDict[b]["project"],
                      "calCode": "C",
                      "scanType": "Dwell", "scanLength": "00:05:00" })

    # Output the schedule.
    schedule1.completeSchedule()
    # Set the LST of the first scan.
    schedule1.getScan(idx=0).setTime(startLst)
    schedule1.write(name="c006_magnetar_example4_test1.sch")

    # Next, the source is setting, and CABB is in 1 MHz continuum mode. 
    correlatorConfig = "ca_2048_2048_2f"
    cabb64 = False
    doCalibration = False

    schedule2 = cabb.schedule()
    schedule2.setLooping(False)
    schedule2.enablePrepScans()
    schedule2.setPointingLowBand("15mm")

    # Set the LST at the start. In this case, we set it to be just after the
    # source transits at 01:10.
    startLst = "01:10:00"
    startLstHours = stringTimeToHours(startLst)
    # How long can we run?
    maxLengthHours = stringTimeToHours(requestDict["maxExposureLength"])
    # Or before the source sets.
    if sourceTimes['set'] is None:
        # We assume we can go for the full duration since the source doesn't set.
        untilSetHours = maxLengthHours
    else :
        untilSetHours = sourceTimes['set'] - startLstHours
        if untilSetHours < 0:
            untilSetHours += 24.0
        untilSetHours *= lstToHours
    timeRemainingHours = untilSetHours
    if maxLengthHours < untilSetHours:
        timeRemainingHours = maxLengthHours
    # Set aside 10 minutes per band for flux density calibration.
    # This should account for slewing time and focusing time etc.
    maxLengthHours -= len(bandsRequested) * (10.0 / 60.0)
    # We need to work out how long we can wait until we visit our flux
    # density calibrator.
    # We only try to get 1934-638, as it is not worth getting 0823-500.
    # We also try to get 1934-638 above 35 degrees, so we have good quality
    # data and a bit of leeway if the schedule runs differently to what we
    # expect.
    fluxcalRiseLst12 = stringTimeToHours("11:01:00")
    fluxcalRiseLst35 = stringTimeToHours("14:53:00")
    fluxcalSetLst35 = stringTimeToHours("00:25:00")
    fluxcalSetLst12 = stringTimeToHours("04:18:00")
    hoursLeft35 = 0
    checkRise = False
    addFluxCal = True
    # Check if the cal is up at the start.
    if (startLstHours > fluxcalRiseLst12 or startLstHours < fluxcalSetLst12):
        # It is up. We work out if we have time before it goes below 35 degrees.
        if (startLstHours > fluxcalRiseLst35 or startLstHours < fluxcalSetLst35):
            # OK, we have some time. How much time until it drops below 35 degrees?
            hoursLeft35 = fluxcalSetLst35 - startLstHours
            if hoursLeft35 < 0:
                hoursLeft35 += 24.0
            # We will go to the flux density calibrator within this time.
            hoursLeft35 *= lstToHours
        else:
            # Are we rising or setting?
            if (startLstHours > fluxcalRiseLst12 and startLstHours < fluxcalRiseLst35):
                # We are rising, we can wait for a long time.
                hoursLeft35 = fluxcalSetLst35 - startLstHours
                if hoursLeft35 < 0:
                    hoursLeft35 += 24.0
                hoursLeft35 *= lstToHours
            else:
                # We are setting. Do we have enough time to go now?
                checkLeft = fluxcalSetLst12 - startLstHours
                if checkLeft < 0:
                    checkLeft += 24.0
                if checkLeft >= 0.5:
                    # We can go now.
                    hoursLeft35 = 0
                else:
                    # We may need to wait until it next rises.
                    checkRise = True
    else:
        checkRise = True
    if checkRise:
        # It is not up yet. How long until it rises above 35 degrees?
        hoursLeft35 = fluxcalRiseLst35 - startLstHours
        if hoursLeft35 < 0:
            hoursLeft35 += 24.0
        hoursLeft35 *= lstToHours
        # Check if we will have finished by then?
        if hoursLeft35 > timeRemainingHours:
            # We will have to compromise. Can we get the flux cal below 35 degrees?
            hoursLeft12 = fluxcalRiseLst12 - startLstHours
            if hoursLeft12 < timeRemainingHours:
                # OK, we'll go at the end
                hoursLeft35 = timeRemainingHours
            else:
                # We can't get flux calibration.
                addFluxCal = False
        # else we will go just after the flux cal rises above 35 degrees; we do it
        # that way so that we don't get caught out by an experiment that might go
        # all the way past the flux cal rising and then setting again; we don't need
        # to do anything here because hoursLeft35 is already set correctly at this
        # point.
        
    bandScans2 = []
    bandCals2 = []
    bandReps2 = []
    # This is the amount of time consumed so far, in hours.
    timeConsumed = 0
    fluxCalAdded = not addFluxCal
    while True:
        # Check if we've exceeded the time.
        if timeConsumed >= timeRemainingHours:
            # We're done.
            break
        if timeConsumed >= hoursLeft35 and not fluxCalAdded:
            # Time to put in the flux density calibrators.
            for i in range(0, len(bandsRequested)):
                b = bandsRequested[i]
                if (b in requestDict and "use" in requestDict[b] and
                    requestDict[b]["use"] == True):
                    schedule2.addScan(
                        { "source": "1934-638",
                          "rightAscension": "19:39:25.026",
                          "declination": "-63:42:45.63",
                          "freq1": requestDict[b]["freq1"],
                          "freq2": requestDict[b]["freq2"],
                          "project": requestDict["project"],
                          "calCode": "C",
                          "scanType": "Dwell", "scanLength": "00:05:00" })
            fluxCalAdded = True
            # Allow for slewing, focus, pointing.
            timeConsumed += len(bandsRequested) * 15.0 / 60.0
        for i in range(0, len(bandsRequested)):
            b = bandsRequested[i]
            if (b in requestDict and "use" in requestDict[b] and
                requestDict[b]["use"] == True):
                # Check if we've already worked out how to schedule this.
                bandComplete = False
                bandCompleteId = None
                freqLength = stringTimeToDelta(requestDict[b]["exposureLength"])
                for j in range(0, len(bandScans2)):
                    if (bandScans2[j].getSource() == requestDict["source"] and
                        bandScans2[j].IF1().getFreq() == requestDict[b]["freq1"] and
                        bandScans2[j].IF2().getFreq() == requestDict[b]["freq2"]):
                        bandComplete = True
                        nReps = bandReps2[j]
                        bandCompleteId = bandScans2[j].getId()
                        break
                if bandComplete:
                    # We just need to copy some scans.
                    for j in range(0, nReps):
                        schedule2.copyScans([ bandCompleteId ])
                else:
                    # We need to work out how long to make each scan.
                    nReps = 1
                    compLength = ((nReps * datetime.timedelta(seconds=bandMaxScanLengths[b]) +
                                   (nReps * 2) * datetime.timedelta(seconds=calibratorScanLengths)))
                    while (freqLength > compLength):
                        nReps += 1
                        compLength = ((nReps * datetime.timedelta(seconds=bandMaxScanLengths[b]) +
                                       (nReps * 2) * datetime.timedelta(seconds=calibratorScanLengths)))
                    dwellLength = str(freqLength / nReps)
                    bandScans2.append(schedule2.addScan(
                        { "source": requestDict["source"],
                          "rightAscension": requestDict["rightAscension"],
                          "declination": requestDict["declination"],
                          "freq1": requestDict[b]["freq1"],
                          "freq2": requestDict[b]["freq2"],
                          "project": requestDict["project"],
                          "scanType": "Dwell", "scanLength": dwellLength }
                    ))
                    bandReps2.append(nReps)
                    # Find a calibrator for this scan.
                    calList = bandScans2[-1].findCalibrator()
                    bestCal = calList.getBestCalibrator(arrayName)
                    bandCals2.append(schedule2.addCalibrator(
                        bestCal['calibrator'], bandScans2[-1],
                        { 'scanLength': str(datetime.timedelta(seconds=calibratorScanLengths)) }))
                    # Repeat this the appropriate number of times.
                    for j in range(1, nReps):
                        schedule2.copyScans([ bandScans2[-1].getId() ])
                # Allow for 20s slews.
                timeConsumed += ((nReps * stringTimeToHours(dwellLength)) +
                                 (nReps * 2 * 20.0 / 3600.0) +
                                 ((nReps + 1) * calibratorScanLengths / 3600.0))
                # If we're in a pointing band, allow a bit of extra time per hour.
                if schedule2.needsPointing(b):
                    timeConsumed += (2.0 / 60.0)
                # Add some time for focusing.
                timeConsumed += 2.0 / 60.0
                
    if not fluxCalAdded:
        # We have to put the flux calibrators at the end.
        for i in range(0, len(bandsRequested)):
            b = bandsRequested[i]
            if (b in requestDict and "use" in requestDict[b] and
                requestDict[b]["use"] == True):
                schedule2.addScan(
                    { "source": "1934-638",
                      "rightAscension": "19:39:25.026",
                      "declination": "-63:42:45.63",
                      "freq1": requestDict[b]["freq1"],
                      "freq2": requestDict[b]["freq2"],
                      "project": requestDict[b]["project"],
                      "calCode": "C",
                      "scanType": "Dwell", "scanLength": "00:05:00" })

    # Output the schedule.
    schedule2.completeSchedule()
    # Set the LST of the first scan.
    schedule2.getScan(idx=0).setTime(startLst)
    schedule2.write(name="c006_magnetar_example4_test2.sch")
    
    # Next, there is no chance to get 1934-638.
    correlatorConfig = "ca_2048_2048_2f"
    cabb64 = False
    doCalibration = False

    schedule3 = cabb.schedule()
    schedule3.setLooping(False)
    schedule3.enablePrepScans()
    schedule3.setPointingLowBand("15mm")

    # Set the LST at the start. In this case, we set it to be just 3 hours before
    # the source sets.
    startLst = "03:50:00"
    startLstHours = stringTimeToHours(startLst)
    # How long can we run?
    maxLengthHours = stringTimeToHours(requestDict["maxExposureLength"])
    # Or before the source sets.
    if sourceTimes['set'] is None:
        # We assume we can go for the full duration since the source doesn't set.
        untilSetHours = maxLengthHours
    else :
        untilSetHours = sourceTimes['set'] - startLstHours
        if untilSetHours < 0:
            untilSetHours += 24.0
        untilSetHours *= lstToHours
    timeRemainingHours = untilSetHours
    if maxLengthHours < untilSetHours:
        timeRemainingHours = maxLengthHours
    # Set aside 10 minutes per band for flux density calibration.
    # This should account for slewing time and focusing time etc.
    maxLengthHours -= len(bandsRequested) * (10.0 / 60.0)
    # We need to work out how long we can wait until we visit our flux
    # density calibrator.
    # We only try to get 1934-638, as it is not worth getting 0823-500.
    # We also try to get 1934-638 above 35 degrees, so we have good quality
    # data and a bit of leeway if the schedule runs differently to what we
    # expect.
    fluxcalRiseLst12 = stringTimeToHours("11:01:00")
    fluxcalRiseLst35 = stringTimeToHours("14:53:00")
    fluxcalSetLst35 = stringTimeToHours("00:25:00")
    fluxcalSetLst12 = stringTimeToHours("04:18:00")
    hoursLeft35 = 0
    checkRise = False
    addFluxCal = True
    # Check if the cal is up at the start.
    if (startLstHours > fluxcalRiseLst12 or startLstHours < fluxcalSetLst12):
        # It is up. We work out if we have time before it goes below 35 degrees.
        if (startLstHours > fluxcalRiseLst35 or startLstHours < fluxcalSetLst35):
            # OK, we have some time. How much time until it drops below 35 degrees?
            hoursLeft35 = fluxcalSetLst35 - startLstHours
            if hoursLeft35 < 0:
                hoursLeft35 += 24.0
            # We will go to the flux density calibrator within this time.
            hoursLeft35 *= lstToHours
        else:
            # Are we rising or setting?
            if (startLstHours > fluxcalRiseLst12 and startLstHours < fluxcalRiseLst35):
                # We are rising, we can wait for a long time.
                hoursLeft35 = fluxcalSetLst35 - startLstHours
                if hoursLeft35 < 0:
                    hoursLeft35 += 24.0
                hoursLeft35 *= lstToHours
            else:
                # We are setting. Do we have enough time to go now?
                checkLeft = fluxcalSetLst12 - startLstHours
                if checkLeft < 0:
                    checkLeft += 24.0
                if checkLeft >= 0.5:
                    # We can go now.
                    hoursLeft35 = 0
                else:
                    # We may need to wait until it next rises.
                    checkRise = True
    else:
        checkRise = True
    if checkRise:
        # It is not up yet. How long until it rises above 35 degrees?
        hoursLeft35 = fluxcalRiseLst35 - startLstHours
        if hoursLeft35 < 0:
            hoursLeft35 += 24.0
        hoursLeft35 *= lstToHours
        # Check if we will have finished by then?
        if hoursLeft35 > timeRemainingHours:
            # We will have to compromise. Can we get the flux cal below 35 degrees?
            hoursLeft12 = fluxcalRiseLst12 - startLstHours
            if hoursLeft12 < timeRemainingHours:
                # OK, we'll go at the end
                hoursLeft35 = timeRemainingHours
            else:
                # We can't get flux calibration.
                addFluxCal = False
        # else we will go just after the flux cal rises above 35 degrees; we do it
        # that way so that we don't get caught out by an experiment that might go
        # all the way past the flux cal rising and then setting again; we don't need
        # to do anything here because hoursLeft35 is already set correctly at this
        # point.
        
    bandScans3 = []
    bandCals3 = []
    bandReps3 = []
    # This is the amount of time consumed so far, in hours.
    timeConsumed = 0
    fluxCalAdded = not addFluxCal
    while True:
        # Check if we've exceeded the time.
        if timeConsumed >= timeRemainingHours:
            # We're done.
            break
        if timeConsumed >= hoursLeft35 and not fluxCalAdded:
            # Time to put in the flux density calibrators.
            for i in range(0, len(bandsRequested)):
                b = bandsRequested[i]
                if (b in requestDict and "use" in requestDict[b] and
                    requestDict[b]["use"] == True):
                    schedule3.addScan(
                        { "source": "1934-638",
                          "rightAscension": "19:39:25.026",
                          "declination": "-63:42:45.63",
                          "freq1": requestDict[b]["freq1"],
                          "freq2": requestDict[b]["freq2"],
                          "project": requestDict["project"],
                          "calCode": "C",
                          "scanType": "Dwell", "scanLength": "00:05:00" })
            fluxCalAdded = True
            # Allow for slewing, focus, pointing.
            timeConsumed += len(bandsRequested) * 15.0 / 60.0
        for i in range(0, len(bandsRequested)):
            b = bandsRequested[i]
            if (b in requestDict and "use" in requestDict[b] and
                requestDict[b]["use"] == True):
                # Check if we've already worked out how to schedule this.
                bandComplete = False
                bandCompleteId = None
                freqLength = stringTimeToDelta(requestDict[b]["exposureLength"])
                for j in range(0, len(bandScans3)):
                    if (bandScans3[j].getSource() == requestDict["source"] and
                        bandScans3[j].IF1().getFreq() == requestDict[b]["freq1"] and
                        bandScans3[j].IF2().getFreq() == requestDict[b]["freq2"]):
                        bandComplete = True
                        nReps = bandReps3[j]
                        bandCompleteId = bandScans3[j].getId()
                        break
                if bandComplete:
                    # We just need to copy some scans.
                    for j in range(0, nReps):
                        schedule3.copyScans([ bandCompleteId ])
                else:
                    # We need to work out how long to make each scan.
                    nReps = 1
                    compLength = ((nReps * datetime.timedelta(seconds=bandMaxScanLengths[b]) +
                                   (nReps * 2) * datetime.timedelta(seconds=calibratorScanLengths)))
                    while (freqLength > compLength):
                        nReps += 1
                        compLength = ((nReps * datetime.timedelta(seconds=bandMaxScanLengths[b]) +
                                       (nReps * 2) * datetime.timedelta(seconds=calibratorScanLengths)))
                    dwellLength = str(freqLength / nReps)
                    bandScans3.append(schedule3.addScan(
                        { "source": requestDict["source"],
                          "rightAscension": requestDict["rightAscension"],
                          "declination": requestDict["declination"],
                          "freq1": requestDict[b]["freq1"],
                          "freq2": requestDict[b]["freq2"],
                          "project": requestDict["project"],
                          "scanType": "Dwell", "scanLength": dwellLength }
                    ))
                    bandReps3.append(nReps)
                    # Find a calibrator for this scan.
                    calList = bandScans2[-1].findCalibrator()
                    bestCal = calList.getBestCalibrator(arrayName)
                    bandCals3.append(schedule3.addCalibrator(
                        bestCal['calibrator'], bandScans3[-1],
                        { 'scanLength': str(datetime.timedelta(seconds=calibratorScanLengths)) }))
                    # Repeat this the appropriate number of times.
                    for j in range(1, nReps):
                        schedule3.copyScans([ bandScans3[-1].getId() ])
                # Allow for 20s slews.
                timeConsumed += ((nReps * stringTimeToHours(dwellLength)) +
                                 (nReps * 2 * 20.0 / 3600.0) +
                                 ((nReps + 1) * calibratorScanLengths / 3600.0))
                # If we're in a pointing band, allow a bit of extra time per hour.
                if schedule3.needsPointing(b):
                    timeConsumed += (2.0 / 60.0)
                # Add some time for focusing.
                timeConsumed += 2.0 / 60.0
                
    if not fluxCalAdded:
        # We have to put the flux calibrators at the end.
        for i in range(0, len(bandsRequested)):
            b = bandsRequested[i]
            if (b in requestDict and "use" in requestDict[b] and
                requestDict[b]["use"] == True):
                schedule3.addScan(
                    { "source": "1934-638",
                      "rightAscension": "19:39:25.026",
                      "declination": "-63:42:45.63",
                      "freq1": requestDict[b]["freq1"],
                      "freq2": requestDict[b]["freq2"],
                      "project": requestDict[b]["project"],
                      "calCode": "C",
                      "scanType": "Dwell", "scanLength": "00:05:00" })

    # Output the schedule.
    schedule3.completeSchedule()
    # Set the LST of the first scan.
    schedule3.getScan(idx=0).setTime(startLst)
    schedule3.write(name="c006_magnetar_example4_test3.sch")
    
    # Lastly we repeat the first example but now we have
    # CABB in 64 MHz zoom mode. 
    correlatorConfig = "cfb_64_32_2f_zm16"
    cabb64 = True
    doCalibration = True

    schedule4 = cabb.schedule()
    schedule4.setLooping(False)
    schedule4.enablePrepScans()
    schedule4.enableDelayCal()
    schedule4.setPointingLowBand("15mm")

    # Set the LST at the start. In this case, we set it to be just after the
    # source rises at 19:10.
    startLst = "19:10:00"
    startLstHours = stringTimeToHours(startLst)
    # How long can we run?
    maxLengthHours = stringTimeToHours(requestDict["maxExposureLength"])
    # Or before the source sets.
    if sourceTimes['set'] is None:
        # We assume we can go for the full duration since the source doesn't set.
        untilSetHours = maxLengthHours
    else :
        untilSetHours = sourceTimes['set'] - startLstHours
        if untilSetHours < 0:
            untilSetHours += 24.0
        untilSetHours *= lstToHours
    timeRemainingHours = untilSetHours
    if maxLengthHours < untilSetHours:
        timeRemainingHours = maxLengthHours
    # Set aside 10 minutes per band for flux density calibration.
    # This should account for slewing time and focusing time etc.
    maxLengthHours -= len(bandsRequested) * (10.0 / 60.0)
    # We need to work out how long we can wait until we visit our flux
    # density calibrator.
    # We only try to get 1934-638, as it is not worth getting 0823-500.
    # We also try to get 1934-638 above 35 degrees, so we have good quality
    # data and a bit of leeway if the schedule runs differently to what we
    # expect.
    fluxcalRiseLst12 = stringTimeToHours("11:01:00")
    fluxcalRiseLst35 = stringTimeToHours("14:53:00")
    fluxcalSetLst35 = stringTimeToHours("00:25:00")
    fluxcalSetLst12 = stringTimeToHours("04:18:00")
    hoursLeft35 = 0
    checkRise = False
    addFluxCal = True
    # Check if the cal is up at the start.
    if (startLstHours > fluxcalRiseLst12 or startLstHours < fluxcalSetLst12):
        # It is up. We work out if we have time before it goes below 35 degrees.
        if (startLstHours > fluxcalRiseLst35 or startLstHours < fluxcalSetLst35):
            # OK, we have some time. How much time until it drops below 35 degrees?
            hoursLeft35 = fluxcalSetLst35 - startLstHours
            if hoursLeft35 < 0:
                hoursLeft35 += 24.0
            # We will go to the flux density calibrator within this time.
            hoursLeft35 *= lstToHours
        else:
            # Are we rising or setting?
            if (startLstHours > fluxcalRiseLst12 and startLstHours < fluxcalRiseLst35):
                # We are rising, we can wait for a long time.
                hoursLeft35 = fluxcalSetLst35 - startLstHours
                if hoursLeft35 < 0:
                    hoursLeft35 += 24.0
                hoursLeft35 *= lstToHours
            else:
                # We are setting. Do we have enough time to go now?
                checkLeft = fluxcalSetLst12 - startLstHours
                if checkLeft < 0:
                    checkLeft += 24.0
                if checkLeft >= 0.5:
                    # We can go now.
                    hoursLeft35 = 0
                else:
                    # We may need to wait until it next rises.
                    checkRise = True
    else:
        checkRise = True
    if checkRise:
        # It is not up yet. How long until it rises above 35 degrees?
        hoursLeft35 = fluxcalRiseLst35 - startLstHours
        if hoursLeft35 < 0:
            hoursLeft35 += 24.0
        hoursLeft35 *= lstToHours
        # Check if we will have finished by then?
        if hoursLeft35 > timeRemainingHours:
            # We will have to compromise. Can we get the flux cal below 35 degrees?
            hoursLeft12 = fluxcalRiseLst12 - startLstHours
            if hoursLeft12 < timeRemainingHours:
                # OK, we'll go at the end
                hoursLeft35 = timeRemainingHours
            else:
                # We can't get flux calibration.
                addFluxCal = False
        # else we will go just after the flux cal rises above 35 degrees; we do it
        # that way so that we don't get caught out by an experiment that might go
        # all the way past the flux cal rising and then setting again; we don't need
        # to do anything here because hoursLeft35 is already set correctly at this
        # point.
        
    bandScans4 = []
    bandCals4 = []
    bandReps4 = []
    # This is the amount of time consumed so far, in hours.
    timeConsumed = 0
    fluxCalAdded = not addFluxCal
    while True:
        # Check if we've exceeded the time.
        if timeConsumed >= timeRemainingHours:
            # We're done.
            break
        if timeConsumed >= hoursLeft35 and not fluxCalAdded:
            # Time to put in the flux density calibrators.
            for i in range(0, len(bandsRequested)):
                b = bandsRequested[i]
                if (b in requestDict and "use" in requestDict[b] and
                    requestDict[b]["use"] == True):
                    schedule4.addScan(
                        { "source": "1934-638",
                          "rightAscension": "19:39:25.026",
                          "declination": "-63:42:45.63",
                          "freq1": requestDict[b]["freq1"],
                          "freq2": requestDict[b]["freq2"],
                          "bw1": 64, "bw2": 64,
                          "project": requestDict["project"],
                          "calCode": "C",
                          "scanType": "Dwell", "scanLength": "00:05:00" })
            fluxCalAdded = True
            # Allow for slewing, focus, pointing.
            timeConsumed += len(bandsRequested) * 15.0 / 60.0
        for i in range(0, len(bandsRequested)):
            b = bandsRequested[i]
            if (b in requestDict and "use" in requestDict[b] and
                requestDict[b]["use"] == True):
                # Check if we've already worked out how to schedule this.
                bandComplete = False
                bandCompleteId = None
                freqLength = stringTimeToDelta(requestDict[b]["exposureLength"])
                for j in range(0, len(bandScans4)):
                    if (bandScans4[j].getSource() == requestDict["source"] and
                        bandScans4[j].IF1().getFreq() == requestDict[b]["freq1"] and
                        bandScans4[j].IF2().getFreq() == requestDict[b]["freq2"]):
                        bandComplete = True
                        nReps = bandReps4[j]
                        bandCompleteId = bandScans4[j].getId()
                        break
                if bandComplete:
                    # We just need to copy some scans.
                    for j in range(0, nReps):
                        schedule4.copyScans([ bandCompleteId ])
                else:
                    # We need to work out how long to make each scan.
                    nReps = 1
                    compLength = ((nReps * datetime.timedelta(seconds=bandMaxScanLengths[b]) +
                                   (nReps * 2) * datetime.timedelta(seconds=calibratorScanLengths)))
                    while (freqLength > compLength):
                        nReps += 1
                        compLength = ((nReps * datetime.timedelta(seconds=bandMaxScanLengths[b]) +
                                       (nReps * 2) * datetime.timedelta(seconds=calibratorScanLengths)))
                    dwellLength = str(freqLength / nReps)
                    bandScans4.append(schedule4.addScan(
                        { "source": requestDict["source"],
                          "rightAscension": requestDict["rightAscension"],
                          "declination": requestDict["declination"],
                          "freq1": requestDict[b]["freq1"],
                          "freq2": requestDict[b]["freq2"],
                          "bw1": 64, "bw2": 64,
                          "project": requestDict["project"],
                          "scanType": "Dwell", "scanLength": dwellLength }
                    ))
                    bandReps4.append(nReps)
                    # Find a calibrator for this scan.
                    calList = bandScans4[-1].findCalibrator()
                    bestCal = calList.getBestCalibrator(arrayName)
                    bandCals4.append(schedule4.addCalibrator(
                        bestCal['calibrator'], bandScans4[-1],
                        { 'scanLength': str(datetime.timedelta(seconds=calibratorScanLengths)) }))
                    # Repeat this the appropriate number of times.
                    for j in range(1, nReps):
                        schedule4.copyScans([ bandScans4[-1].getId() ])
                # Allow for 20s slews.
                timeConsumed += ((nReps * stringTimeToHours(dwellLength)) +
                                 (nReps * 2 * 20.0 / 3600.0) +
                                 ((nReps + 1) * calibratorScanLengths / 3600.0))
                # If we're in a pointing band, allow a bit of extra time per hour.
                if schedule4.needsPointing(b):
                    timeConsumed += (2.0 / 60.0)
                # Add some time for focusing.
                timeConsumed += 2.0 / 60.0
                
    if not fluxCalAdded:
        # We have to put the flux calibrators at the end.
        for i in range(0, len(bandsRequested)):
            b = bandsRequested[i]
            if (b in requestDict and "use" in requestDict[b] and
                requestDict[b]["use"] == True):
                schedule4.addScan(
                    { "source": "1934-638",
                      "rightAscension": "19:39:25.026",
                      "declination": "-63:42:45.63",
                      "freq1": requestDict[b]["freq1"],
                      "freq2": requestDict[b]["freq2"],
                      "bw1": 64, "bw2": 64,
                      "project": requestDict[b]["project"],
                      "calCode": "C",
                      "scanType": "Dwell", "scanLength": "00:05:00" })

    # Output the schedule.
    schedule4.completeSchedule()
    # Set the LST of the first scan.
    schedule4.getScan(idx=0).setTime(startLst)
    schedule4.write(name="c006_magnetar_example4_test4.sch")
