#!/bin/bash

# Usage: stop.sh [pidfile]

HOME=$(dirname $(dirname $(dirname $(realpath "$0"))))
PROJ=$(echo $(basename ${HOME}) | tr '[:upper:]' '[:lower:]')

if [[ $# -gt 0 ]]; then
	pidfile="$1"
else
	pidfile="${HOME}/var/${PROJ}.pid"
fi

kill_and_wait () {
	pid="$1"
	max="$2"

	# Send SIGINT to the process
	kill -2 "$pid"

	# Wait for the process to be dead (at most 'max' seconds)
	cpt=0
	while kill -0 "$pid" 2>/dev/null; do
		if [[ $cpt -gt $max ]]; then break; fi
		sleep 1
		cpt=$((cpt+1))
	done
}

if [ -f ${pidfile} ]; then
	pid=$(cat ${pidfile})
	if [[ "$pid" =~ ^[0-9]+$ ]]; then
		kill_and_wait "$pid" 30
	else
		echo "The content of the pid file is invalid"
	fi
else
	echo "The pid file was not found"
fi