#!/usr/bin/env python
from Queue import Queue
from threading import Thread
from time import time, sleep
from subprocess import Popen, PIPE

class HostRangeGenerator(object):
    def __init__(self, lstIn):
        self.myList = [range(256) if x =="*" else [x] if hasattr(x,'real') else x for x in lstIn]
        self.A, self.B, self.C, self.D = self.myList

    def hRange(self,myDiv = 1):
        return range(len(self)/myDiv)

    def __len__(self):
        return len(self.A)*len(self.B)*len(self.C)*len(self.D)

    def __iter__(self):
        '''generates a range of host names based on the 4 part integer list input'''
        for myA in self.A:
            for myB in self.B:
                for myC in self.C:
                    for myD in self.D:
                        yield "%i.%i.%i.%i"%(myA, myB, myC, myD)

class ThreadReport(Thread):
    """Threaded OS command which returns to a queue"""
    def __init__(self, queueIn, queueOut):
        Thread.__init__(self)
        self.get_queue = queueIn
        self.put_queue = queueOut

    def _get(self):
        return self.get_queue.get()
    def _done(self):
        self.get_queue.task_done()
    def _put(self,toPut):
        return self.put_queue.put(toPut)

    def run(self):
        while True:
            myCommand = self._get() #maybe command should consist of a popen command list and a callback for that command
            cmdLst = myCommand[0]
            fnXf = myCommand[1]
            try:
                pipe = Popen(cmdLst, stdout=PIPE)
                myOut = fnXf(pipe.communicate()[0])
            except Exception as e:
                print "%s, %s"%(",".join(cmdLst), str(fnXf))
                myOut = None
            self._done()
            self._put(myOut)

class ThreadPing(ThreadReport):
    """Threaded Url Grab"""
    def run(self):
        while True:
            myCommand = self._get() #maybe command should consist of a popen command list and a callback for that command
            if not myCommand or len(myCommand) != 2 or type(myCommand)!= type([]):
                print "%r"%myCommand
                raise Exception("command: %r"%myCommand)
            cmdLst = myCommand[0]
            fnXf = myCommand[1]
            #print cmdLst[-1]
            myOut = False
            thisCounter = 0
            while not myOut and thisCounter < 10:
                try:
                    thisCounter += 1
                    if type(cmdLst) != type([]):
                        raise Exception("need a list")
                    pipe = Popen(cmdLst, stdout=PIPE)
                    myOut = fnXf(pipe.communicate()[0])
                except Exception as e:
                    print "%s, %s"%(",".join(cmdLst), str(fnXf))
                    raise e
                    myOut = None
                    sleep(2000)
            self._done()
            if myOut:
                self._put(myOut)

class myReport(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.total = 0
        self.lstOut = []

    def run(self):
        while True:
            try:
                lstOut = self.queue.get()
                self.total += 1
                if lstOut:
                        self.lstOut.append([lstOut[0],lstOut[3]])

            except Exception as e:
                print lstOut
            self.queue.task_done()

def doPing(ipList,q_hosts,q_report):
    myHosts = HostRangeGenerator(ipList)
    dThreads = len(myHosts) if len(myHosts) < 1024 else 1024
    print("Pinging %i Hosts\nusing %i threads:"%(len(myHosts),dThreads))
    #spawning pools of threads, and passing them the queues
    for i in range(dThreads):
        t = ThreadPing(q_hosts,q_report)
        t.setDaemon(True)
        t.start()
    #populate queue with data -if this were expensive (i/o bound), having the ability to work on the queue while it is populated is nice!
    for myInt, myhost in enumerate(myHosts):
        q_hosts.put([['ping','-c 5', myhost], lambda x: x.split("\n")])
    #now that is going, we only need one thread for summing
    myRep = myReport(q_report)
    myRep.setDaemon(True)
    myRep.start()
    #wait on the queues until everything has been processed
    q_hosts.join()
    q_report.join()
    return dThreads, myRep.total, myRep.lstOut

def getPings(ipLst):
    #build the Queues
    q_hosts = Queue()
    q_report = Queue()
    start = time()
    dThreads, lTotal, lstOut = doPing(ipLst,q_hosts,q_report)
    eTime = time() - start
    for lstLine in lstOut:
        if lstLine:
            if "100% packet loss" not in lstLine[1] and "Host Unreachable" not in lstLine[1]:
                print "<---->"
                print "%s"%("\n".join(lstLine))
                print ">-----<"
    print "Elapsed Time: %.02f seconds\nfor %i pings on %i hosts\nusing %i threads"%(eTime,lTotal*5,lTotal,dThreads)

if __name__ == '__main__':
    #getPings([10,'*',[0,1,2],'*']) #196608 hosts
    #getPings([192,168,'*','*']) #65536 hosts
    getPings([192,168,2,'*']) #256 hosts
    #getPings([192,168,[1,2,100],'*']) #768 hosts
    #getPings([10,0,[2,1],'*']) #512 hosts
