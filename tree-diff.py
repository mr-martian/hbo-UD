#!/usr/bin/env python3

import argparse
import json
import sys

import utils

parser = argparse.ArgumentParser()
parser.add_argument('--macula', '-m', action='store_true')
parser.add_argument('book', action='store')
parser.add_argument('verse', action='store')
args = parser.parse_args()

m = 'macula-' if args.macula else ''
fgen = f'temp/{m}merged/{args.book}.conllu'
fref = f'data/checked/{args.book}.conllu'
fman = f'data/manual/{args.book}.conllu'

gen = utils.load_conllu(fgen)
ref = utils.load_conllu(fref, True)
man = utils.load_conllu(fman, True)

for k in gen:
    if str(gen[k][0]) == args.verse:
        sid = k
        break
else:
    print(f'Could not find {args.book} {args.verse}.')
    sys.exit(1)

text = ''
words = [('0', 'ROOT', 'ROOT', 'ROOT', 'ROOT')]
arcs = {}

for line in gen[sid][1].splitlines():
    if line.startswith('# text ='):
        text = line.split('=')[1].strip()
        continue
    cols = line.strip().split('\t')
    if len(cols) != 10:
        continue
    if not cols[0].isdigit():
        continue
    gls = ''
    if 'Gloss' in cols[9]:
        gls = cols[9].split('Gloss=')[1].split('|')[0]
    arcs[cols[0]] = [(cols[6], cols[7])]
    words.append((cols[0], cols[1], cols[2], cols[3], gls))

words.reverse()

rows = ''.join(
    f'<tr id="words{i}"><td>' + '</td><td>'.join(r) + '</td></tr>'
    for i, r in enumerate(zip(*words))
)
rows += f'<tr><td colspan="{len(words)}">{text}</td></tr>'

if sid in ref:
    block = ref[sid][1]
elif sid in man:
    block = man[sid][1]
else:
    print(f'Reference for {args.book} {args.verse} not found.')
    sys.exit(1)

for line in block.splitlines():
    cols = line.strip().split('\t')
    if len(cols) == 10 and cols[0] in arcs:
        arcs[cols[0]].append((cols[6], cols[7]))

als = []
for k, v in arcs.items():
    dep = len(words) - int(k) - 1
    h0 = len(words) - int(v[0][0].replace('_', '0')) - 1
    h1 = len(words) - int(v[1][0].replace('_', '0')) - 1
    if v[0] == v[1]:
        als.append({'head': h0, 'dep': dep, 'label': v[0][1], 'color': 'black'})
    else:
        als.append({'head': h0, 'dep': dep, 'label': v[0][1], 'color': 'red'})
        als.append({'head': h1, 'dep': dep, 'label': v[1][1], 'color': 'green'})

for i in range(len(als)):
    als[i]['height'] = 0

def contains(big, little):
    bh, bd = big['head'], big['dep']
    lh, ld = little['head'], little['dep']
    if (bh, bd) == (ld, lh):
        return bh < lh
    elif (bh, bd) == (lh, ld):
        return big['color'] == 'green'
    elif (bh <= lh <= bd) and (bh <= ld <= bd):
        return True
    else:
        return (bd <= lh <= bh) and (bd <= ld <= bh)

relevant = {}
for i in range(len(als)):
    relevant[i] = [j for j in range(len(als))
                   if i != j and contains(als[i], als[j])]

todo = list(relevant.keys())
while todo:
    nt = []
    for t in todo:
        h = [als[i]['height'] for i in relevant[t]]
        if not h:
            als[t]['height'] = 1
        elif 0 not in h:
            als[t]['height'] = max(h) + 1
        else:
            nt.append(t)
    todo = nt

with open('tree-diff.html') as fin, open('index.html', 'w') as fout:
    page = fin.read()
    page = page.replace('[[WORDS]]', rows)
    page = page.replace('[[ARCS]]', json.dumps(als))
    page = page.replace('[[HEIGHT]]', str(max(h['height'] for h in als)))
    fout.write(page)
