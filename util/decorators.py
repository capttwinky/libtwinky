#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  decorators.py
#  
#  this is a default description of this file
#  

def unittest_dev_wrapper(testfn):
    @wraps(testfn)
    def inner_fn(*args, **kwargs):
        print '\n{}\n{}\n'.format('*'*80,testfn.__name__)
        mret = testfn(*args, **kwargs)
        print '*'*80
        return mret
    return inner_fn
