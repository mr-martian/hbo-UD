#!/usr/bin/env python3

from collections import defaultdict

def load_volume(vol, hoist):
    from tf.app import use
    import sys
    out = sys.stdout
    sys.stdout = open('blah.txt', 'w')
    if vol[0].isnumeric():
        v = vol[:2] + vol[2:].capitalize() + 'Book'
    else:
        v = vol.capitalize() + 'Book'
    use("bhsa", mod="etcbc/trees/tf,etcbc/bridging/tf", hoist=hoist, volume=v)
    sys.stdout.close()
    sys.stdout = out

def get_id(block):
    ls = block.splitlines()
    for ln in ls:
        if ln.startswith('# sent_id'):
            return ln.split()[-1]

def clean_ref(block):
    ls = block.splitlines()
    return '\n'.join(ln for ln in ls if not ln.startswith('# checker'))

def iter_conllu(fname):
    with open(fname) as fin:
        for block in fin.read().strip().split('\n\n'):
            if not block:
                continue
            yield get_id(block), block

def load_conllu(fname, clean=False):
    ret = {}
    for i, (n, b) in enumerate(iter_conllu(fname), 1):
        ret[n] = (i, clean_ref(b) if clean else b)
    return ret

def load_conllu_multi(fname):
    ret = defaultdict(list)
    for n, b in iter_conllu(fname):
        ret[n].append(b)
    return ret

def get_chapter(sid):
    def single(s):
        return int(s.split('-')[-1])
    p = sid.split(':')
    if len(p) == 2:
        return [single(p[0])]
    else:
        return [single(p[0]), single(p[1])]

def get_first_verse(sid):
    v1 = sid.split('-')[2]
    c, v = v1.split(':')
    return (int(c), int(v))

def split_lines(sent):
    head = []
    body = []
    for l in sent.strip().split('\n'):
        if l.startswith('#'):
            head.append(l)
        else:
            body.append(l)
    return head, body

def update_deps(old_sent, new_sent, old_headers=True):
    oh, ols = split_lines(old_sent)
    nh, nls = split_lines(new_sent)
    lines = oh if old_headers else nh
    if len(ols) != len(nls):
        return None
    for ol, nl in zip(ols, nls):
        ot = ol.split('\t')
        nt = nl.split('\t')
        if ot[0] != nt[0]:
            return None
        ot[6] = nt[6]
        ot[7] = nt[7]
        lines.append('\t'.join(ot))
    return '\n'.join(lines)

def get_cg(sent_id):
    book = sent_id.split('-')[1].lower()
    data = load_conllu(f'temp/merged/{book}.conllu')
    idx = data[sent_id][0]-1
    with open(f'temp/parsed-cg3/{book}.txt') as fin:
        return fin.read().split('\n\n')[idx]

def get_coref(book):
    with open(f'coref/spans/{book}.txt') as fin:
        for l in fin:
            ls = l.strip().split()
            if len(ls) != 2:
                continue
            yield (tuple(ls[0].split('-')), ls[1])
