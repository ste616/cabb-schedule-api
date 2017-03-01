# This program is to test the Python library functionality.

import cabb_scheduler as cabb

# Make a new schedule.
testSchedule = cabb.schedule()
scan1 = testSchedule.addScan({ 'source': "1934-638", 'rightAscension': "19:39:25.026", 'freq1': 5500, 'freq2': 9000 })
scan2 = testSchedule.addScan()
scan3 = testSchedule.addScan({ 'source': "0823-500", 'rightAscension': "08:25:26.869", 'declination': "-50:10:38.49" })
try:
    scan2.setSource("0537-441").setRightAscension("05:38:50.362").setEpoch("J2000")
except cabb.errors.ScanError as e:
    print "Caught exception: ", e.value
scan3.findCalibrator()
    
testSchedule.write(name="test.sch")

# Read an existing schedule.
testSchedule.read("c2914_follow_cal.sch")
# Output some things.
a = testSchedule.getScan(18)
print a.getSource()
print a.IF1().getFreq()

