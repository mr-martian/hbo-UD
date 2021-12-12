#!/bin/bash

python3 splitting.py $1
make "$1.corpus.cg3.txt"
make "$1.parsed.cg3.txt"
make "$1.cg3.conllu"
make "$1.punct.conllu"
make "$1.parsed.conllu"
make "$1-book"
make "$1-report"
