# A schedule is a collection of scans, so the schedule class
# doesn't do much. But we do keep track of certain constants.

class schedule:
    def __init__(self):
        # This is the list of scans, in order.
        self.scans = []
        
