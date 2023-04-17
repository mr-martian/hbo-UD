#!/usr/bin/env python3

import subprocess
import sys

data = sys.stdin.read()

proc = subprocess.run(['udapy', '-s', '-q', 'ud.FixPunct'],
                      input=data.encode('utf-8'),
                      capture_output=True)

for l1, l2 in zip(data.splitlines(), proc.stdout.decode('utf-8').splitlines()):
    if l1.count('\t') != 9 or 'PUNCT' not in l1:
        print(l1)
    else:
        ls1 = l1.split('\t')
        ls2 = l2.split('\t')
        ls1[6] = ls2[6]
        print('\t'.join(ls1))
