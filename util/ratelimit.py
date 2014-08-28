#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ratelimit.py
#  
#  two functions which throttle call frequency:
#
#  TimerLimiter := throttle arbitrary function calls by #calls/time
#
#  BackoffLimiter := throttle calls made by the requests library specifically,
#   increasing wait time between successive attempts
#  
#  © 2014-05-09 tinyco 
#      Joel McGrady <jmcgrady@tinyco.com>

import time
import functools

from requests.exceptions import ConnectionError, HTTPError

logger = logging.logging.get_logger(__name__)

class TimerLimiter(object):
    '''throttle calls to an arbitrary function
    two ways to use:
    1) as a wrapper
      def inner_fn():
        ...
      my_fn = TimerLimiter(inner_fn, 100, 20)
    
    2) as a decorator:
      my_dec = functools.partial(TimerLimiter, call_number=100, time_period=20)
      
      @my_dec
      def inner_fn():
        ...
    
    both examples create a function which is limited to 100 calls in 20 seconds
    
    '''
    
    def __init__(self, call_function, call_number, time_period):
        '''
        @param call_function: function to be rate limited
        @param call_number: the maximum amount of calls per unit of time
        @param time_period: number of seconds in the unit of time
        '''
        self._fn = call_function
        self._calls = call_number
        self._period = time_period
        self._start = 0
        self._call_count = 0
        self.make_wrapper(self._fn)

    def make_wrapper(self, fn_in):
        @functools.wraps(fn_in)
        def inner_fn(*args, **kwargs):
            e_time = time.time()-self._start
            if e_time >= self._period:
                self._call_count = 0
                self._start = time.time()
            if self._call_count >= self._calls:
                pause_duration = self._period - e_time
                if logger: logger.debug(
                    '{0} in {1} waiting for {2}'.format(
                        self._call_count, e_time, pause_duration))
                time.sleep(pause_duration)
            mret = self._fn(*args, **kwargs)
            self._call_count += 1
            return mret
        self._wrapped = inner_fn

    def __call__(self, *args, **kwargs):
        return self._wrapped(*args, **kwargs)


class BackoffLimiter(object):
    '''throttle calls made via the requests library
    wrapped functions should take the form of
      def inner_fn():
        mreq = requests.get(....)
        mreq.raise_for_status()
        return mreq.content
    
    the significant step is mreq.raise_for_status() which returns the 
    specific type of errors we catch here
    
    three ways to use:
    1) as a wrapper:
      my_fn = BackoffLimiter(inner_fn, 0, 20, 300, 200)
      
        makes a funciton which:
            1) will backoff 1 second for each failure, starting with 1 second
            2) will pause at most 20 seconds between attempts
            3) will raise an exception if it runs for more than 300 seconds
            4) will raise an exception if it makes more than 200 attempts
    
    2) as a decorator:
        @BackoffLimiter
        def inner_fn():...
        
        makes a function which:
            1) will backoff 1 second for each failure, starting with 1 second
            2) will pause an unlimited number of seconds between each run
            3) will not raise an exception based on entire duration of run
            4) will not raise an exception based on the total number of attempts
    
    3) as a decorator via functools.partial:
      my_dec = functools.partial(BackoffLimiter, reset=30, timeout=1000)
      
      @my_dec
      def inner_fn():
        ...
        makes a function which:
            1) will backoff 1 second for each failure, starting with 1 second
            2) will pause at most 30 seconds between each run
            3) will raise an exception if it runs for more than 1000 seconds
            4) will not raise an exception based on the total number of attempts
    '''

    def __init__(self, call_function, initial_pause=0, reset=None, timeout=None, max_retries=None):
        '''
        @pram call_function : callable, function to rate limit
        @param initial_pause : int, minimum wait time between runs in seconds
        @param reset: int, if we sleep for longer than this number of seconds, reset the backoff
        @param timeout: int, terminate run if it takes more seconds than this
        @param max_retries: int, terminate run if there are more tries than this
        '''
        self._start = time.time()
        self._fn = call_function
        self._ibk = initial_pause
        self._backoff = initial_pause
        self._timeout = self._start + timeout if timeout else None
        self._reset = reset or 0
        self._max_retries = max_retries
        self._tries = 0
        self.make_wrapper(self._fn)

    def make_wrapper(self, fn_in):
        @functools.wraps(fn_in)
        def inner_fn(*args, **kwargs):
            if self._timeout and time.time() >= self._timeout:
                raise Exception("timeout: {0} seconds".format(self._timeout-self._start))
            self._tries += 1
            try:
                mret = self._fn(*args, **kwargs)
                self._tries = 0
                self._backoff = self._ibk
            except (ConnectionError, HTTPError) as e:
                if self._max_retries and self._tries >= self._max_retries:
                    raise Exception("max retries exceeded: {0}".format(self._max_retries))
                self._backoff += 1
                if logger: logger.error("{0} waiting {1}".format(
                    e.message, self._backoff))
                time.sleep(self._backoff)
                if self._reset and self._backoff >= self._reset:
                    self._backoff = self._ibk
                return inner_fn(*args, **kwargs)
            return mret
        self._wrapped = inner_fn

    def __call__(self, *args, **kwargs):
        return self._wrapped(*args, **kwargs)
