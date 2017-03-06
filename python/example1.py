# example1.py
# Jamie Stevens
# Part of the ATCA scheduler Python library.

# This example shows how to create a simple schedule to follow up a ToO
# source.

# Example 1:
# Suppose an event trigger has been received for a flaring magnetar at
# coordinates RA = 01:00:43.1, Dec = -72:11:33.8.
# You have decided to observe this position with the ATCA, in the 4cm
# band.

# Include the library.
import cabb_scheduler as cabb

# Make a new schedule.
schedule = cabb.schedule()

# Add a scan to look at the magnetar's coordinates.
# This is where we set our project code; in this example we'll use
# the code C001 (although this wouldn't work for the rapid response
# mode).
# We'll also set it to be 20 minutes long, with Dwell mode.
scan1 = schedule.addScan(
    { 'source': "magnetar", 'rightAscension': "01:00:43.1", 'declination': "-72:11:33.8",
      'freq1': 5500, 'freq2': 9000, 'project': "C001", 'scanLength': "00:20:00", 'scanType': "Dwell" }
)

# Request a list of nearby calibrators from the ATCA calibrator database.
calList = scan1.findCalibrator()

# Ask for the library to choose the best one.
bestCal = calList.getBestCalibrator()
# This should choose 2353-686.
print "Calibrator chosen: %s, %.1f degrees away" % (bestCal['calibrator'].getName(),
                                                    bestCal['distance'])

# We add this calibrator to the schedule, attaching it to the scan it
# will be the calibrator for. We'll ask to observe the calibrator for 2
# minutes.
schedule.addCalibrator(bestCal['calibrator'], scan1, { 'scanLength': "00:02:00" })

# We can write out the schedule now, to the file "c001_magnetar.sch".
schedule.write(name="c001_magnetar.sch")
