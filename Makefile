all: torah ruth-book

torah: genesis-book exodus-book leviticus-book numbers-book deuteronomy-book

current: genesis-book ruth-book
background: exodus-book leviticus-book numbers-book deuteronomy-book
finished:

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
	./clean_checked.py $*
	./filter-ready.py $*

%-report:
	./report.py $*

export:
	./export.py genesis 1 5 > UD_Ancient_Hebrew-PTNK/hbo_ptnk-ud-test.conllu

.PRECIOUS: %.parsed.cg3.txt
