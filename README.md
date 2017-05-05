# dmod
Python-based wrapper for HPC Environment Modules

dmod functions as a wrapper for the module command used in many hpc environments.  There are several ways that dmod improves on modules, including:

+ Active dependency tree resolution
+ Full string searching of available modules
+ Dependency checking when unloading modules
+ Saving and restoring user-defined sets of modules

## Installation

Clone this repository and chmod+x 
Add the following to your .bashrc (define or replace $DMODPATH with the path to dModule.py):

```dmod() {  DMODULECMD="$DMODPATH";
 eval `${DMODULECMD} $*`
}
export -f dmod
```

## Usage

