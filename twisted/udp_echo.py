#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  udp_echo.py
#  
#  echo udp packets
#  
#  © 2014-05-08 tinyco 
#      Joel McGrady <jmcgrady@tinyco.com>
#  

LISTEN_PORT = 8125

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import time

class Echo(DatagramProtocol):

    def datagramReceived(self, data, (host, port)):
        print "{} received {} from {}:{}".format(time.asctime(), data, host, port)
        self.transport.write(data, (host, port))

def port_reporter(listener):
    print '='*80
    print '{0} listening for {1.type} at {1.host}:{1.port}'.format(
        listener.protocol.__class__.__name__, listener.getHost())
    print '='*80

udp_listener = reactor.listenUDP(LISTEN_PORT, Echo())
reactor.callWhenRunning(port_reporter, udp_listener)
reactor.run()
