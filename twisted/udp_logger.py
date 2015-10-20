#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  udp_logger.py
#  
#  log udp packets
 

import sys

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

LISTEN_PORT = 8125
LOG_TARGET = None


class Echo(DatagramProtocol):

    def datagramReceived(self, data, (host, port)):
        log.msg("{}:{} {}".format(host, port, data))

def port_reporter(listener):
    log.msg('{0} listening for {1.type} at {1.host}:{1.port}'.format(
        listener.protocol.__class__.__name__, listener.getHost()))

def setup_logs(log_target = None):
    if log_target is None:
        log_out = sys.stdout
    else:
        log_out = open(log_target, 'w') 
    return log_out

log.startLogging(setup_logs(LOG_TARGET))
udp_listener = reactor.listenUDP(LISTEN_PORT, Echo())
reactor.callWhenRunning(port_reporter, udp_listener)
reactor.run()
