# This program is to test the Python library functionality.

import cabb_scheduler as cabb

# Make a new schedule.
testSchedule = cabb.schedule()
scan1 = testSchedule.addScan({ 'source': "1934-638", 'rightAscension': "19:39:25.026" })
scan2 = testSchedule.addScan()
scan3 = testSchedule.addScan({ 'source': "0823-500", 'rightAscension': "08:25:26.869" })
scan2.setSource("0537-441").setRightAscension("05:38:50.362")
testSchedule.write(name="test.sch")
