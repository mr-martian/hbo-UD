#!/usr/bin/env python3

import sys
from collections import defaultdict

ORDER = [#'Voct',
         'Time', 'Nega', 'Modi', 'Loca', 'Adju', 'Cmpl', 'Objc', 'Subj', '@cop', 'IntS', 'ModS', 'PrcS', 'PrAd', 'PreO', 'PreS', 'PtcO', 'PreC', '@ein', 'NCop', 'NCoS', 'Exst', 'ExsS', 'Pred']

MAP = [('vbcp', '@cop'), ('nmcp', '@ein')]
MAPd = {v:k for k,v in MAP}

# ignored: Frnt, EPPr, Conj, Intj, Ques, Rela, Supp, Unkn

def tags(w):
    try:
        return w.split('<', 1)[1][:-2].split('><')
    except:
        raise Exception(f'w = {w}')

def wid(tgs, pref):
    for t in tgs:
        if t.startswith(pref) and t[len(pref):].isnumeric():
            return int(t[len(pref):])
    return 0

def getord(tgs):
    global ORDER, MAP
    for i, t in enumerate(ORDER):
        if t in tgs:
            if t in ['Pred', 'Nega']:
                for r, o in MAP:
                    if r in tgs:
                        return ORDER.index(o)
            return i
    return -2

def ident(wds):
    clsmx = defaultdict(lambda: -1)
    ls1 = []
    for w, tgs in wds:
        o = getord(tgs)
        c = wid(tgs, 'c')
        clsmx[c] = max(clsmx[c], o)
        ls1.append((w, tgs, c, o))
    ls2 = []
    for w, tgs, c, o in ls1:
        if c != 0 and o != -1 and clsmx[c] == o:
            t = '<'+ORDER[MAPd.get(o, o)]+'>'
            ls2.append(w.replace(t, t+f'<ClausePhraseRoot>'))
        else:
            ls2.append(w)
    print(' '.join(ls2))

def main():
    ls = []
    cur_sent = 0
    for line in sys.stdin:
        if not line:
            break
        w = line.strip()
        if not w:
            continue
        tgs = tags(w)
        s = wid(tgs, 's')
        if s not in [0, cur_sent]:
            if ls:
                ident(ls)
                ls = []
            cur_sent = s
        ls.append((w, tgs))
    if ls:
        ident(ls)

if __name__ == '__main__':
    main()
