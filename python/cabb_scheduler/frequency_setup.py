# A frequency setup.
from cabb_scheduler.zoom import zoom
import cabb_scheduler.errors

class frequency_setup:
    def __init__(self, parent):
        self.__parent = parent
        # Some valid and necessary defaults.
        self.__setupDetails = { 'continuumCentre': 2100, 'channelBandwidth': 1,
                                'zooms': [] }
        # Assign all the zooms.
        for i in range(0, 16):
            self.__setupDetails['zooms'].append(zoom(self))

    def __frequencyToBand(self, cfreq=None):
        # Return the band that would satisfy the specified continuum centre frequency.
        if cfreq is None:
            cfreq = self.__setupDetails['continuumCentre']

        if cfreq is not None:
            if (cfreq >= 1728 and cfreq <= 2882):
                return "16cm"
            elif (cfreq >= 4928 and cfreq <= 10928):
                return "4cm"
            elif (cfreq >= 16001 and cfreq <= 25472):
                return "15mm"
            elif (cfreq >= 30001 and cfreq <= 49999):
                return "7mm"
            elif (cfreq >= 82501 and cfreq <= 117699):
                return "3mm"
        return None

    def getFrequencyBand(self):
        return self.__frequencyToBand()
    
    def getFreq(self):
        return self.__setupDetails['continuumCentre']

    def getChannelWidth(self):
        return self.__setupDetails['channelBandwidth']

    def getSideband(self):
        return self.__parent.getSideband()
        
    def getZoom(self, idx=None):
        if idx is not None and idx >= 0 and idx < 16:
            if (self.__setupDetails['zooms'][idx].isEnabled):
                return self.__setupDetails['zooms'][idx]
        return None

    def getNZooms(self):
        # Return the number of zoom channels currently in use.
        tw = 0
        for i in range(0, len(self.__setupDetails['zooms'])):
            if (self.__setupDetails['zooms'][i].isEnabled()):
                tw += 1
        return tw

    def getZoomGroups(self):
        # Return a list of all the zoom groups we have.
        groups = []
        for i in range(0, len(self.__setupDetails['zooms'])):
            if (self.__setupDetails['zooms'][i].isEnabled):
                g = self.__setupDetails['zooms'][i].getGroup()
                if g not in groups:
                    groups.append(g)
        return groups

    def setZoomChannel(self, zoomnum=None, chan=None):
        # We set a particular zoom to a particular channel.
        # This gets used a lot during load.
        if (zoomnum is None or zoomnum < 1 or zoomnum > 16):
            raise ZoomError("Unable to set zoom information.")
        if (chan is None):
            raise ZoomError("Channel number not supplied while setting zoom info.")
        z = self.__setupDetails['zooms'][zoomnum - 1]
        if (chan == 0):
            # This means disable this zoom.
            z.disable()
        else:
            z.setChannel(chan)
            z.enable()

    def getZoomChannel(self, zoomnum):
        if ((zoomnum is not None) and (zoomnum >= 1) and (zoomnum <= 16)):
            z = self.__setupDetails['zooms'][zoomnum - 1]
            if (z.isEnabled()):
                return self.__setupDetails['zooms'][zoomnum - 1].getChannel()
            else:
                return 0
        else:
            raise ZoomError("Valid zoom number not supplied.")
            
    def getAllZooms(self):
        zobj = {}
        for i in range(1, len(self.__setupDetails['zooms']) + 1):
            pz = self.getZoomChannel(i)
            if pz != 0:
                zobj['zoom%d' % i] = pz
        return zobj
    
    def addZoom(self, options=None):
        # Check we don't already have all the zooms.
        nZooms = self.getNZooms()
        if nZooms > 16:
            raise ZoomError("All zooms have already been allocated.")
        if (options is not None) and ('width' in options):
            if (options['width'] + nZooms) > 16:
                raise ZoomError("Cannot allocate more than 16 zooms.")
        # Work out which group we will be.
        cgroups = self.getZoomGroups()
        ngroup = max(cgroups)
        # Work out which channel will be the "centre" channel.
        cchan = 1
        sb = self.getSideband()
        w = 1
        if (options is not None) and ('width' in options):
            w = options['width']
            if ((w % 2) == 0):
                # Even width.
                cchan = w / 2
                if (sb > 0):
                    # USB
                    cchan += 1
            else:
                # Odd width.
                cchan = (w + 1) / 2
        # We need to work out which zoom channel corresponds to the first zoom.
        zchan = -1
        # Are we setting the frequency?
        if (options is not None) and ('freq' in options):
            achan = nZooms + (cchan - 1)
            self.__setupDetails['zooms'][achan].setFreq(options['freq'])
            # Now get the zoom channel number for this, and from this work out the
            # first zoom channel.
            zchan = self.__setupDetails['zooms'][achan].getChannel() - (cchan - 1)
        elif (options is not None) and ('chan' in options):
            zchan = options['chan'] - (cchan - 1)
        # Now go through all the zooms and set their channel number and group.
        for i in range(0, w):
            achan = nZooms + i
            self.__setupDetails['zooms'][achan].setChannel(zchan + i)
            self.__setupDetails['zooms'][achan].setGroup(ngroup)
            self.__setupDetails['zooms'][achan].enable()
        return self
    
    def setFreq(self, cfreq=None):
        # Set the continuum centre-channel frequency, in MHz.
        # We also check whether the setting is valid.
        if cfreq is not None:
            if self.__frequencyToBand(cfreq) is not None:
                # Valid frequency.
                self.__setupDetails['continuumCentre'] = cfreq
            else:
                raise errors.FrequencyError("Specified continuum centre frequency is not achievable.")
        return self

    def setChannelWidth(self, bandw=None):
        # Set the channel width of each continuum channel, in MHz.
        if bandw is not None:
            if bandw == 1 or bandw == 64:
                # The only two supported widths.
                self.__setupDetails['channelBandwidth'] = bandw
            else:
                raise errors.FrequencyError("Specified continuum channel width is unsupported.")
        return self

    def classify(self):
        # Return a classification of this setup, to make it easy to
        # check if two IFs are compatible.
        c = { 'band': "", 'corrConfigs': [] }
        c['band'] = self.__frequencyToBand(self.__setupDetails['continuumCentre'])
        # Add all the compatible CABB configurations.
        n = self.getNZooms()
        if (self.__setupDetails['channelBandwidth'] == 1 and
            n == 0):
            # 1 MHz continuum, no zooms necessary.
            c['corrConfigs'].append("1M")
            c['corrConfigs'].append("1MZ")
            c['corrConfigs'].append("1M64MZ")
        elif (self.__setupDetails['channelBandwidth'] == 1 and
              n > 0):
            # 1 MHz continuum, zooms required.
            c['corrConfigs'].append("1MZ")
        elif (self.__setupDetails['channelBandwidth'] == 64):
            # 64 MHz continuum, zooms required.
            c['corrConfigs'].append("64MZ")
            c['corrConfigs'].append("1M64MZ")
        return c
