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

def print_block(blk):
    for line in unicodedata.normalize('NFC', blk).splitlines():
        ls = line.strip().split('\t')
        if len(ls) == 10 and ls[1] == '_':
            ls[1] = ls[2]
        print('\t'.join(ls))
    print('')

for sid in ids:
    if sid in rule:
        print_block(rule[sid][1])
    else:
        print_block(manual[sid][1])
