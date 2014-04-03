from twisted.internet import reactor, defer, task
import random
from contextlib import contextmanager

def dummyLRP(choices, max_wait = 30):
    """
    dummy long running sort and select proces.
    """
    d = defer.Deferred()
    to_wait = random.uniform(0, max_wait)
    reactor.callLater(to_wait, d.callback, (random.choice(choices), to_wait,))
    return d

def printData(d):
    """
    simulated blocking Data handling function to be added as a callback:
    handles the data by printing the result
    """
    print d

class Queue_Worker(object):
    doing_work = 0
    def __init__(self, _i, queuein, process_fn, callback_fn = None, do_run = False):
        self._i = _i
        self.q = queuein
        self.running = do_run
        self.pfun = process_fn
        self.cbfn = callback_fn
        self.working = False
        if do_run:
            self.run()

    @defer.inlineCallbacks
    def run(self):
        self.running = True
        while self.running:
            my_data = yield self.q.get()
            mr = yield self.process_data(my_data)
            if self.cbfn:
                yield self.cbfn(mr)

    @defer.inlineCallbacks
    def process_data(self,my_data):
        with self.work_counter() as wc:
            mr = yield self.pfun(my_data)
        if self.cbfn:
            defer.returnValue(mr)
    
    @contextmanager
    def work_counter(self):
        Queue_Worker.doing_work += 1
        self.working = True
        yield True
        self.working = False
        Queue_Worker.doing_work -= 1

def reactor_manager(queues, pad_loops = 5):
    if all([len(my_queue.pending) == 0 for my_queue in queues]) and Queue_Worker.doing_work == 0:
        reactor.stop()
    else:
        print 'waiting:{0}, working:{1}'.format(sum([len(q.pending) for q in queues]), Queue_Worker.doing_work)

def main():
    #### set up and populate the input queue
    ip_queue = defer.DeferredQueue()
    for i in xrange(100):
        ip_queue.put(i)
    #### set up the output queue
    op_queue = defer.DeferredQueue()        
    #### start the queue length chceks to know when to stop the reactor
    task.LoopingCall(reactor_manager,(ip_queue, op_queue)).start(1, now=True)
    #### configure the input workers
    my_iws = [Queue_Worker(a,ip_queue,
        lambda x: dummyLRP('abcdefg', 30), 
        op_queue.put) for a in xrange(25)]
    #### configure and start the output worker
    Queue_Worker('output', op_queue, printData).run()
    #### start input workers
    for my_iw in my_iws:
        my_iw.run()
    #### get the whole thing going
    reactor.run()

if __name__ == '__main__':
    main()
    

