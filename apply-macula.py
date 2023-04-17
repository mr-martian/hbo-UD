#!/usr/bin/env python3

import utils
import xml.etree.ElementTree as ET
import glob

books = [
    ('genesis', '01-Gen'),
    ('exodus', '02-Exo'),
    ('ruth', '08-Rut'),
]

def iter_trees(macula_name):
    for fname in sorted(glob.glob(f'macula-hebrew/nodes/{macula_name}-*.xml')):
        tree = ET.parse(fname)
        yield from tree.getroot()

def clean_str(s):
    return ''.join(c for c in s if ord(c) <= 0x5ea)

rule2rel = {
    'NpAdjp': ['*', 'amod'],
    'DetNP': ['det', '*'],
    'PrepNp': ['case', '*'],
    'OmpNP': ['case', '*'],
    'NpaNp': ['*', 'cc', 'conj'],
    'NPofNP': ['*', 'compound:smixut'],
    'PPandPP': ['*', 'cc', 'conj'],
    'cjpCLx': ['mark', '*'],
    'NpNump': ['*', 'nummod'],
    'CLaCL': ['*', 'cc', 'conj'],
    'NpRelp': ['*', 'acl:relcl'],
    'relCL': ['mark', '*'],
    '2Pp': ['case', '*'],
    'DetAdjp': ['det', '*'],
    'NpPp': ['*', 'nmod'],
    'Np-Appos': ['*', 'appos'],
    'QuanNP': ['*', 'compound:smixut'],
    'NumpNP': ['nummod', '*'],
    'PrepCL': ['mark', '*'],
    'NumpAndNump': ['*', 'cc', 'conj'],
    'NumpNump': ['*', 'flat'],
    'DetNump': ['det', '*'],
    'NounX': ['*', 'case'],
    'VerbX': ['*', 'dep'],
    'AdvX': ['*', 'case'],
    'AdjpaAdjp': ['*', 'cc', 'conj'],
    'CLandCL2': ['*', 'cc', 'conj'],
    'OmpRelp': ['*', 'acl:relcl'],
    'AdjpAdvp': ['*', 'advmod'],
    'VPandVP': ['*', 'cc', 'conj'],
    'aNpaNp': ['cc', '*', 'cc', 'conj'],
    'NPaNPNPaNP': ['*', 'cc', 'conj', 'conj', 'cc', 'conj'],
    'AdvpandAdvp': ['*', 'cc', 'conj'],

    'PpPp': ['*', 'appos'], # TODO
    'ClCl2': ['advmod', '*'], # hineh
    'ClCl': ['*', 'advcl'], # pen
}

conjs = [
    ('cjp+CL', ['cc', '*'], '+cjp+CL', ['cc', 'conj']),
    ('CL', ['*'], '+cjp+CL', ['cc', 'conj']),
    ('Nump', ['*'], 'aNump', ['cc', 'conj']),
]

for k1, v1, kp, vp in conjs:
    for i in range(4):
        k = k1
        v = v1[:]
        for j in range(i):
            k += kp
            v += vp
        rule2rel[k] = v

def set_relations(node):
    if node.tag != 'Node':
        return
    if len(node) == 1:
        node[0].attrib['deprel'] = node.attrib['deprel']
        set_relations(node[0])
        return
    rule = node.attrib.get('Rule', '')
    if not rule and node.attrib.get('Cat', '')== 'S':
        rule = '+'.join(c.attrib.get('Cat', '_') for c in node)
    rels = []
    for p in rule.split('-'):
        x = {'S': 'nsubj', 'V': '*', 'O': 'obj', 'PP': 'obl', 'P': '*', 'ADV': 'advmod', 'O2': 'xcomp'}
        if p not in x:
            rels = []
            break
        rels.append(x[p])
    if not rels:
        if rule not in rule2rel:
            print(rule or '_', node.attrib.get('nodeId', 'no id'))
            for c in node:
                c.attrib['deprel'] = 'dep'
                set_relations(c)
            return
        rels = rule2rel[rule]
    if len(rels) != len(node):
        print(rule, node.attrib.get('nodeId', 'no id'), len(rule), '!=', len(node))
        for c in node:
            c.attrib['deprel'] = 'dep'
            set_relations(c)
        return
    for n, r in zip(node, rels):
        if r == '*':
            r = node.attrib['deprel']
        n.attrib['deprel'] = r
        set_relations(n)

def process_tree(ud_block, macula_trees):
    mac_deps = []
    ls = []
    skip = ['paragogic he', 'directional he', 'paragogic nun']
    for t in macula_trees:
        for tr in t.iter('Tree'):
            for c in tr:
                c.attrib['deprel'] = 'root'
                set_relations(c)
        for m in t.iter('m'):
            if m.attrib.get('type', '') in skip:
                continue
            ls.append(m.text or '_')
            mac_deps.append(m.attrib.get('deprel', '_'))
    head, body = utils.split_lines(ud_block)
    words = [l for l in body if '-' not in l.split()[0] and 'PUNCT' not in l]
    lemor = 0
    dirhe = 0
    leplus = 0
    ud_deps = []
    for w in words:
        dep = w.split('\t')[7]
        if 'לאמר\tSCONJ' in w:
            ud_deps += ['case', dep]
            lemor += 1
        elif 'Case=Loc' in w:
            ud_deps += [dep, 'case']
            dirhe += 1
        elif w.split()[2] in ['לכן', 'למה', 'אדני']:
            ud_deps += ['case', dep]
            leplus += 1
        else:
            ud_deps.append(dep)
    if len(words) + lemor + dirhe + leplus != len(ls):
        print('misalign', head[0], len(words), len(ls))
        print('misalign', ls)
        print('misalign', [x.split()[2] for x in words])
    elif ud_deps != mac_deps:
        print('depdiff', head[0])
        print('depdiff ud ', ud_deps)
        print('depdiff mac', mac_deps)

def process_book(ud_name, macula_name):
    all_trees = iter_trees(macula_name)
    for cid, block in utils.iter_conllu(f'temp/merged/{ud_name}.conllu'):
        verses = cid.split('-')[2:-1]
        v1 = verses[0]
        v2 = verses[-1]
        if ':' not in v2:
            v2 = v1.split(':')[0] + ':' + v2
        t = next(all_trees)
        trees = [t]
        while t.attrib['verse'].split()[-1] != v2:
            t = next(all_trees)
            trees.append(t)
        process_tree(block, trees)

for b in books:
    process_book(*b)

