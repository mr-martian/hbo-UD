all: torah ruth-book

torah: genesis-book exodus-book leviticus-book numbers-book deuteronomy-book

current: genesis-book
background: exodus-book leviticus-book numbers-book deuteronomy-book
finished: ruth-book

temp/plain-cg3/%.txt: to-CG.py find_clause_root.py
	mkdir -p temp/plain-cg3
	./to-CG.py $* | apertium-cleanstream -n | ./find_clause_root.py | cg-conv -al > $@

temp/macula-arcs/%.tsv: extract_macula_arcs.py data/manual-arcs/%.tsv
	mkdir -p temp/macula-arcs
	./extract_macula_arcs.py $* > $@

temp/macula-cg3/%.txt: to-CG.py temp/macula-arcs/%.tsv add-macula.py
	mkdir -p temp/macula-cg3
	./to-CG.py $* | apertium-cleanstream -n | ./add-macula.py temp/macula-arcs/$*.tsv | cg-conv -al | sed -E 's/(txt:[[:digit:]]+)/<\1>/g' > $@

temp/macula-parsed-cg3/%.txt: temp/macula-cg3/%.txt hbo-macula.bin
	mkdir -p temp/macula-parsed-cg3
	cat $< | vislcg3 -t -g hbo-macula.bin | tail -n +4 > $@

temp/macula-merged/%.conllu: temp/macula-parsed-cg3/%.txt cg_to_conllu.py
	mkdir -p temp/macula-merged
	cat $< | ./cg_to_conllu.py $* | ./merge_punct.py > $@

temp/parsed-cg3/%.txt: temp/plain-cg3/%.txt hbo.bin
	mkdir -p temp/parsed-cg3
	cat $< | vislcg3 -t -g hbo.bin | tail -n +4 > $@

temp/merged/%.conllu: temp/parsed-cg3/%.txt cg_to_conllu.py
	mkdir -p temp/conv temp/merged
	cat $< | ./cg_to_conllu.py $* > temp/conv/$*.conllu
	cat temp/conv/$*.conllu | ./merge_punct.py > $@

hbo.bin: hbo-with.cg3
	cg-comp $< $@

hbo-macula.bin: hbo-macula.cg3
	cg-comp $< $@

%-book: temp/macula-merged/%.conllu data/checked/%.conllu data/manual/%.conllu
	./check.sh $*
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

coref/base/ruth.conllu: data/checked/ruth.conllu data/manual/ruth.conllu
	mkdir -p coref/base
	./export.py ruth 1-4 > $@

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

.PRECIOUS: temp/parsed-cg3/%.txt temp/merged/%.conllu temp/macula-parsed-cg3/%.txt temp/macula-merged/%.conllu temp/macula-cg3/%.txt
