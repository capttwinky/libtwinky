#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import os
import contextlib
import shutil
import tempfile
import time

@contextlib.contextmanager
def file_locker(path_in, path_repl, locker_path = None):
    in_path = os.path.split(path_in)
    mask_file = os.path.join(path_repl, in_path[-1])
    if os.path.exists(mask_file):
        print 'copy {0} to locker'.format(mask_file)
        if locker_path is not None:
            tmp_dir = locker_path
        else:
            tmp_dir = tempfile.mkdtemp()
        tmp_file = os.path.join(tmp_dir, in_path[-1])
        shutil.copy2(mask_file, tmp_file)
    else:
        tmp_file = None
    print 'copy {0} to {1}'.format(path_in, mask_file)
    shutil.copy2(path_in, mask_file)
    yield path_in
    if tmp_file is not None:
        print 'replace {0} with locker copy'.format(mask_file)
        shutil.copy2(tmp_file, mask_file)
        shutil.rmtree(tmp_dir)
    else:
        print 'remove {0}'.format(mask_file)
        os.unlink(mask_file)

def main():
    import sys
    path_in, path_repl = sys.argv[1:3]
    with file_locker(path_in, path_repl) as myfl:
        while True:
            minput = raw_input("press <enter> to quit")
            break
    print "Done!"

if __name__ =='__main__':
    main()
