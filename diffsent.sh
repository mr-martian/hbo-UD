#!/bin/bash

diff -U0 <(./show.py -r $1 $2) <(./show.py -g $1 $2) | dwdiff -uc
