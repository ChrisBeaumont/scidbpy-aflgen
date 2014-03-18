# SciDB AFL Parser

This code parses SciDB source and documentation pages to build
a database of AFL function information. This database is in turn
used to build the SciDBpy AFL binding

## Usage

* Obtain the SciDB source code
* Build the manpages, as described [here](https://github.com/Paradigm4/scripts#step-1)
* Edit the Makefile if needed. `SCIDB_MATNPATH` should point to the
`doc/api/man/man3` subdirectory of wherever the documentation was built. `SCIDB_SRCPATH` should point to the `src/` subdirectory of the SciDB source code
* run `make` to generate `afl.json`
