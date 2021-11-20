#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('sent', type=int)
parser.add_argument('annotator', action='store')
args = parser.parse_args()

with open('generated.conllu') as fin:
    block = fin.read().strip().split('\n\n')[args.sent-1]
    with open('checked.conllu', 'a') as fout:
        fout.write('\n')
        written = False
        for ln in block.splitlines():
            fout.write(ln + '\n')
            if ln[0] != '#' and not written:
                fout.write(f'# checker = {args.annotator}\n')
                written = True
