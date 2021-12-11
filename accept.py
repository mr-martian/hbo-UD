#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('annotator', action='store')
parser.add_argument('book', action='store')
parser.add_argument('sent', type=int)
args = parser.parse_args()

with open(f'{args.book}.parsed.conllu') as fin:
    block = fin.read().strip().split('\n\n')[args.sent-1]
    with open(f'{args.book}.checked.conllu', 'a') as fout:
        written = False
        for ln in block.splitlines():
            if ln[0] != '#' and not written:
                fout.write(f'# checker = {args.annotator}\n')
                written = True
            fout.write(ln + '\n\n')
