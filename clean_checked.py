#!/usr/bin/env python3

import utils

def clean_block(block):
    head = []
    blk = []
    for ln in block.splitlines():
        if ln[0] == '#':
            if 'sentence_index' not in ln:
                head.append(ln)
        else:
            blk.append(ln)
    return '\n'.join(head + blk)

gen = utils.load_conllu('generated.conllu')
ref = utils.load_conllu('checked.conllu')

ls = []
for k in ref:
    ls.append((gen[k][0], clean_block(ref[k][1])))
ls.sort()
with open('checked.conllu', 'w') as fout:
    fout.write('\n\n'.join(b[1] for b in ls) + '\n')
