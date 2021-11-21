#!/usr/bin/env python3

import sys

def get_id(block):
    ls = block.splitlines()
    for ln in ls:
        if ln.startswith('# sent_id'):
            return ln.split()[-1]

def load_conllu(fname):
    with open(fname) as fin:
        ret = {}
        for i, block in enumerate(fin.read().strip().split('\n\n'), 1):
            ret[get_id(block)] = (i, block)
        return ret

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

check = load_conllu('checked.conllu')
gen = load_conllu('generated.conllu')

with open('checkable.conllu', 'w') as fout:
    n = 0
    for k, (i, b) in gen.items():
        if k in check:
            continue
        if not is_complete(b):
            continue
        fout.write(f'# sentence_index = {i}\n')
        fout.write(b + '\n\n')
        n += 1
print(f'{n} sentences are fully connected')
