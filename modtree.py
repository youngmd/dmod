#!/usr/bin/env python
import os,sys
import subprocess

def modcmds(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    outlines = err.splitlines()
    return outlines

def get_mod_reqs(modname):
    cmd = 'module show %s' % modname
    outlines = modcmds(cmd)
    deps = []
    cons = []
    for l in outlines:
        if not l.startswith('prereq') or l.startswith('conflict'):
            continue
        else:
            vals = l.split()
            if vals[0] == 'prereq':
                for i in vals[1:]:
                    deps.append(i)
            if vals[0] == 'conflict':
                for i in vals[1:]:
                    cons.append(i)
    return [deps, cons]

cmd = "module -t avail"
outlines = modcmds(cmd)

mods = {}
for l in outlines:
    if l.strip().endswith(':'):
        modgroup = l.strip().split('/')[-1]
        continue
    else:
        modname = l.strip()
        t = get_mod_reqs(l)
        d = {'deps':t[0], 'cons':t[1], 'group':modgroup}
        mods[modname] = d

print mods