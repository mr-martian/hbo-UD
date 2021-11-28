#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('sent', type=int)
args = parser.parse_args()

with open('generated.conllu') as fin:
    block = fin.read().strip().split('\n\n')[args.sent-1]
    with open('rejected.conllu', 'a') as fout:
        fout.write('\n' + block + '\n')
