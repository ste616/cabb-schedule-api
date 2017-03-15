# A library to handle dealing with ATCA MoniCA points.
from requests import Session
import json
import errors

class monicaPoint:
    def __init__(self, info={}):
        self.value = None
        self.description = None
        self.pointName = None
        self.updateTime = None
        self.errorState = None
        if "value" in info:
            self.setValue(info['value'])
        if "description" in info:
            self.setDescription(info['description'])
        if "pointName" in info:
            self.pointName = info['pointName']
        if "updateTime" in info:
            self.setUpdateTime(info['updateTime'])
        if "errorState" in info:
            self.setErrorState(info['errorState'])

    def getPointName(self):
        return self.pointName
            
    def setValue(self, value=None):
        if value is not None:
            self.value = value
        return self

    def getValue(self):
        return self.value

    def setDescription(self, description=None):
        if description is not None:
            self.description = description
        return self

    def getDescription(self):
        return self.description
    
    def setUpdateTime(self, updateTime=None):
        if updateTime is not None:
            self.updateTime = updateTime
        return self

    def getUpdateTime(self):
        return self.updateTime
    
    def setErrorState(self, errorState=None):
        if errorState is not None:
            self.errorState = errorState
        return self

    def getErrorState(self):
        return self.errorState

class monicaServer:
    def __init__(self, info={}):
        self.serverName = "monhost-nar"
        self.protocol = "http"
        self.webserverName = "www.narrabri.atnf.csiro.au"
        self.webserverPath = "cgi-bin/obstools/web_monica/monicainterface_json.pl"
        self.points = []
        if "serverName" in info:
            self.serverName = info['serverName']
        if "protocol" in info:
            self.protocol = info['protocol']
        if "webserverName" in info:
            self.webserverName = info['webserverName']
        if "webserverPath" in info:
            self.webserverPath = info['webserverPath']

    def addPoint(self, pointName=None):
        if pointName is not None:
            npoint = monicaPoint({ 'pointName': pointName })
            self.points.append(npoint)
        return self
    
    def addPoints(self, points=[]):
        if len(points) > 0:
            for i in xrange(0, len(points)):
                self.addPoint(points[i])
        return self

    def getPointByName(self, pointName=None):
        if pointName is not None:
            for i in xrange(0, len(self.points)):
                if (self.points[i].getPointName() == pointName):
                    return self.points[i]
        return None

    def __comms(self, data=None):
        if data is None:
            return None

        session = Session()
        url = self.protocol + "://" + self.webserverName + "/" + self.webserverPath
        print data
        postResponse = session.post( url=url, data=data )
        print postResponse.text
        return json.loads(postResponse.text)

    def updatePoints(self):
        allPointNames = [ p.getPointName() for p in self.points ]
        data = { 'action': "points", 'server': self.serverName,
                 'points': ";".join(allPointNames) }
        response = self.__comms(data)
        if response is not None and "pointData" in response:
            for i in xrange(0, len(response['pointData'])):
                point = self.getPointByName(response['pointData'][i]['pointName'])
                point.setValue(response['pointData'][i]['value'])
                point.setUpdateTime(response['pointData'][i]['time'])
                point.setErrorState(not bool(response['pointData'][i]['errorState']))
            return True
        return False

serverInstance = None

def initialiseServerInstance(*args):
    global serverInstance
    if serverInstance is None:
        serverInstance = monicaServer()
    return serverInstance

def getArray(*args):
    server = initialiseServerInstance()
    server.addPoint("site.misc.array").updatePoints()
    return server.getPointByName("site.misc.array").getValue()

def getFrequencies(*args):
    server = initialiseServerInstance()
    server.addPoints([ "site.misc.obs.freq1", "site.misc.obs.freq2" ]).updatePoints()
    freqs = [ float(server.getPointByName("site.misc.obs.freq1").getValue()), float(server.getPointByName("site.misc.obs.freq2").getValue()) ]
    return freqs
