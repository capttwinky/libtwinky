#!/usr/bin/env python

import sys
import os
import subprocess
import json
import shlex

MODULE_SETTINGS = type("MODULE_STATE", (object,), {
    "base_dir": "/home/jmcgrady/ssh_mounts",
    "config_file": None,
    "mounts": None,
})


ssh_cmd = "ssh -A -t -o 'StrictHostKeyChecking=no' "


def do_mount(target_host, mtpoint, slink = None):
    mtpoint = "{0}/{1}".format(MODULE_SETTINGS.base_dir, mtpoint)
    if not os.path.exists(mtpoint):
        os.makedirs(mtpoint)
    elif os.listdir(mtpoint):
        raise Exception("mount point not empty: {0}".format(mtpoint))
    subprocess.Popen(shlex.split("sshfs -o ssh_command="
        "'{cmd}' ubuntu@{host}:/ {point}".format(
        cmd = ssh_cmd,
        host = target_host,
        point = mtpoint)))
    if slink:
        sym_link =  "{0}/{1}".format(MODULE_SETTINGS.base_dir, slink)
        if not os.path.exists(sym_link):
            os.symlink(mt_point, sym_link)

def clear_entry(ip_address = None, link = None):
    if not (ip_address or link):
        raise Exception("must give ip_address or link to remove")
    if ip_address:
        if ip_address in MODULE_SETTINGS.mounts:
            link = MODULE_SETTINGS.mounts[ip_address]
        else:
            raise Exception("ip address {0} not found".format(ip_address))
    else:
        MODULE_SETTINGS.reverse = {v:k for k,v in MODULE_SETTINGS.mounts.items()}
        if link not in MODULE_SETTINGS.reverse:
            raise Exception("link {0} not found".format(link))
        ip_address = MODULE_SETTINGS.reverse[link]
    
    l_file = '{0}/{1}'.format(MODULE_SETTINGS.base_dir, link)
    m_point ='{0}/{1}'.format(MODULE_SETTINGS.base_dir, ip_address.replace('.','-'))
    
    #~ print l_file
    if os.path.exists(l_file):
        os.unlink(l_file)
    else:
        raise Exception("{0} not found".format(l_file))
    #~ print m_point
    if os.path.exists(m_point):
        if not os.listdir(m_point):
            os.rmdir(m_point)
        else:
            raise Exception("{0} not empty".format(m_point))
    else:
        raise Exception("{0} not found".format(m_point))
    #~ print os.path.exists(m_point)
    
    del(MODULE_SETTINGS.mounts[ip_address])
    save_settings(MODULE_SETTINGS.mounts)
    
def load_settings():
    if os.path.exists(MODULE_SETTINGS.config_file):
        with open(MODULE_SETTINGS.config_file) as ofile:
            return json.load(ofile)

def save_settings(d_sets):
    with open(MODULE_SETTINGS.config_file, 'w') as ofile:
        ofile.write(json.dumps(d_sets))

def do_setup():
    MODULE_SETTINGS.config_file = '{0}/sshmount.json'.format(
        MODULE_SETTINGS.base_dir)
    MODULE_SETTINGS.mounts = load_settings() or {}

def main():
    ## if there are dots, it's a hostname, if not, it's a label
    do_setup()
    if '.' in sys.argv[1]:
        target_host = sys.argv[1]
        if len(sys.argv) == 3:
            slink = sys.argv[2]
            
            MODULE_SETTINGS.mounts[target_host] = slink
            save_settings(MODULE_SETTINGS.mounts)
        else:
            slink = None
    else:
        slink = sys.argv[1]
        for target_host, link_name in MODULE_SETTINGS.mounts.iteritems():
            if slink == link_name:
                break 
        else:
            import pdb; pdb.set_trace()
            raise Exception("{0} not found in labels".format(slink))
    do_mount(target_host, target_host.replace('.','-'), slink)
    print "did {0} ok".format(sys.argv[1])

if __name__ == '__main__':
    main()
