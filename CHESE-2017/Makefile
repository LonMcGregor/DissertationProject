all:: 17-chese.pdf

.PHONY : FORCE_MAKE

TEXMAINFILES=17-chese.tex
PDFMAINFILES=$(TEXMAINFILES:.tex=.pdf)

all:: $(PDFMAINFILES)

onchage:
	while inotifywait -e close_write 17-chese.tex Peer-testing.bib ; do latexmk -pdf 17-chese.tex ; done


clean: FORCE_MAKE
	latexmk -C -bibtex $(TEXMAINFILES)
	rm -f comment.cut
	rm -fr auto

%.pdf : %.tex FORCE_MAKE
	latexmk -pdf -bibtex -use-make $<

# dia
%.eps: %.dia
	dia --export $@ $<

%.pdf: %.eps
	epstopdf --outfile=$@ $<
