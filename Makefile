SCIDB_MANPATH=${HOME}/scidb-13.12.0.6872/doc/api/man/man3/
SCIDB_SRCPATH=${HOME}/scidb-13.12.0.6872/src/

afl.json : generate.py
	SCIDB_MANPATH=${SCIDB_MANPATH} SCIDB_SRCPATH=${SCIDB_SRCPATH} python generate.py
