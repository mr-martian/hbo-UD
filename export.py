#!/usr/bin/env python3

import utils
import argparse
import unicodedata

parser = argparse.ArgumentParser()
parser.add_argument('book', action='store')
parser.add_argument('chapters', nargs='+')
args = parser.parse_args()

chapters = []
for c in args.chapters:
    if c.isnumeric():
        chapters.append(int(c))
    elif c.count('-') == 1:
        a, b = c.split('-')
        if a.isnumeric() and b.isnumeric():
            chapters += list(range(int(a), int(b)+1))
        else:
            parser.error("Invalid chapter specifier '%s'" % c)
    else:
        parser.error("Invalid chapter specifier '%s'" % c)

ids = []
for sid, block in utils.iter_conllu(f'{args.book}.parsed.conllu'):
    for ch in utils.get_chapter(sid):
        if ch in chapters:
            ids.append(sid)

rule = utils.load_conllu(f'{args.book}.checked.conllu', True)
manual = utils.load_conllu(f'{args.book}.manual.conllu', True)

for sid in ids:
    if sid in rule:
        print(unicodedata.normalize('NFC', rule[sid][1]) + '\n')
    else:
        print(unicodedata.normalize('NFC', manual[sid][1]) + '\n')
