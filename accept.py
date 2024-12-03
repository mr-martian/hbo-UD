#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('annotator', action='store')
parser.add_argument('book', action='store')
parser.add_argument('sent', type=int, nargs='+')
args = parser.parse_args()

with open(f'temp/macula-merged/{args.book}.conllu') as fin:
    blocks = fin.read().strip().split('\n\n')
    with open(f'data/checked/{args.book}.conllu', 'a') as fout:
        for sent in args.sent:
            block = blocks[sent-1]
            written = False
            for ln in block.splitlines():
                if ln[0] != '#' and not written:
                    fout.write(f'# checker = {args.annotator}\n')
                    written = True
                fout.write(ln + '\n')
            fout.write('\n')
