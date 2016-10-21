# Bibworld - easy publication lists with flask

Bibworld is a tool to create HTML publications lists from bibtex files and directories with corresponding PDFs and teaser images.

Author: Erik Rodner (Erik.Rodner (at) uni-jena.de)

The dynamic component of bibworld is based on flask (http://flask.pocoo.org/docs/) and Jinja2 (http://jinja.pocoo.org/docs/).

# Demo system

The computer vision group in Jena is running bibworld to list and organize their publications: ``http://hera.inf-cv.uni-jena.de:6680/author/Rodner``

# Using bibworld

Bibworld can be used to create static HTML files of your publication list or dynamic webpages. 
To create a static webpage the script bib2template.py can be used:

```
python bib2template.py --engine jinja2 -b mypublications.bib -t example-template-jinja2/publist.html -o test.html
```

The static interface of bibworld is limited and we strongly recommend the dynamic interface with flask and a proper webserver. In the default setting,
bibworld searches for teaser images and pdf documents in a predefined directory (`/home/dbv/publications/` for our case). The PDF file names have to be set according to the
BibTeX identification strings, e.g., `Rodner09:LFE` results in `Rodner09:LFE.pdf`. Furthermore, the standard template `biborblist.html` searches for teaser images, e.g., for
the BibTeX entry `Rodner09:LFE` the teaser image `Rodner09:LFE.pdf.teaser.png` will be shown if it is available.
We recommend to use bibworld together with a git repository containing the BibTeX file itself, which allows for proper version control.

Further features:
* You can access the publications of single authors for example by `http://yourwebserverurl/author/Rodner` searching for publications with the text Rodner in the authors field
* Publications of single years: `http://yourwebserverurl/year/2013`
* Teaser images: `http://yourwebserverurl/teaser/Rodner09:LFE(.png)`
* PDF documents: `http://yourwebserverurl/pdf/Rodner09:LFE(.pdf)`
* Supplementary PDF documents: `http://yourwebserverurl/supplementary/Rodner09:LFE(.pdf)`
* Presentation slides: `http://yourwebserverurl/presentation/Rodner09:LFE(.pdf)`
* Refresh database: `http://yourwebserverurl/pdf/Rodner09:LFE` (this feature is still experiment and requires a bibtex file directly in the top level of a git repo)
* Search for terms: `http://yourwebserverurl/search/Erik` this searches for Erik in every field of a BibTeX item, you can also specify regular expressions here
* Search for terms in specific fields: `http://yourwebserverurl/searchbyfield/title/Gaussian%20Process` this searches for the text `Gaussian Process` only in the field `title`
* Plain BibTeX entries: `http://yourwebserverurl/bib/Rodner09:LFE` (only a certain subset of the keys will be exported as specified in the source code: `exported_bibkeys = {'title', 'author', 'booktitle', 'pages', 'journal', 'year'}`
* Plain BibTeX entries for a search result: `http://yourwebserverurl/bibsearch/Rodner`

Templates
--------------------------------------------

Bibworld can be used with Jinja2 templates and you can build own webpage layout by simplying adapting them and adding new styles. Examples are provided in the `example-template-jinja2/` directory.


Deploying bibworld
--------------------------------------------

There are many ways to deploy a flask app. An easy way is to use the nginx webserver and uwsgi as a middleware component (with python and http plugin!). An example
nginx and uwsgi config is part of this package. Furthermore, there is also an installation script that can be used to setup up a virtual environment (deploy-examples/).



