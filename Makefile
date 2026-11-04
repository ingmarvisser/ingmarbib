.PHONY: cv clean

cv: cv_pubs.pdf

cv_pubs.pdf: cv_pubs.tex ingmar.bib
	latexmk -pdf -bibtex cv_pubs.tex

clean:
	latexmk -C cv_pubs.tex
	rm -f cv_pubs.bbl cv_pubs.bcf cv_pubs.run.xml
