#!/bin/bash

diff -U0 <(./show.py $1 $2 ref) <(./show.py $1 $2 conllu) | dwdiff -uc
