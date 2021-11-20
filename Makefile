all: generated.conllu

generated.conllu: generated.cg3.txt cg_to_conllu.py
	cat $< | ./cg_to_conllu.py | grep -v IPython | grep -v 'This is' | grep -v 'Api reference' | grep -v 'features found' > $@

generated.cg3.txt: hbo.bin to-CG.py
	./to-CG.py | grep -v IPython | grep -v 'This is' | grep -v 'Api reference' | grep -v 'features found' | cg-conv -al | vislcg3 -g hbo.bin > $@

hbo.bin: hbo.cg3
	cg-comp $< $@

check: generated.conllu
	./check.py $< checked.conllu
	./report.py
