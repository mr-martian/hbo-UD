# Unresolved
- @ccomp vs @xcomp vs @advcl
  - @xcomp for כי (e.g. 144)
- why does Annotatrix object to @punct depending on SCONJ?
  - probably all the punctuation is a bit off from guidelines
- 226 is weird in the underlying corpus
- is @advmod really the best way to handle infinitive absolute?
  - while it's @advmod, they're retagged VERB→ADV
- is it really main @ccomp לאמר @ccomp quote?
  - or should it be main @xcomp לאמר?
- where does @appos attach?
- adonai elohim - @flat:name or @appos ? (e.g. 65)
- גם־הוא e.g. 84
  - @advmod of a NOUN feels weird
- order of clause building - @det before NUM - 4023
- 70 double object weirdness
- delete CB around relative clauses
- should G139 actually have @ccomp rather than @xcomp? also G191

# Resolved - unimplemented
- A B וC - B should get @conj
  - what about A וB C וD ?
    - all @conj (e.g. 674)
- retag מאד e.g. 31
- (subs) that function like (prep)
- @conj vs @appos vs @parataxsis
  - @conj if @cc present anywhere
  - @appos if NOUN NOUN in same phrase
  - @parataxsis if adjacent clauses
- attachment of particples 1005
  - in smixut retag to NOUN if in same phrase
  - @acl if not
- objects of particples (@compound or @obj?) e.g. 483
  - @obj
- retokenize so we don't have words with spaces
  - e.g. 842
- @obl vs @nmod for verb-less sentences (e.g. 243)
  - @nmod if TF puts them in the same phrase (e.g. 172)
- אחד ממנו - "one of us"
  - PRON as @nmod of NUM, following English GUM

# Resolved - implemented
- should any verb+prep combos get @obj?
  - no
- numbers in smixut e.g. 190
  - @nummod and @compound over them
- @obl vs @iobj
  - per guidelines @obl
