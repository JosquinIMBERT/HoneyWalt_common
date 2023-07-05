#!/bin/bash

# Usage: start.sh <log-level> [pidfile]

HOME=$(dirname $(dirname $(dirname $(realpath "$0"))))
PROJ=$(echo $(basename ${HOME}) | tr '[:upper:]' '[:lower:]')

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <log-level> [pidfile]"
	exit 1
else
	loglevel="$1"
fi

if [[ $# -gt 1 ]]; then
	pidfile="$1"
else
	pidfile="${HOME}/var/${PROJ}.pid"
fi

if [ "${PROJ}" = "honeywalt-vm" ]; then
	git -C ${HOME} reset -q --hard
	git -C ${HOME} pull -q --recurse-submodules
	${HOME}/requirements.sh
fi

# Start
python3 ${HOME}/src/${PROJ}.py \
	--log-level ${loglevel} \
	--pid-file ${pidfile}
