# example3.py
# Jamie Stevens
# Part of the ATCA scheduler Python library.

# This example shows how to create a simple schedule to follow up a ToO
# source but with 64 MHz zoom modes.

# Example 3:
# Suppose an event trigger has been received for a flaring magnetar at
# coordinates RA = 01:00:43.1, Dec = -72:11:33.8.
# You have decided to observe this position with the ATCA, at the same
# frequencies that are currently being observed.
# Unfortunately CABB is in 64 MHz zooms mode, so we need to use the zoom
# bands to get decent data.

# Include the library.
import cabb_scheduler as cabb

# Make a new schedule.
schedule = cabb.schedule()

# Add a scan to look at the magnetar's coordinates.
# We're going to use the current project's frequencies so we don't need to
# do any setup calibration. We can get those frequencies from MoniCA.
currentFreqs = cabb.monica_information.getFrequencies()

# This is where we set our project code; in this example we'll use
# the code C001 (although this wouldn't work for the rapid response
# mode).
# We'll also set it to be 20 minutes long, with Dwell mode.
scan1 = schedule.addScan(
    { 'source': "magnetar", 'rightAscension': "01:00:43.1", 'declination': "-72:11:33.8",
      'freq1': currentFreqs[0], 'freq2': currentFreqs[1], 'project': "C001",
      'scanLength': "00:20:00", 'scanType': "Dwell" }
)
# Add the 64 MHz zooms.
scan1.IF1().addZoom(
    { 'width': 16, 'freq': currentFreqs[0] }
)
scan1.IF2().addZoom(
    { 'width': 16, 'freq': currentFreqs[1] }
)
# Since we definitely want to get onto source as quickly as possible, we tell the
# library not to go to the calibrator first.
schedule.disablePriorCalibration()

# Request a list of nearby calibrators from the ATCA calibrator database.
calList = scan1.findCalibrator()

# Ask for the library to choose the best one for the current array. We first need to
# get the current array from MoniCA.
currentArray = cabb.monica_information.getArray()
# And pass this as the arggument to the calibrator selector.
bestCal = calList.getBestCalibrator(currentArray)
# This should choose 2353-686.
print "Calibrator chosen: %s, %.1f degrees away" % (bestCal['calibrator'].getName(),
                                                    bestCal['distance'])

# We add this calibrator to the schedule, attaching it to the scan it
# will be the calibrator for. We'll ask to observe the calibrator for 2
# minutes.
calScan = schedule.addCalibrator(bestCal['calibrator'], scan1, { 'scanLength': "00:02:00" })

# We want the schedule to run for about an hour, so we want another two copies
# of these two scans. Remembering that the library will take care of
# associating a calibrator to each source, we only need to copy the source
# scan.
for i in xrange(0, 2):
    schedule.copyScans([ scan1.getId() ])

# Tell the library that we won't be looping, so there will be a calibrator scan at the
# end of the schedule.
schedule.setLooping(False)
    
# We can write out the schedule now, to the file "c001_magnetar.sch".
schedule.write(name="c001_magnetar_64mhz.sch")
# This schedule should have 7 scans, with 2353-686 at scans 2, 4 and 6, and the
# magnetar at scan 1, 3 and 5.
