all: torah ruth-book

torah: genesis-book exodus-book leviticus-book numbers-book deuteronomy-book

%.corpus.cg3.txt: to-CG.py
	./to-CG.py $* | cg-conv -al > $@

%.parsed.cg3.txt: %.corpus.cg3.txt hbo.bin
	cat $< | vislcg3 -t -g hbo.bin | tail -n +4 > $@

%.parsed.conllu: %.parsed.cg3.txt cg_to_conllu.py
	cat $< | ./cg_to_conllu.py $* > $@

hbo.bin: hbo.cg3
	cg-comp $< $@

%-book: %.parsed.conllu %.checked.conllu
	./check.py $^
	./clean_checked.py $*
	./filter-ready.py $*

%-report:
	./report.py $*
