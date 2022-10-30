all: torah ruth-book

torah: genesis-book exodus-book leviticus-book numbers-book deuteronomy-book

current: genesis-book
background: exodus-book leviticus-book numbers-book deuteronomy-book
finished: ruth-book

temp/plain-cg3/%.txt: to-CG.py find_clause_root.py
	mkdir -p temp/plain-cg3
	./to-CG.py $* | apertium-cleanstream -n | ./find_clause_root.py | cg-conv -al > $@

temp/parsed-cg3/%.txt: temp/plain-cg3/%.txt hbo.bin
	mkdir -p temp/parsed-cg3
	cat $< | vislcg3 -t -g hbo.bin | tail -n +4 > $@

temp/merged/%.conllu: temp/parsed-cg3/%.txt cg_to_conllu.py
	mkdir -p temp/conv temp/punct temp/merged
	cat $< | ./cg_to_conllu.py $* > temp/conv/$*.conllu
	cat temp/conv/$*.conllu | udapy -s -q ud.FixPunct > temp/punct/$*.conllu
	./merge_punct.py $*

hbo.bin: hbo.cg3
	cg-comp $< $@

%-book: temp/merged/%.conllu data/checked/%.conllu data/manual/%.conllu
	./check.py $*
	./update_manual.py $*
	./filter-ready.py $*
	./rule-stats.py $*

%-report:
	./report.py $*

%-filter: %-book
	mkdir -p data/filter
	cat data/checkable/$*.conllu | udapy -s util.Filter delete_tree_if_node='node.deprel in ["parataxis", "appos"] or node.is_nonprojective()' > data/filter/$*.conllu

coref/base/genesis.conllu: data/checked/genesis.conllu data/manual/genesis.conllu
	mkdir -p coref/base
	./export.py genesis 1-50 > $@

coref/pred/%.txt: coref/base/%.conllu
	mkdir -p coref/pred
	python3 xrenner/xrenner/xrenner.py -m ./xrhbo coref/base/$*.conllu > $@

coref/pred-spans/%.txt: coref/pred/%.txt
	mkdir -p coref/pred-spans
	./conv_xrenner.py $*

export:
	./export.py genesis 1-18 > UD_Ancient_Hebrew-PTNK/hbo_ptnk-ud-dev.conllu
	./export.py genesis 19-30 > UD_Ancient_Hebrew-PTNK/hbo_ptnk-ud-test.conllu
	./export.py genesis 31-50 > UD_Ancient_Hebrew-PTNK/hbo_ptnk-ud-train.conllu
	./export.py ruth 1-4 >> UD_Ancient_Hebrew-PTNK/hbo_ptnk-ud-train.conllu

.PRECIOUS: temp/parsed-cg3/%.txt temp/merged/%.conllu
