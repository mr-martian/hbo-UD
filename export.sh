#!/bin/bash

mode=$1

if [[ "$mode" == "train" ]]
then
	./export.py genesis 31-50
	./export.py ruth 1-4
elif [[ "$mode" == "dev" ]]
then
     ./export.py genesis 1-18
else
	./export.py genesis 19-30
fi
