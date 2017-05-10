#!/usr/bin/env python

import os, sys
import subprocess
#import warnings
#warnings.filterwarnings("ignore")

version = "0.2"

def modcmds(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    outlines = err.decode('ascii').splitlines()
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

def update_resolved(resolved, newmods):
    for i in newmods:
        if i not in resolved:
            resolved.append(i)
    return resolved

def resolve_deps(mods, resolved = []):
    for i in mods:
        d2, cons = get_mod_reqs(i)
        if len(d2) == 0:
            resolved = update_resolved(resolved, [i])
        else:
            resolved = update_resolved(resolve_deps(d2, resolved), resolved)
            resolved = update_resolved(resolved, [i])
    return resolved

def get_loaded():
    cmd = 'module -t list'
    outlines = modcmds(cmd)

    loaded = []
    for l in outlines:
        if l.startswith("Currently"):
            continue
        else:
            loaded.append(l.strip())
    return loaded

def exact_mod(modname):
    cmd = "module -v show %s" % modname
    outlines = modcmds(cmd)
    for l in outlines:
        if modname in l:
            if l.strip().endswith(modname+":"):
                return True
            else:
                return False
    raise Exception('Module requested not found by module system: %s' % modname)

def load(modname, loaded=get_loaded()):
    exact = exact_mod(modname)
    for l in loaded:
        if exact:
            if l == modname:
                return
        else:
            if modname in l:
                return
    print 'module load %s; ' % modname
    #os.system(cmd)
    return

def get_all_modules():
    cmd = "module -t avail"
    outlines = modcmds(cmd)

    modules = []
    for l in outlines:
        if l.strip().endswith(':'):
            continue
        else:
            if "(default)" in l:
                l = l.strip("(default)")
            modules.append(l.strip())
    return modules

def search_mods(modname):
    modules = get_all_modules()
    count = 0
    for i in modules:
        if modname.lower() in i.lower():
            print "echo '%s';" % i
            count += 1
    if not count:
        print 'echo ; echo No matches found for %s!;' % modname
        from fuzzywuzzy import process
        bestmatch = process.extractBests(modname, modules, score_cutoff=60, limit=10)
        if len(bestmatch) > 0:
            print "echo --------; echo Closest matches:;"
            for b in bestmatch:
                print "echo '%s';" % b[0]
        print "echo ; echo ;"

def load_mod(modname):
    loaded = get_loaded()
    print "echo Building module dependency tree;"
    deps = resolve_deps([modname])
    print "echo Loading required modules;"
    for d in deps:
        load(d, loaded)

def unload_mod(modname):
    global switches
    loaded = get_loaded()
    if switches['-f']['setting']:
        print 'echo Force unloading %s;' % modname
        print 'module unload %s; ' % modname
        return
    for l in loaded:
        deps, cons = get_mod_reqs(l)
        for d in deps:
            if modname.startswith(d) or d.startswith(modname):
                print "echo %s requires %s, aborting unload;  echo Hint: use -f to force unload;" % (l, modname)
                return
    print 'module unload %s; ' % modname

def help_mod(helpcmd=None):
    print "echo ; echo dmod version %s;" % version
    if helpcmd:
        print "echo %s - %s ; echo ;" % (helpcmd, avail_cmds[helpcmd]['desc'])
        return

    print "echo ; echo dmod is a wrapper for Environment modules, intended; echo to improve on some of its functionality; echo ;"
    print "echo Usage:  dmod [switches] [subcommand] [modulename]; echo ; echo Switches:;"
    for key, item in switches.iteritems():
        print "echo '\t'%s : %s ;" % (key, item['desc'])
    print "echo ; echo Subcommands:;"
    for key, item in avail_cmds.iteritems():
        print "echo '\t'+ %s : %s ;" % (key, item['desc'])
    print "echo ;"

def bookmark_env(name=None):
    if name is None:
        print "echo No bookmark name provided, aborting;"
        return
    dmod_dir = os.path.join(os.path.expanduser('~'),'.dmod')
    bm = os.path.join(dmod_dir,name)
    if os.path.isfile(bm):
        print "echo Bookmark %s is already in use;" % name
        return
    print "echo Bookmarking current modules...; echo;"
    if not os.path.isdir(dmod_dir):
        os.mkdir(dmod_dir)
    bmfile = open(bm, 'w')
    loaded = get_loaded()
    for l in loaded:
        bmfile.write("%s\n" % l)
    bmfile.close()
    print "echo Current module environment saved under bookmark %s; echo -----------------;" % name
    print "echo To load this bookmark call dmod restore %s;" % name
    print "echo To see all saved bookmarks call dmod bookmarks;"

def restore_env(name=None):
    global switches
    switches['-f']['setting'] = True
    if name is None:
        print "echo No bookmark name provided, aborting;"
        return
    dmod_dir = os.path.join(os.path.expanduser('~'),'.dmod')
    bm = os.path.join(dmod_dir,name)
    if not os.path.isfile(bm):
        print "echo Bookmark %s not found;" % name
        return
    print "echo Loading %s modules...;" % name
    bmfile = open(bm, 'r')
    mods = bmfile.readlines()
    bmfile.close()
    for m in mods:
        load(m.strip())
    loaded = get_loaded()
    for l in loaded:
        keep = False
        for m in mods:
            if l.strip() == m.strip():
                keep = True
                break
        if not keep:
            unload_mod(l)

    print "echo Module environment %s restored;" % name

def bookmarks(foo):
    dmod_dir = os.path.join(os.path.expanduser('~'), '.dmod')
    if not os.path.isdir(dmod_dir):
        print "echo No bookmarks saved;"
        return
    else:
        for i in os.listdir(dmod_dir):
            print "echo %s;" % i

switches = {
    '-f' : {
                'name': 'force',
                'setting': False,
                'desc': "Force module unload, ignoring dependencies"
            },
    '-V' : {
                'name': 'version',
                'setting': False,
                'desc': "Print dmod version information and exit"
            }
    }

avail_cmds = {
    'avail' : {
                'func': search_mods,
                'desc': "Returns a list of available modules that include the provided string anywhere in the module name"
            },
    'load' : {
                'func': load_mod,
                'desc': "Recursively loads the requested module and all modules that it depends on"
            },
    'unload' : {
                'func': unload_mod,
                'desc': "Unloads the requested module, while checking to ensure that no other loaded modules depend on it"
            },
    'help' : {
                'func': help_mod,
                'desc': "Displays the available dmod commands and their descriptors"
            },
    'save' : {
                'func': bookmark_env,
                'desc': "Saves the list of currently loaded modules and creates a bookmark to allow rapid switching between environmental sets"
            },
    'restore' : {
                'func': restore_env,
                'desc': "Saves the list of currently loaded modules and creates a bookmark to allow rapid switching between environmental sets"
            },
    'bookmarks' : {
                'func': bookmarks,
                'desc': "List all saved bookmarks.  Use with -v to show the modules within each bookmark"
            }
    }

def main():
    global switches
    modindex = 2
    for idx,s in enumerate(sys.argv[1:]):
        if s in switches:
            switches[s]['setting'] = True
            continue
        elif s not in avail_cmds:
            print 'echo Unrecognized command: %s;' % s
            return
        else:
            modfunc = avail_cmds[s]['func']
            modindex = idx + 2
            break

    if switches['-V']['setting']:
        print "echo dmod v%s;" % version
        return
    # if sys.argv[1] not in avail_cmds:
    #     print 'echo Invalid module command;'
    #     return
    # else:
    #     modfunc = avail_cmds[sys.argv[1]]['func']

    try:
        modname = sys.argv[modindex]
    except:
        modname = None

    modfunc(modname)

if __name__ == '__main__':
    main()