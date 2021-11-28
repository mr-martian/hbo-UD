#!/usr/bin/env python3

import sys
import utils

def is_complete(block):
    for ln in block.splitlines():
        if '\t' not in ln:
            continue
        ls = ln.split('\t')
        if '-' in ls[0]:
            continue
        if '_' in [ls[3], ls[6], ls[7]]:
            return False
    return True

check = utils.load_conllu('checked.conllu', clean=True)
gen = utils.load_conllu('generated.conllu')
rej = utils.load_conllu_multi('rejected.conllu')

with open('checkable.conllu', 'w') as fout:
    n = 0
    for k, (i, b) in gen.items():
        if k in check:
            continue
        if b in rej[k]:
            continue
        if not is_complete(b):
            continue
        fout.write(f'# sentence_index = {i}\n')
        fout.write(b + '\n\n')
        n += 1
print(f'{n} sentences are fully connected')
