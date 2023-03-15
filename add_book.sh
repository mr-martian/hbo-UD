#!/bin/bash

python3 splitting.py $1
make "temp/plain-cg3/$1.txt"
make "temp/parsed-cg3/$1.txt"
make "temp/merged/$1.conllu"
touch "data/manual/$1.conllu"
touch "data/checked/$1.conllu"
touch "data/checkable/$1.conllu"
touch "data/incomplete/$1.conllu"
make "$1-book"
make "$1-report"
