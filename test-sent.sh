#!/bin/bash

diff -U0 <(./show.py $1 $2 cg) <(vislcg3 -t -g hbo-macula.bin) | dwdiff -uc | aha -n
