# A scan has several required fields.

class scan:
    def __init__(self):
        # We put all the properties of the scan in a dictionary.
        self.scanDetails = { 'source': "",
                             'rightAscension': "",
                             'declination': "",
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
                             'setupF1': None,
                             'setupF2': None }
        
