#!/bin/bash

diff -U0 <(./show.py -r $1) <(./show.py -g $1) | dwdiff -uc