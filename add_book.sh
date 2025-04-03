#!/bin/bash

python3 splitting.py $1
touch "data/manual-arcs/$1.tsv"
touch "data/manual-heads/$1.tsv"
make "temp/macula-arcs/$1.tsv"
make "temp/macula-cg3/$1.txt"
make "temp/macula-parsed-cg3/$1.txt"
make "temp/macula-merged/$1.conllu"
touch "data/checked/$1.conllu"
touch "data/checkable/$1.conllu"
touch "data/incomplete/$1.conllu"
make "$1-book"
make "$1-report"
