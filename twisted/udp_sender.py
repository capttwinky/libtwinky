from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import sys, time
import random
import string

class HeartbeatSender(DatagramProtocol):
    def __init__(self, name, host, port):
        self.name = name
        self.loopObj = None
        self.host = host
        self.port = port
        self._count = 0
    
    @property
    def count(self):
        self._count += 1
        return self._count

    def startProtocol(self):
        # Called when transport is connected
        # I am ready to send heart beats
        self.loopObj = LoopingCall(self.sendHeartBeat)
        self.loopObj.start(2, now=False)

    def stopProtocol(self):
        "Called after all transport is teared down"
        pass

    def sendHeartBeat(self):
        self.transport.write("{}:{}".format(time.asctime(), ''.join(random.sample(string.letters, 12))), (self.host, self.port))
        print self.count



heartBeatSenderObj = HeartbeatSender("sender", "127.0.0.1", 8125)

reactor.listenUDP(0, heartBeatSenderObj)
reactor.run()
