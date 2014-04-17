SCIDB_MANPATH=${HOME}/scidb-14.3.0.7383/doc/api/man/man3/
SCIDB_SRCPATH=${HOME}/scidb-14.3.0.7383/src/

afldb.py : generate.py
	SCIDB_MANPATH=${SCIDB_MANPATH} SCIDB_SRCPATH=${SCIDB_SRCPATH} python generate.py
