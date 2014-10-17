#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  git.py
#  
#  this is a default description of this file
#  
#  © 2014-09-26 tinyco 
#      Joel McGrady <jmcgrady@tinyco.com>
#  


from dulwich import repo



def main():
    rep_obj = repo.Repo('.')
    local_branches = [k for k in rep_obj.refs.keys() if 'heads' in k]
    for item in local_branches:
        if raw_input("keep branch {}? (y/n)/n".format(item))=='n':
            rep_obj.refs.remove_if_equals(item, None)
