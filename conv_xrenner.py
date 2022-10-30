#!/usr/bin/env python3

from utils import iter_conllu

import sys

book = sys.argv[1]

words = []
for i, (sid, block) in enumerate(iter_conllu(f'coref/base/{book}.conllu'), 1):
    for l in block.splitlines():
        n = l.split('\t')[0]
        if n.isdigit():
            words.append(f'{i}:{n}')

marked_words = []
with open(f'coref/pred/{book}.txt') as fin:
    starts = 0
    ends = 0
    cur = ''
    for l in fin.readlines():
        if l.startswith('</ref'):
            ends += 1
        elif l.startswith('<ref'):
            if cur or ends > 0:
                marked_words.append((cur, starts, ends))
                cur = ''
                ends = 0
            starts += 1
        else:
            if cur:
                marked_words.append((cur, starts, ends))
                starts = 0
                ends = 0
            cur = l.strip()
    if cur:
        marked_words.append((cur, starts, ends))

print(f'words {len(words)} marked {len(marked_words)}')

spans = []
stack = []
for idx, (surf, start, end) in zip(words, marked_words):
    for i in range(start):
        stack.append(idx)
    for i in range(end):
        s = stack.pop()
        spans.append((s, idx))

with open(f'coref/pred-spans/{book}.txt', 'w') as fout:
    for i, (s, e) in enumerate(spans, 1):
        fout.write(f'{s}-{e} u{i}\n')
