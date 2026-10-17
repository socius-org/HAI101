# Lecture notes

Preliminary reading for the series, linked from the site's "Before the series" section.

## Introduction to Transformers and LLMs

Source: `transformers-src/` (LaTeX, by Nick Oh and Steven Feng). The site serves the built PDF
from `public/notes/HAI101-Introduction-to-Transformers-and-LLMs.pdf`, with its first page as
`public/img/notes-cover.jpg`.

Rebuild after editing (MiKTeX or TeX Live with latexmk):

    cd lecture-notes/transformers-src
    latexmk -pdf -interaction=nonstopmode main.tex
    cp main.pdf ../../public/notes/HAI101-Introduction-to-Transformers-and-LLMs.pdf
    python -c "import pymupdf as f; f.open('main.pdf')[0].get_pixmap(dpi=110).save('../../public/img/notes-cover.jpg')"

The version and date on the title page come from `\docversion` in `main.tex` and the build date.

Appendix D reproduces the gpt() function from Andrej Karpathy's microgpt
(https://karpathy.github.io/2026/02/12/microgpt/) under `transformers-src/code/`, his code as written
plus a comment block of ours at the top.
