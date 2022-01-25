all: torah ruth-book

torah: genesis-book exodus-book leviticus-book numbers-book deuteronomy-book

current: genesis-book
background: exodus-book leviticus-book numbers-book deuteronomy-book
finished: ruth-book

%.corpus.cg3.txt: to-CG.py find_clause_root.py
	./to-CG.py $* | apertium-cleanstream -n | ./find_clause_root.py | cg-conv -al > $@

%.parsed.cg3.txt: %.corpus.cg3.txt hbo.bin
	cat $< | vislcg3 -t -g hbo.bin | tail -n +4 > $@

%.cg3.conllu: %.parsed.cg3.txt cg_to_conllu.py
	cat $< | ./cg_to_conllu.py $* > $@

%.punct.conllu: %.cg3.conllu
	cat $< | udapy -s -q ud.FixPunct > $@

%.parsed.conllu: %.punct.conllu
	./merge_punct.py $*

hbo.bin: hbo.cg3
	cg-comp $< $@

%-book: %.parsed.conllu %.checked.conllu
	./check.py $^
	./filter-ready.py $*

%-report:
	./report.py $*

%-filter: %-book
	cat $*.checkable.conllu | udapy -s util.Filter delete_tree_if_node='node.deprel in [] or node.is_nonprojective()' > $*.filter.conllu
#	cat $*.checkable.conllu | udapy -s util.Filter keep_tree_if_node='node.deprel in ["appos", "nmod"]' > $*.filter.conllu

export:
	./export.py genesis 1 2 3 4 5 6 7 8 9 10 11 12 > UD_Ancient_Hebrew-PTNK/hbo_ptnk-ud-test.conllu
	./export.py ruth 1 2 3 4 >> UD_Ancient_Hebrew-PTNK/hbo_ptnk-ud-test.conllu

.PRECIOUS: %.parsed.cg3.txt
