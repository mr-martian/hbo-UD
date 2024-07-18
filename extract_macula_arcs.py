#!/usr/bin/env python3

import utils
import xml.etree.ElementTree as ET
import glob
import sys
import unicodedata
from collections import defaultdict

xml_id = '{http://www.w3.org/XML/1998/namespace}id'

HEAD_OVERRIDE = {
    'PpAdvp': 1,
    'PpRelp': 0, # TODO: should we just use case:outer for this instead?

    '2PpaPp': 0,
    'QuanNP': 0,

    '2CLaCL': 0,
    '2Np': 0,
    '2NpaNpaNp': 0,
    '3NpaNp': 0,
    'AdjpaAdjp': 0,
    'CLaCL': 0,
    'CLandCL2': 0,
    'ClCl': 0,
    'Conj3CL': 0,
    'Conj4Np': 0,
    'Conj4Pp': 0,
    'Conj5Np': 0,
    'NP3NP': 0,
    'NpaNp': 0,
    'NPaNPaNPNPaNP': 0,
    'NPaNPNP': 0,
    'NPaNPNPaNP': 0,
    'NpNpNp': 0,
    'NPNPNPaNPaNP': 0,
    'NpNpNpNp': 0,
    'NpPp': 0,
    'NumpAndNump': 0,
    'NumpNump': 0,
    'PPandPP': 0,
    'PpaPpPpaPp': 0,
    'Relp3Relp': 0,


    'AdjpAdjpandAdjp': 0,
    'AdjpandAdjpAdjp': 0,
    'AdvpandAdvp': 0,
    'AdvpandPp': 0,
    'CLandCL2': 0,
    'NPandPP2np': 0,
    'NumpAndNump': 0,
    'PPandPP': 0,
    'PpPpPpPpandPp': 0,
    'PpPpPpandPp': 0,
    'PpPpPpandPpPp': 0,
    'PpPpandPpPp': 0,
    'PpandAdvp': 0,
    'PpandPpPp': 0,
    'RelpandRelp': 0,
    'VPandVP': 0,

    'Conj11Np': 0,
    'Conj2Pp': 0,
    'Conj3Adjp': 0,
    'Conj3CL': 0,
    'Conj3Np': 0,
    'Conj3Pp': 0,
    'Conj4Adjp': 0,
    'Conj4CL': 0,
    'Conj4Np': 0,
    'Conj4Pp': 0,
    'Conj5CL': 0,
    'Conj5Np': 0,
    'Conj5Pp': 0,
    'Conj6Np': 0,
    'Conj6Pp': 0,
    'Conj7Np': 0,
    'Conj7Pp': 0,
    'Conj8Np': 0,
    'Conj9Np': 0,

    '12Np': 0,
    '2Advp_h1': 0,
    '3Adjp': 0,
    '3NpaNp': 0,
    '4NpaNp': 0,
    '7Np': 0,

    'NP10NP': 0,
    'NP3NP': 0,
    'NPnp4NP': 0,
    'NPnp5NP': 0,
    'Np5Np': 0,
    'NpNp5': 0,
    'NpNp6': 0,
    'NpNpNp11': 0,
    'PP8PP': 0,
    'PP9PP': 0,
    'PPPP4': 0,
    'PPPP5': 0,
    'PpPp9': 0,
    'Relp3Relp': 0,
    'Relp5Relp': 0,
    'VP3VP': 0,
    'VpVp2V3': 0,
    'Vpvp2V1': 0,
    'ppPP5PP': 0,
    'ppPP6PP': 0,
    'ppappPP5PP': 0,

}

def is_nouny(node):
    prep_noun_lemmas = [
        '8478', # תחת
        '5978', # עמד
    ]
    if node.attrib.get('Cat') == 'np':
        return True
    elif node.attrib.get('lemma') in prep_noun_lemmas:
        return True
    else:
        return any(is_nouny(ch) for ch in node)

def propogate_heads(node):
    if node.tag == 'm':
        node.attrib['headword'] = node.attrib[xml_id]
        if node.attrib.get('lemma') == '1961':
            if node.attrib.get('type') == 'jussive':
                node.attrib['copula'] = 'juss'
            else:
                node.attrib['copula'] = 'yes'
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
    elif r and '-' in r:
        ls = r.split('-')
        if 'V' in ls:
            v = ls.index('V')
            cop = node[v].attrib.get('copula')
            if cop in ['yes', 'juss']:
                if 'O' in ls:
                    node.attrib['Head'] = str(ls.index('O'))
                elif 'PP' in ls and cop != 'juss':
                    node.attrib['Head'] = str(ls.index('PP'))
    elif r == 'PpPp' and is_nouny(node[0]):
        node.attrib['Head'] = '0'
    elif r == '2Pp':
        if is_nouny(node[0]):
            node.attrib['Head'] = '0'
        else:
            node.attrib['Head'] = '1'
    elif r == 'ClClCl' and node[0].attrib.get('Rule') == 'Intj2CL':
        node.attrib['Head'] = '1'
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
    else:
        n = node.attrib.get('Head', '*')
        r = node.attrib.get('Rule', parentrule)
        roles = r.split('-')
        if len(node) == 1:
            roles = [rulepiece]
        elif r == 'Np-Appos':
            roles = [rulepiece, 'Appos']
        elif len(roles) != len(node):
            roles = [None] * len(node)
            roles[int(n)] = rulepiece
        for i, (ch, role) in enumerate(zip(node, roles)):
            if n == '*' or int(n) == i:
                distribute_heads(ch, headword, parentrule, role)
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
    'genesis': [28427, 28426, 28460, 28461, 16564],
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

def is_merge_prefix(node, idx):
    if node.attrib.get('lemma') == 'l' and F.lex.v(idx) in ['LMH', 'LKN']:
        return True
    return False

def is_merge_main(node, idx):
    if F.lex.v(idx) == 'LMH' and node.attrib.get('lemma') == '4100':
        return True
    if F.lex.v(idx) == 'LKN' and node.attrib.get('lemma') == '3651 c':
        return True
    return False

def is_np_second(node, idx):
    if F.lex.v(idx) == '>RM/' and F.lex.v(idx-1) == 'PDN/':
        return True
    return False

def is_name_group(node, idx):
    lm = node.attrib.get('lemma')
    if lm in name_groups:
        for i in range(len(name_groups[lm])):
            if F.lex.v(idx+i) != name_groups[lm][i]:
                return (False, 0)
        return (True, len(name_groups[lm]))
    return (False, 0)

def extract_morphemes(node):
    if node.tag == 'm':
        yield node
    elif node.tag == 'c':
        yield node[0]
    else:
        for ch in node:
            yield from extract_morphemes(ch)

def align_to_bhsa(sentence, bhsa0):
    morphs = list(extract_morphemes(sentence))
    morphs.sort(key=lambda m: m.attrib[xml_id])
    m2b = {}
    tags = defaultdict(list)
    heads = {}
    idx = bhsa0
    for m in morphs:
        while idx in bhsa_skip_nodes:
            idx += 1
        mid = m.attrib[xml_id]
        tags[mid].append(m.attrib['parentrule'])
        if 'rulepiece' in m.attrib:
            tags[mid].append('role:'+m.attrib['rulepiece'])
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
        if is_np_second(m, idx):
            continue
        if is_merge_main(m, idx):
            m2b[mid] = idx
            idx += 1
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
        print(f'w{wid}\t{head}\t{tagstr}')

def process_sentence(sent):
    propogate_heads(sent)
    distribute_heads(sent, sent.attrib['headword'], '_')
    c, v = sent.attrib['verse'].split()[-1].split(':')
    cl = L.u(1, otype='chapter')[0] + int(c) - 1
    vl = L.d(cl, otype='verse')[0] + int(v) - 1
    wl = L.d(vl, otype='word')[0]
    align_to_bhsa(sent, wl)

book_names = {
    'genesis': '01-Gen',
    'exodus': '02-Exo',
    'ruth': '08-Rut',
}

book = sys.argv[1]

bhsa_skip_nodes = bhsa_skip_nodes.get(book, [])

utils.load_volume(book, globals())

for fname in sorted(glob.glob(f'macula-hebrew/nodes/{book_names[book]}-*.xml')):
    tree = ET.parse(fname)
    for sent in tree.getroot().iter('Sentence'):
        process_sentence(sent)
