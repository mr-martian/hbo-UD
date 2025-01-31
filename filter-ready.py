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
        if ls[7] == 'dep':
            return False
        if ls[7] != 'root' and ls[6] == '0':
            return False
    return True

check = utils.load_conllu(f'data/checked/{book}.conllu')

good = []
bad = []
checked = []

for i, (n, b) in enumerate(utils.iter_conllu(f'temp/macula-merged/{book}.conllu'), 1):
    if n in check:
        checked.append(check[n][1])
    elif is_complete(b):
        good.append(f'# sentence_index = {i}\n' + b)
    else:
        bad.append(f'# sentence_index = {i}\n' + b)

def maybe_replace(fname, ls):
    text = '\n\n'.join(ls) + ('\n\n' if ls else '')
    with open(fname) as fin:
        if text != fin.read():
            with open(fname, 'w') as fout:
                fout.write(text)

maybe_replace(f'data/checked/{book}.conllu', checked)
maybe_replace(f'data/checkable/{book}.conllu', good)
maybe_replace(f'data/incomplete/{book}.conllu', bad)

print(f'{book}: accepted: {len(checked)} checkable: {len(good)} incomplete: {len(bad)}')
