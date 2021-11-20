#!/usr/bin/env python3

import sys

with open('generated.cg3.txt') as fin:
    print(fin.read().strip().split('\n\n')[int(sys.argv[1])-1])

with open('generated.conllu') as fin:
    print(fin.read().strip().split('\n\n')[int(sys.argv[1])-1])
