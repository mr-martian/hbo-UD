all: generated.conllu checkable.conllu check

generated.conllu: generated.cg3.txt cg_to_conllu.py
	cat $< | ./cg_to_conllu.py | tail -n +14 > $@

generated.cg3.txt: hbo.bin to-CG.py
	./to-CG.py | tail -n +14 | cg-conv -al | vislcg3 -t -g hbo.bin | tail -n +4 > $@

hbo.bin: hbo.cg3
	cg-comp $< $@

check: generated.conllu
	./check.py $< checked.conllu
	./clean_checked.py
	./report.py

checkable.conllu: generated.conllu checked.conllu
	./filter-ready.py
