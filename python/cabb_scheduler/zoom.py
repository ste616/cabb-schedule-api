# A zoom band.
import errors

class zoom:
    def __init__(self, parent):
        self.__parent = parent
        self.__details = { 'channel': 1, 'enabled': False, 'group': -1 }

    def isEnabled(self):
        return self.__details['enabled']

    def enable(self):
        self.__details['enabled'] = True
        return self

    def disable(self):
        self.__details['enabled'] = False
        return self

    def getGroup(self):
        return self.__details['group']

    def setGroup(self, group=None):
        if group is not None:
            self.__details['group'] = group
        return self
    
    def getChannel(self):
        return self.__details['channel']

    def setChannel(self, chan=None):
        channelWidth = parent.getChannelWidth()
        nChannels = 2048 / channelWidth
        if chan is not None:
            if (chan < 1) or (chan > (nChannels * 2) + 1):
                raise ZoomError("Specified zoom channel is not in the band.")
            else:
                self.__details['channel'] = chan
        return self
    
    def setFreq(self, freq=None):
        sideband = self.__parent.getSideband()
        channelWidth = self.__parent.getChannelWidth()
        nChannels = 2048 / channelWidth
        centreFreq = self.__parent.getFreq()
        if freq is not None:
            rChan = int(round((2 / (sideband * channelWidth)) * ((sideband * nChannels * channelWidth) / 2 + freq - centreFreq) + 1))
            if (rChan < 1) or (rChan > (nChannels * 2) + 1):
                raise ZoomError("Specified zoom frequency is not in the band.")
            else:
                self.setChannel(rChan)
        return self

    def getFreq(self):
        sideband = self.__parent.getSideband()
        channelWidth = self.__parent.getChannelWidth()
        nChannels = 2048 / channelWidth
        centreFreq = self.__parent.getFreq()
        centreZoomFreq = centreFreq - (sideband * nChannels * channelWidth) / 2 + (sideband * self.getChannel() * channelWidth) / 2
        return centreZoomFreq
