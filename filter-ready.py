#!/usr/bin/env python3

import sys
import utils
book = sys.argv[1]

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

check = utils.load_conllu(f'{book}.checked.conllu', clean=True)
gen = utils.load_conllu(f'{book}.parsed.conllu')

with open(f'{book}.checkable.conllu', 'w') as good:
    with open(f'{book}.incomplete.conllu', 'w') as bad:
        gc = 0
        bc = 0
        for k, (i, b) in gen.items():
            if k in check:
                continue
            if is_complete(b):
                good.write(f'# sentence_index = {i}\n')
                good.write(b + '\n\n')
                gc += 1
            else:
                bad.write(f'# sentence_index = {i}\n')
                bad.write(b + '\n\n')
                bc += 1
print(f'{gc} sentences in {book} are fully connected')
print(f'{bc} sentences in {book} have gaps')
