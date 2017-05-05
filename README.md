# dmod
Python-based wrapper for HPC Environment Modules

dmod functions as a wrapper for the module command used in many hpc environments.  There are several ways that dmod improves on modules, including:

+ Active dependency tree resolution
+ Full string searching of available modules
+ Dependency checking when unloading modules
+ Saving and restoring user-defined sets of modules

## Installation

Clone this repository and make sure dModule.py is flagged as executable. 

### bash

Add the following to your .bashrc (define or replace $DMODPATH with the path to dModule.py):

```
dmod() {  DMODULECMD="$DMODPATH";
 eval `${DMODULECMD} $*`
}
export -f dmod
```
### csh/tcsh


## Usage

Usage: dmod [switches] [subcommand] [modulename]

Switches:
 - -V : Print dmod version information and exit
 - -f : Force module unload, ignoring dependencies

Subcommands:
 + load : Recursively loads the requested module and all modules that it depends on
 + restore : Saves the list of currently loaded modules and creates a bookmark to allow rapid switching between environmental sets
 + help : Displays the available dmod commands and their descriptors
 + unload : Unloads the requested module, while checking to ensure that no other loaded modules depend on it
 + avail : Returns a list of available modules that include the provided string anywhere in the module name
 + bookmarks : List all saved bookmarks. Use with -v to show the modules within each bookmark
 + save : Saves the list of currently loaded modules and creates a bookmark to allow rapid switching between environmental sets
