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

rule = utils.load_conllu(f'data/checked/{args.book}.conllu', True)
manual = utils.load_conllu(f'data/manual/{args.book}.conllu', True)
rule.update(manual)
ids = sorted(rule.keys(), key=utils.get_first_verse)
ids = [s for s in ids if any(c in chapters for c in utils.get_chapter(s))]

def print_block(blk):
    for line in unicodedata.normalize('NFC', blk).splitlines():
        ls = line.strip().split('\t')
        if len(ls) == 10 and ls[1] == '_':
            ls[1] = ls[2]
        print('\t'.join(ls))
    print('')

for sid in ids:
    print_block(rule[sid][1])
