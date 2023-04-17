#!/usr/bin/env python3

import utils
import xml.etree.ElementTree as ET
import glob
import sys
import unicodedata
from collections import defaultdict

xml_id = '{http://www.w3.org/XML/1998/namespace}id'

def propogate_heads(node):
    if node.tag == 'm':
        node.attrib['headword'] = node.attrib[xml_id]
        return
    for ch in node:
        propogate_heads(ch)
    if 'Head' not in node.attrib:
        node.attrib['Head'] = '0'
    h = int(node.attrib['Head'])
    node.attrib['headword'] = node[h].attrib['headword']

def distribute_heads(node, headword, parentrule):
    if node.tag == 'm':
        node.attrib['parentrule'] = parentrule
        if node.attrib[xml_id] != headword:
            node.attrib['head'] = headword
        else:
            node.attrib['head'] = '0'
    else:
        n = node.attrib.get('Head', '*')
        r = node.attrib.get('Rule', parentrule)
        for i, ch in enumerate(node):
            if n == '*' or int(n) == i:
                distribute_heads(ch, headword, parentrule)
            else:
                distribute_heads(ch, node.attrib['headword'], r)

def skip(c):
    if ord(c) > 0x5ea:
        return True # trop
    if ord(c) == 0x5c3:
        return True # sof pasuq
    if ord(c) < 0x5d0:
        return True # vowel
    return False
                
def clean(s):
    s2 = ''.join(c for c in (s or '').strip() if not skip(c))
    #s3 = s2.replace(
    return unicodedata.normalize('NFC', s2)
                
def matches(node, idx):
    bt = T.text(idx).strip(F.trailer_utf8.v(idx))
    mt = node.text
    btc = clean(bt)
    mtc = clean(mt)
    if btc == mtc:
        return True
    if F.prs.v(idx) and btc.startswith(mtc):
        return True
    print(btc, mtc)
    return False

moved_nodes = [
    (46, 'o010010040051'),
    (1160, 'o010020250031'),
    (5805, 'o010120170051'),
    (5806, 'o010120170061'),
    (5869, 'o010130010031'),
    (5870, 'o010130010032'),
    (6246, 'o010140020171'), # var spelling
    (6429, 'o010140120042'),
    (6430, 'o010140120051'),
    (8155, 'o010180200061'),
    (8159, 'o010180200091'),
    (8556, 'o010190070041'),
    (11428, 'o010240150081'),
    (11586, 'o010240240051'),
    (11763, 'o010240330022'),
    (12371, 'o010240650061'),
    (13157, 'o010260090061'),
    (14343, 'o010270390091'),
    (14344, 'o010270390101'),
    (15630, 'o010300020081'),
    (15905, 'o010300200041'),
    (17401, 'o010310530071'),
    (17402, 'o010310530081'),
    (18401, 'o010330170151'), # bad lemma
    (19170, 'o010350060021'),
    (19324, 'o010350140081'),
    (19325, 'o010350140091'),
    (19603, 'o010360050051'), # bad lemma
    (19771, 'o010360140151'), # bad lemma
    (20518, 'o010370190081'),
    (22049, 'o010400080061'),
    (22077, 'o010400090101'),
    (22078, 'o010400090102'),
    (22391, 'o010410030051'),
    (22392, 'o010410030061'),
    (22393, 'o010410030071'),
    (22394, 'o010410030081'),
    (22395, 'o010410030082'),
    (22628, 'o010410150081'),
    (22690, 'o010410190051'),
    (22691, 'o010410190061'),
    (23257, 'o010410490041'),
    (23258, 'o010410490042'),
    (23259, 'o010410490051'),
    (23260, 'o010410490052'),
    (23631, 'o010420130051'),
    (23812, 'o010420220161'),
    (23978, 'o010420320031'),
    (24889, 'o010440030041'),
    (25687, 'o010450120031'),
    (26541, 'o010460340091'),
    (26542, 'o010460340101'),
    (26543, 'o010460340111'),
    (26544, 'o010460340121'),
    (27467, 'o010480090061'),
    (27593, 'o010480150101'),
    (27594, 'o010480150111'),
    (27595, 'o010480150112'),
    (27893, 'o010490090061'),
    (27916, 'o010490100121'),
    (27975, 'o010490150031'),
    (27981, 'o010490150071'),
    (28521, 'o010500140031'),
    (28667, 'o010500220021'),
]
b2m_moved = dict(moved_nodes)
m2b_moved = {b:a for a,b in moved_nodes}

mac_skip_nodes = ['o010130150101', 'o010130150102', 'o010140120091', 'o010250320101', 'o010270290042', 'o010280130201', 'o010280130202', 'o010280130203', 'o010280140151', 'o010280140152', 'o010280140153', 'o010320190051', 'o010390220201', 'o010410050101', 'o010410050111', 'o010410050112', 'o010410220091', 'o010410220101', 'o010410220102', 'o010420120071', 'o010420120081', 'o010420120082', 'o010430280092', 'o010480010141']
bhsa_skip_nodes = [6152, 6154, 6428, 7287, 10176, 10186, 10204, 10646, 11326, 12319, 12370, 12733, 13599, 14112, 14522, 14581, 14606, 14675, 16564, 16705, 17279, 17802, 18416, 19236, 20517, 24704, 26004, 26066, 26227, 27317, 28426, 28427, 28460, 28461]

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

def align_to_bhsa(node, idx, add_tags):
    if node.tag == 'm':
        if node.attrib[xml_id] in m2b_moved:
            node.attrib['bhsa'] = m2b_moved[node.attrib[xml_id]]
            return idx
        while idx in b2m_moved or idx in bhsa_skip_nodes:
            idx += 1
        if node.attrib[xml_id] in mac_skip_nodes:
            return idx
        if node.attrib['pos'] == 'suffix':
            if node.attrib['type'] == 'pronominal':
                node.attrib['bhsa'] = str(idx-1) + 'p'
                return idx
            elif node.attrib['type'] == 'paragogic nun':
                add_tags[node.attrib['head']].append('para_nun')
                return idx
            elif node.attrib['type'] == 'paragogic he':
                add_tags[node.attrib['head']].append('para_he')
                return idx
            elif node.attrib['type'] == 'directional he':
                add_tags[node.attrib['head']].append('dir_he')
                return idx
        if is_merge_prefix(node, idx):
            return idx
        if is_np_second(node, idx):
            return idx + 1
        if is_merge_main(node, idx):
            node.attrib['bhsa'] = idx
            return idx + 1
        if matches(node, idx):
            node.attrib['bhsa'] = idx
            return idx + 1
        print('NOMATCH', node.attrib[xml_id], idx, 'BHSA', F.voc_lex_utf8.v(idx), 'Macula', node.text, 'context', ' '.join(F.lex_utf8.v(i) for i in range(idx-2,idx+3)), file=sys.stderr)
        return idx
    elif node.tag == 'c':
        return align_to_bhsa(node[0], idx, add_tags)
    else:
        for ch in node:
            idx = align_to_bhsa(ch, idx, add_tags)
        return idx

def process_sentence(sent):
    propogate_heads(sent)
    distribute_heads(sent, sent.attrib['headword'], '_')
    add_tags = defaultdict(list)
    c, v = sent.attrib['verse'].split()[-1].split(':')
    cl = L.u(1, otype='chapter')[0] + int(c) - 1
    vl = L.d(cl, otype='verse')[0] + int(v) - 1
    wl = L.d(vl, otype='word')[0]
    align_to_bhsa(sent, wl, add_tags)
    data = {}
    for m in sent.iter('m'):
        if 'bhsa' in m.attrib:
            data[m.attrib[xml_id]] = [m.attrib['bhsa'], m.attrib['parentrule'], m.attrib['head']]
    for k in sorted(data.keys()):
        wid, rl, head = data[k]
        tags = f'<{rl}>' + ''.join(f'<{x}>' for x in add_tags[k])
        if head in data:
            head = 'w' + str(data[head][0])
        print(f'w{wid}\t{head}\t{tags}')

book_names = {
    'genesis': '01-Gen',
    'exodus': '02-Exo',
    'ruth': '08-Rut',
}

book = sys.argv[1]

utils.load_volume(book, globals())

for fname in sorted(glob.glob(f'macula-hebrew/nodes/{book_names[book]}-*.xml')):
    tree = ET.parse(fname)
    for sent in tree.getroot().iter('Sentence'):
        process_sentence(sent)
