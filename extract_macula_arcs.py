#!/usr/bin/env python3

import utils
import xml.etree.ElementTree as ET
import glob
import re
import sys
import unicodedata
from collections import defaultdict

xml_id = '{http://www.w3.org/XML/1998/namespace}id'

HEAD_OVERRIDE = {
    'PpAdvp': 1,
    'ppCL': 0,
    'PpRelp': 0, # TODO: should we just use case:outer for this instead?
    'OmpRelp': 0,
    'ADV-ADV': 0, # TODO: check which adverbs?
    'QuanNP': 0,
    'CLaCL': 0,

    '12Np': 0,
    '2Advp_h1': 0,
    '2Advp_h2': 0,
    '2Np': 0,
    '3Adjp': 0,
    '7Np': 0,
    'AdvpandPp': 0,
    'CjpAdvpCjpAdvp': 1,
    'ClCl': 0,
    'NP10NP': 0,
    'NP3NP': 0,
    'NPandPP2np': 0,
    'NPnp4NP': 0,
    'NPnp5NP': 0,
    'Np5Np': 0,
    'NpNp5': 0,
    'NpNp6': 0,
    'NpNpNp': 0,
    'NpNpNp11': 0,
    'NpNpNpNp': 0,
    'NpNpNpNpNp': 0,
    'NpPp': 0,
    'NumpNump': 0,
    'PP8PP': 0,
    'PP9PP': 0,
    'PPPP4': 0,
    'PPPP5': 0,
    'PpPp9': 0,
    'PpPpPp': 0,
    'PpPpPpPpPp': 0,
    'PpandAdvp': 0,
    'Relp3Relp': 0,
    'Relp5Relp': 0,
    'VP3VP': 0,
    'VpVp2V3': 0,
    'Vpvp2V1': 0,
    'ppPP5PP': 0,
    'ppPP6PP': 0,
    'ppappPP5PP': 0,
}

r_and = re.compile(r'^\d*([A-Z]{1,2}[a-z]*?)\1*(?:[aA]nd\1+)+$')
r_a = re.compile(r'^a?\d*([A-Z]+[a-z]*?)\1*(?:a\1+)+$')
r_conj = re.compile(r'^Conj\d+([A-Z]+[a-z]*)$')

book_names = utils.load_book_data('Macula-file')

book = sys.argv[1]

manual = {}
with open(f'data/manual-arcs/{book}.tsv') as fin:
    for line in fin:
        ls = line.strip().split('\t')
        if len(ls) > 1:
            manual[ls[0]] = ls[1:]

manual_heads = {}
with open(f'data/manual-heads/{book}.tsv') as fin:
    for line in fin:
        ls = line.strip().split('\t')
        if len(ls) > 1:
            manual_heads[ls[0]] = ls[1]

def is_nouny(node):
    prep_noun_lemmas = [
        '8478', # תחת
        '5978', # עמד
    ]
    if node.attrib.get('Cat') == 'np':
        return True
    elif node.attrib.get('StrongNumberX') in prep_noun_lemmas:
        return True
    else:
        return any(is_nouny(ch) for ch in node)

def is_timey(node):
    if node.attrib.get('CoreDomain') == '168':
        return True
    return any(is_timey(ch) for ch in node)

def is_cond(node):
    if node.attrib.get('oshb-strongs') == '518a':
        return True
    if node.attrib.get('Cat') == 'relp':
        return True
    if node.attrib.get('Cat') == 'CL' and '-' in node.attrib.get('Rule', ''):
        return False
    return any(is_cond(ch) for ch in node)

def propogate_heads(node):
    if node.tag == 'm':
        node.attrib['headword'] = node.attrib[xml_id]
        if node.attrib.get('oshb-strongs') == '1961' and False:
            # TODO: copulas have been broken for a while
            # and updating the CG might be messy
            if node.attrib.get('type') == 'jussive':
                node.attrib['copula'] = 'juss'
            else:
                node.attrib['copula'] = 'yes'
        elif node.attrib.get('oshb-strongs') in ['3426', '369']:
            node.attrib['copula'] = 'nmcp'
        return
    for ch in node:
        propogate_heads(ch)
    if len(node) == 1:
        node.attrib['copula'] = node[0].attrib.get('copula') or ''
    if 'Head' not in node.attrib:
        node.attrib['Head'] = '0'
    r = node.attrib.get('Rule')
    if r in HEAD_OVERRIDE:
        node.attrib['Head'] = str(HEAD_OVERRIDE[r])
    elif r is None and node.attrib.get('Cat') == 'S':
        if node[0].attrib.get('Cat') == 'cjp':
            node.attrib['Head'] = '1'
    elif r == 'PrepNp':
        if node[0].attrib.get('Rule') == 'PrepNp' or is_nouny(node[0]):
            node.attrib['Head'] = '0'
            node.attrib['Rule'] = 'PrepNp+NomPrep'
    elif r == 'CLandCL2':
        cl0 = node[0]
        if cl0.attrib.get('Rule') == 'Np2CL' and len(cl0) == 1 and cl0[0].attrib.get('Cat') == 'np':
            node.attrib['Rule'] = 'CLandCL2+disloc'
        elif not is_cond(cl0):
            node.attrib['Head'] = '0'
        else:
            node.attrib['Rule'] = 'CLandCL2+if'
    elif r and '-' in r:
        if r == 'P-S':
            m = list(node[0].iter('m'))
            if len(m) == 1 and m[0].attrib.get('pos') == 'pronoun':
                r = 'S-P'
                node.attrib['Rule'] = 'S-P'
                node.attrib['Head'] = '1'
        ls = r.split('-')
        for i, role in enumerate(ls):
            if role == 'ADV' and node[i].attrib.get('copula') == 'nmcp':
                node.attrib['Head'] = str(i)
        if 'V' in ls:
            v = ls.index('V')
            cop = node[v].attrib.get('copula')
            if cop in ['yes', 'juss'] and node.attrib.get('Head', str(v)) == str(v):
                if 'O' in ls:
                    node.attrib['Head'] = str(ls.index('O'))
                elif 'PP' in ls and cop != 'juss':
                    possible = [p for p in enumerate(ls) if p[1] == 'PP']
                    possible2 = [p for p in possible if not is_timey(node[p[0]])]
                    if possible2:
                        node.attrib['Head'] = str(possible2[0][0])
                    else:
                        node.attrib['Head'] = str(possible[0][0])
    elif r == 'PpPp' and is_nouny(node[0]):
        node.attrib['Head'] = '0'
    elif r == '2Pp':
        if is_nouny(node[0]):
            node.attrib['Head'] = '0'
        else:
            node.attrib['Head'] = '1'
    elif r == 'ClClCl' and node[0].attrib.get('Rule') == 'Intj2CL':
        node.attrib['Head'] = '1'
    elif r and (m := r_and.match(r)):
        node.attrib['Head'] = '0'
        node.attrib['ConjType'] = m.group(1)
    elif r and (m := r_a.match(r)):
        node.attrib['Head'] = '1' if r[0] == 'a' else '0'
        node.attrib['ConjType'] = m.group(1)
    elif r and (m := r_conj.match(r)):
        node.attrib['ConjType'] = m.group(1)
        node.attrib['Head'] = '0'
    if node.attrib.get('nodeId') in manual_heads:
        node.attrib['Head'] = manual_heads[node.attrib['nodeId']]
    h = int(node.attrib['Head'])
    node.attrib['headword'] = node[h].attrib['headword']

def distribute_heads(node, headword, parentrule, rulepiece=None):
    if node.tag == 'm':
        node.attrib['parentrule'] = parentrule
        if node.attrib[xml_id] != headword:
            node.attrib['head'] = headword
        else:
            node.attrib['head'] = '0'
        if rulepiece is not None:
            node.attrib['rulepiece'] = rulepiece
            if '+' in rulepiece:
                node.attrib['rulepiece'], node.attrib['uprule'] = rulepiece.split('+')[:2]
    else:
        n = node.attrib.get('Head', '*')
        r = node.attrib.get('Rule', parentrule)
        roles = r.split('-')
        if len(node) == 1:
            roles = [rulepiece]
        elif r == 'Np-Appos':
            roles = [rulepiece, 'Appos']
        elif 'ConjType' in node.attrib:
            ct = node.attrib.get('ConjType')
            seq = []
            s = r
            while s:
                if s.startswith(ct):
                    seq.append('conj')
                    s = s[len(ct):]
                elif s.startswith('Conj'):
                    c = 0
                    s = s[4:]
                    while s[0].isdigit():
                        c = c * 10 + int(s[0])
                        s = s[1:]
                    seq += ['conj', 'cc'] * (c-1)
                elif s.startswith('and') or s.startswith('And'):
                    seq.append('cc')
                    s = s[3:]
                elif s.startswith('a'):
                    seq.append('cc')
                    s = s[1:]
                elif s[0].isdigit():
                    c = 0
                    while s[0].isdigit():
                        c = c * 10 + int(s[0])
                        s = s[1:]
                    seq += [ct] * (c-1)
                else:
                    break
            if not s and len(seq) == len(node) and seq[-1] != 'cc':
                hw = None
                for i, (ch, role) in enumerate(zip(node, seq)):
                    if role == 'cc':
                        h = node[seq.index('conj', i)]
                        distribute_heads(ch, h.attrib['headword'],
                                         r+'><@cc><'+ct+'-cc', None)
                    elif not hw:
                        distribute_heads(ch, headword, parentrule, rulepiece)
                        hw = ch.attrib['headword']
                    else:
                        distribute_heads(ch, hw, r+'><@conj><'+ct+'-conj',
                                         None)
                return
            else:
                roles = [None] * len(node)
                roles[int(n)] = rulepiece
        elif len(roles) != len(node):
            roles = [None] * len(node)
            roles[int(n)] = rulepiece
        for i, (ch, role) in enumerate(zip(node, roles)):
            if n == '*' or int(n) == i:
                rl = role
                if rulepiece:
                    rl = role+'+'+rulepiece
                distribute_heads(ch, headword, parentrule, rl)
            else:
                distribute_heads(ch, node.attrib['headword'], r, role)

def skip(c):
    if ord(c) > 0x5ea:
        return True # trop
    if ord(c) == 0x5c3:
        return True # sof pasuq
    if ord(c) < 0x5d0:
        return True # vowel
    return False

def clean(s):
    s2 = (s or '').replace(chr(0xfb2a), chr(0x5e9)).replace(chr(0xfb2b), chr(0x5e9))
    s3 = ''.join(c for c in s2.strip() if not skip(c))
    return unicodedata.normalize('NFC', s3)

def remsuf(a, b):
    if not b:
        return a
    if not a.endswith(b):
        return a
    return a[:-len(b)]

def matches(node, idx):
    bt = remsuf(T.text(idx) or '', F.trailer_utf8.v(idx))
    mt = node.text
    btc = clean(bt)
    mtc = clean(mt)
    if btc == mtc:
        return True
    if F.prs.v(idx) and btc.startswith(mtc):
        return True
    print('BHSA', btc, 'macula', mtc, 'text', [T.text(idx)], 'trailer', [F.trailer_utf8.v(idx)], file=sys.stderr)
    return False

bhsa_skip_nodes = {
    'genesis': [28427, 28426, 28460, 28461, 16564, 17279],
}

macula_skip_nodes = {
    'leviticus': ['o030270330051ה'],
}

name_groups = {
    '883+': ['B>R/', 'LXJ_R>J/'],
    '884+': ['B>R/', 'CB<==/'],
    '6636': ['YB>JM/'],
    '1976': ['H', 'LZH'],
    '763+': ['>RM/', 'NHR/'],
    '3026 a': ['JGR/', 'FHDW/'],
    '4772': ['MRGLT/'],
}

def is_split_prefix(node, idx):
    if node.attrib.get('oshb-strongs') == '1976' and F.lex.v(idx) == 'H' \
       and F.lex.v(idx+1) == 'LZH':
        return True
    return False

def is_merge_prefix(node, idx):
    if node.attrib.get('oshb-strongs') == 'l' and F.lex.v(idx) in ['LMH', 'LKN']:
        return True
    return False

def is_merge_main(node, idx):
    if F.lex.v(idx) == 'LMH' and node.attrib.get('oshb-strongs') == '4100':
        return True
    if F.lex.v(idx) == 'LKN' and node.attrib.get('oshb-strongs') == '3651c':
        return True
    return False

def is_np_second(node, idx):
    if F.lex.v(idx) == '>RM/' and F.lex.v(idx-1) == 'PDN/':
        return True
    return False

def is_name_group(node, idx):
    lm = node.attrib.get('oshb-strongs')
    if lm in name_groups:
        for i in range(len(name_groups[lm])):
            if F.lex.v(idx+i) != name_groups[lm][i]:
                return (False, 0)
        return (True, len(name_groups[lm]))
    return (False, 0)

def extract_morphemes(node):
    if node.tag == 'm':
        if node.attrib[xml_id] not in macula_skip_nodes:
            yield node
    elif node.tag == 'c':
        yield node[0]
    else:
        for ch in node:
            yield from extract_morphemes(ch)

def align_to_bhsa(sentence, bhsa0):
    debug = (sentence.attrib['verse'] == 'GEN 24:65 (!!)')
    morphs = list(extract_morphemes(sentence))
    morphs.sort(key=lambda m: m.attrib[xml_id])
    m2b = {}
    tags = defaultdict(list)
    heads = {}
    idx = bhsa0
    if debug:
        print('#####', len(morphs), file=sys.stderr)
    for mi, m in enumerate(morphs):
        if debug:
            print('##', 'macula', m.text, 'bhsa', F.lex.v(idx), file=sys.stderr)
        while idx in bhsa_skip_nodes:
            idx += 1
        if is_np_second(m, idx):
            idx += 1
        mid = m.attrib[xml_id]
        tags[mid].append(m.attrib['parentrule'])
        if 'rulepiece' in m.attrib:
            tags[mid].append('role:'+m.attrib['rulepiece'])
        if 'uprule' in m.attrib:
            tags[mid].append('uprole:'+m.attrib['uprule'])
        tags[mid].append('mid:'+mid)
        if 'SDBH' in m.attrib:
            tags[mid].append('sdbh:'+m.attrib['SDBH'].replace(' ', ','))
        if 'oshb-strongs' in m.attrib:
            tags[mid].append('strong:'+m.attrib['oshb-strongs'])
        heads[mid] = m.attrib['head']
        if m.attrib['pos'] == 'suffix':
            if m.attrib['type'] == 'pronominal':
                m2b[mid] = str(idx-1) + 'p'
                continue
            elif m.attrib['type'] == 'paragogic nun':
                tags[m.attrib['head']].append('para_nun')
                continue
            elif m.attrib['type'] == 'paragogic he':
                tags[m.attrib['head']].append('para_he')
                continue
            elif m.attrib['type'] == 'directional he':
                tags[m.attrib['head']].append('dir_he')
                continue
        if is_merge_prefix(m, idx):
            continue
        if is_merge_main(m, idx):
            m2b[mid] = idx
            idx += 1
            continue
        if is_split_prefix(m, idx):
            m2b[mid] = idx + 1
            idx += 2
            continue
        ok, n = is_name_group(m, idx)
        if ok:
            m2b[mid] = idx
            idx += n
            continue
        if matches(m, idx):
            m2b[mid] = idx
            idx += 1
            continue
        print('NOMATCH', mid, idx, 'BHSA', F.voc_lex_utf8.v(idx), 'Macula', m.text, 'context', ' '.join((F.lex.v(i) or '_') + ':' + (F.lex_utf8.v(i) or '_') for i in range(idx-2,idx+3)), file=sys.stderr)
    for mid in sorted(m2b.keys()):
        wid = m2b[mid]
        head = heads[mid]
        tagstr = ''.join(f'<{x}>' for x in tags[mid])
        if head in m2b and '_' not in tags[mid]:
            head = 'w' + str(m2b[head])
        man = manual.get(f'w{wid}', [])
        if man:
            if man[0] != '_':
                head = man[0]
            if len(man) > 1:
                tagstr += f'<{man[1]}>'
        print(f'w{wid}\t{head}\t{tagstr}')

def process_sentence(sent):
    propogate_heads(sent)
    if sent.attrib['verse'] == 'GEN 1:6 (!!)':
        print(ET.tostring(sent, encoding='utf-8').decode('utf-8'), file=sys.stderr)
    distribute_heads(sent, sent.attrib['headword'], '_')
    c, v = sent.attrib['verse'].split()[-1].split(':')
    cl = L.u(1, otype='chapter')[0] + int(c) - 1
    vl = L.d(cl, otype='verse')[0] + int(v) - 1
    wl = L.d(vl, otype='word')[0]
    align_to_bhsa(sent, wl)

bhsa_skip_nodes = bhsa_skip_nodes.get(book, [])
macula_skip_nodes = macula_skip_nodes.get(book, [])

utils.load_volume(book, globals())

for fname in sorted(glob.glob(f'macula-hebrew/WLC/nodes/{book_names[book]}-*.xml')):
    tree = ET.parse(fname)
    for sent in tree.getroot().iter('Sentence'):
        process_sentence(sent)
