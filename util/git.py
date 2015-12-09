#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


from dulwich import repo



def main():
    rep_obj = repo.Repo('.')
    local_branches = [k for k in rep_obj.refs.keys() if 'heads' in k]
    for item in local_branches:
        if raw_input("keep branch {}? (y/n)/n".format(item))=='n':
            rep_obj.refs.remove_if_equals(item, None)
