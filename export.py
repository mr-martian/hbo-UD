#!/usr/bin/env python3

import utils
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('book', action='store')
parser.add_argument('chapters', nargs='+', type=int)
args = parser.parse_args()

ids = []
for sid, block in utils.iter_conllu(f'{args.book}.parsed.conllu'):
    for ch in utils.get_chapter(sid):
        if ch in args.chapters:
            ids.append(sid)

rule = utils.load_conllu(f'{args.book}.checked.conllu', True)
manual = utils.load_conllu(f'{args.book}.manual.conllu', True)

for sid in ids:
    if sid in rule:
        print(rule[sid][1] + '\n')
    else:
        print(manual[sid][1] + '\n')
