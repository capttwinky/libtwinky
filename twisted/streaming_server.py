#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
This is a sample implementation of a Twisted push producer/consumer system. It
consists of a TCP server which asks the user how many random integers they
want, and it sends the result set back to the user, one result per line,
and finally closes the connection.
"""

from sys import stdout
from random import randrange

from zope.interface import implements
from twisted.python.log import startLogging
from twisted.internet import interfaces, reactor, defer
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import inotify
from twisted.python import filepath

def mPrint(thing):
    print(thing)

def sleep(secs,cbfn = None):
    cbfn = cbfn if cbfn else lambda secs: mPrint("sleep:%i"%secs)
    d = defer.Deferred()
    d.callback = lambda secs: cbfn(secs)
    reactor.callLater(secs, d.callback(secs), None)
    return d

class Producer(object):
    """
    Send back the requested number of random integers to the client.
    """

    implements(interfaces.IPushProducer)

    def __init__(self, proto):
        self._proto = proto
        self._produced = 0
        self._paused = False

    def pauseProducing(self):
        """
        When we've produced data too fast, pauseProducing() will be called
        (reentrantly from within resumeProducing's sendLine() method, most
        likely), so set a flag that causes production to pause temporarily.
        """
        self._paused = True
        print 'Pausing connection from %s' % self._proto.transport.getPeer()

    def notify(self, filepath, mask):
        mstr =  ', '.join(inotify.humanReadableMask(mask))
        print "event %s on %s" % (mstr, filepath)
        self._proto.sendLine('%s' %mstr)



    def resumeProducing(self):
        """
        Resume producing integers.

        This tells the push producer to (re-)add itself to the main loop and
        produce integers for its consumer until the requested number of integers
        were returned to the client.
        """
        self._paused = False

        while not self._paused:
            print "ok"
            notifier = inotify.INotify()
            notifier.startReading()
            notifier.watch(filepath.FilePath("/home/joel/"), callbacks=[self.notify])

    def stopProducing(self):
        """
        When a consumer has died, stop producing data for good.
        """
        self._proto.transport.unregisterProducer()
        self._proto.transport.loseConnection()

class ServeRandom(LineReceiver):
    """
    Serve up random integers.
    """

    def connectionMade(self):
        """
        Once the connection is made we ask the client how many random integers
        the producer should return.
        """
        print 'Connection made from %s' % self.transport.getPeer()
        self.sendLine('start random feed?')

    def lineReceived(self, line):
        """
        This checks how many random integers the client expects in return and
        tells the producer to start generating the data.
        """
        count = int(line.strip())
        print 'Client requested %d random integers!' % count
        producer = Producer(self)
        self.transport.registerProducer(producer, True)
        producer.resumeProducing()

    def connectionLost(self, reason):
        print 'Connection lost from %s' % self.transport.getPeer()


startLogging(stdout)
factory = Factory()
factory.protocol = ServeRandom
reactor.listenTCP(1234, factory)
reactor.run()
