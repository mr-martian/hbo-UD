#!/usr/bin/env python3

import utils
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('book', action='store')
parser.add_argument('chapters', nargs='+', type=int)
args = parser.parse_args()

for sid, block in utils.iter_conllu(f'{args.book}.checked.conllu'):
    for ch in utils.get_chapter(sid):
        if ch in args.chapters:
            print(utils.clean_ref(block) + '\n')
            break
