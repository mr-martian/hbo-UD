all: torah ruth-book

torah: genesis-book exodus-book leviticus-book numbers-book deuteronomy-book

current: genesis-book
background: exodus-book leviticus-book numbers-book deuteronomy-book
finished: ruth-book

temp/plain-cg3/%.txt: to-CG.py find_clause_root.py
	./to-CG.py $* | apertium-cleanstream -n | ./find_clause_root.py | cg-conv -al > $@

temp/parsed-cg3/%.txt: temp/plain-cg3/%.txt hbo.bin
	cat $< | vislcg3 -t -g hbo.bin | tail -n +4 > $@

temp/conv/%.conllu: temp/parsed-cg3/%.txt cg_to_conllu.py
	cat $< | ./cg_to_conllu.py $* > $@

temp/punct/%.conllu: temp/conv/%.conllu
	cat $< | udapy -s -q ud.FixPunct > $@

temp/merged/%.conllu: temp/%.punct.conllu
	./merge_punct.py $*

hbo.bin: hbo.cg3
	cg-comp $< $@

%-book: temp/merged/%.conllu data/checked/%.conllu data/manual/%.conllu
	./check.py $^
	./update_manual.py $*
	./filter-ready.py $*
	./rule-stats.py $*

%-report:
	./report.py $*

%-filter: %-book
	mkdir -p data/filter
	cat data/checkable/$*.conllu | udapy -s util.Filter delete_tree_if_node='node.deprel in ["parataxis", "appos"] or node.is_nonprojective()' > data/filter/$*.conllu

export:
	./export.py genesis 1-18 > UD_Ancient_Hebrew-PTNK/hbo_ptnk-ud-dev.conllu
	./export.py genesis 19-30 > UD_Ancient_Hebrew-PTNK/hbo_ptnk-ud-test.conllu
	./export.py genesis 31-50 > UD_Ancient_Hebrew-PTNK/hbo_ptnk-ud-train.conllu
	./export.py ruth 1-4 >> UD_Ancient_Hebrew-PTNK/hbo_ptnk-ud-train.conllu

.PRECIOUS: temp/parsed-cg3/%.txt
