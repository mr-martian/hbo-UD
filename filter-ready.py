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

check = utils.load_conllu(f'{book}.checked.conllu')
manual = utils.load_conllu(f'{book}.manual.conllu')

good = []
bad = []
checked = []
manual_ls = []

for i, (n, b) in enumerate(utils.iter_conllu(f'{book}.parsed.conllu'), 1):
    if n in check:
        checked.append(check[n][1])
    elif n in manual:
        if manual[n][1] == b:
            checked.append(manual[n][1])
        else:
            manual_ls.append(manual[n][1])
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

maybe_replace(f'{book}.checked.conllu', checked)
maybe_replace(f'{book}.checkable.conllu', good)
maybe_replace(f'{book}.incomplete.conllu', bad)
maybe_replace(f'{book}.manual.conllu', manual_ls)

print(f'{book}: accepted: {len(checked)} manual: {len(manual_ls)} checkable: {len(good)} incomplete: {len(bad)}')
