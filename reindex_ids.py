#!/usr/bin/env python3

from collections import defaultdict

books = ['genesis', 'ruth']

new_ids = defaultdict(dict)

def get_id(eid, update):
    global new_ids
    etype = eid[0]
    if eid in new_ids[etype]:
        return new_ids[etype][eid]
    elif update:
        n = len(new_ids[etype])+1
        new_ids[etype][eid] = f'{etype}{n}'
        return new_ids[etype][eid]
    else:
        return None

def update_file(fname, col, update):
    new_txt = []
    with open(fname) as fin:
        for line in fin:
            if not line.strip():
                continue
            ls = line.split()
            eid = get_id(ls[col], update)
            if eid:
                ls[col] = eid
                new_txt.append(' '.join(ls))
    with open(fname, 'w') as fout:
        fout.write('\n'.join(new_txt) + '\n')

for book in books:
    update_file(f'coref/spans/{book}.txt', -1, True)

names = []
with open('coref/spans/names.txt') as fin:
    for line in fin:
        ls = line.split()
        if len(ls) == 2:
            eid = get_id(ls[0], False)
            if eid:
                names.append((eid, ls[1]))
with open('coref/spans/names.txt', 'w') as fout:
    ndct = dict(names)
    for etype in sorted(new_ids.keys()):
        for n in range(1, len(new_ids[etype])+1):
            name = ndct.get(f'{etype}{n}', '_')
            fout.write(f'{etype}{n} {name}\n')
