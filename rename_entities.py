#!/usr/bin/env python3

from edit_corefs import CorefCorpus

gcorp = CorefCorpus('genesis')
rcorp = CorefCorpus('ruth')

replace = {}

import sys
for lineno, line in enumerate(sys.stdin, 1):
    ls = line.split()
    if len(ls) == 3:
        ls = [ls[0], ls[1], ls[2][0]+'?', ls[2]]
    if len(ls) == 4:
        oldid, oldname, newid, newname = ls
        if newid in gcorp.rev_names:
            replace[oldid] = newid
            gcorp.rev_names[newid] = newname
            gcorp.names[newname] = newid
            print(f'Line {lineno}: merging {oldid} ({oldname}) into {newid} ({newname})')
            continue
        if newname != '_' and newname in gcorp.names:
            eqid = gcorp.names[newname]
            if eqid[0] != newid[0]:
                print(f'Line {lineno}: name {newname} already in use for entity {eqid}')
                sys.exit(1)
            if newid.endswith('?'):
                newid = eqid
                print(f'Note: Line {lineno}: merging {oldid} ({oldname}) into {newid} ({newname})')
            else:
                if eqid != oldid:
                    print(f'Line {lineno}: name {newname} matches entity {eqid}, merging')
                replace[eqid] = newid
        if newid.endswith('?'):
            newid = gcorp.next_id(newid[0], newname, save=False)
        else:
            gcorp.rev_names[newid] = newname
            gcorp.names[newname] = newid
        replace[oldid] = newid
        print(f'Line {lineno}: replacing {oldid} ({oldname}) with {newid} ({newname})')

if sys.argv[-1] == '--dry':
    sys.exit(0)

def rename(corp):
    global replace
    for span in corp.ispans():
        corp.spans[span] = replace.get(corp.spans[span], corp.spans[span])
    corp.save()

rename(rcorp)
rename(gcorp)
