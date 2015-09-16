ROOT=${HOME}/scidbtrunk
SCIDB_MANPATH=${ROOT}/doc/api/man/man3/
SCIDB_SRCPATH=${ROOT}/src/

afldb.py : generate.py
	SCIDB_MANPATH=${SCIDB_MANPATH} SCIDB_SRCPATH=${SCIDB_SRCPATH} python generate.py
