#!/usr/bin/env python

import os,sys
from dModule import version

print "Setting up dmod v%s" % version

bashrc = os.path.join(os.environ['HOME'],'.bashrc')

f = open(bashrc,'a+')
lines = f.readlines()
for l in lines:
    if l.startswith('dmod() '):
        sys.exit(0)

f.write("""
dmod() {  DMODULECMD="/N/soft/rhel6/dmod/dModule.py";
 eval `${DMODULECMD} $*`
}
export -f dmod""")
f.close()

print "To use dmod, either start a new session or run 'source ~/.bashrc'"
