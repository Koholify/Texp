#! /bin/bash

texp() {
	./src/main.py
	local result
	if [[ -f /tmp/texptargetresult ]]; then
		result=$(cat /tmp/texptargetresult)
		rm /tmp/texptargetresult
	fi

	if [[ -d "$result" ]]; then
		cd "$result"
	fi
}

texp

