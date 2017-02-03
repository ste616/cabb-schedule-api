# A frequency setup.
from zoom import zoom
import errors

class frequency_setup:
    def __init__(self, parent):
        self.__parent = parent
        # Some valid and necessary defaults.
        self.__setupDetails = { 'continuumCentre': 2100, 'channelBandwidth': 1,
                                'zooms': [] }
        # Assign all the zooms.
        for i in xrange(0, 16):
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
        for i in xrange(0, len(self.__setupDetails['zooms'])):
            if (self.__setupDetails['zooms'][i].isEnabled):
                tw += 1
        return tw
    
    def addZoom(self, options=None):
        # Check we don't already have all the zooms.
        nZooms = self.getNZooms()
        if nZooms >= 16:
            raise ZoomError("All zooms have already been allocated.")
        if (options is not None) and ('width' in options):
            if (options['width'] + nZooms) > 16:
                raise ZoomError("Cannot allocate more than 16 zooms.")
        self.__setupDetails['zooms'].append(zoom(self))
        if (options is not None) and ('width' in options):
            self.__setupDetails['zooms'][-1].setWidth(options['width'])
        if (options is not None) and ('freq' in options):
            self.__setupDetails['zooms'][-1].setFreq(options['freq'])
        if (options is not None) and ('chan' in options):
            self.__setupDetails['zooms'][-1].setChannel(options['chan'])
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
        if (self.__setupDetails['channelBandwidth'] == 1 and
            len(self.__setupDetails['zooms']) == 0):
            # 1 MHz continuum, no zooms necessary.
            c['corrConfigs'].append("1M")
            c['corrConfigs'].append("1MZ")
            c['corrConfigs'].append("1M64MZ")
        elif (self.__setupDetails['channelBandwidth'] == 1 and
              len(self.__setupDetails['zooms']) > 0):
            # 1 MHz continuum, zooms required.
            c['corrConfigs'].append("1MZ")
        elif (self.__setupDetails['channelBandwidth'] == 64):
            # 64 MHz continuum, zooms required.
            c['corrConfigs'].append("64MZ")
            c['corrConfigs'].append("1M64MZ")
        return c
