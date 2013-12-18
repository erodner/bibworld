# Documentation of flask at http://flask.pocoo.org/docs/flask-docs.pdf
import flask
from flask import Flask, make_response, abort
from bibdb import bibdb
import argparse

# initialize cache 
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-b', help='Source Bibtex file', required=True)
parser.add_argument('--htmlroot', help='Template folder', default='example-template-jinja2')
parser.add_argument('-t', help='Default template', default='publist.html')
parser.add_argument('-p', help='PDF directory', default='.')
args = parser.parse_args()
bibfile = args.b
pdfdir = args.p
defaulttemplate = args.t

# fixed settings
# bibtex keys that will be exported and provided in the downloaded bibtex keys
exported_bibkeys = {'title', 'author', 'booktitle', 'pages', 'journal', 'year'}

""" server initialization (loading bibtex keys and setting up the cache) """
def init():
    mybib = bibdb()
    mybib.readFromBibTex ( bibfile )
    mybib.addPDFs ( pdfdir )

    # add the references to the cache
    cache.set('mybib', mybib)
    print "Number of publications: ", len(mybib.getReferences())


#
# server initialization
#

# init server
init()

# start Flask server
app = Flask(__name__, template_folder=args.htmlroot, static_folder=args.htmlroot)

#
# Main FLASK functions
#
@app.route('/all/<template>')
@app.route('/all/')
@app.route('/')
def start(template=None):
    mybib = cache.get('mybib')
    refs = mybib.getReferences()
    if not template:
        template = defaulttemplate
    return flask.render_template(template, refs=refs)

@app.route('/author/<author>')
@app.route('/author/<author>/<template>')
def print_author(author, template=None):
    mybib = cache.get('mybib')
    refs = mybib.getReferences(author=author)
    if not template:
        template = defaulttemplate
    return flask.render_template(template, refs=refs)


@app.route('/year/<year>')
@app.route('/year/<year>/<template>')
def print_year(year, template=None):
    mybib = cache.get('mybib')
    refs = mybib.getReferences(year=year)
    if not template:
        template = defaulttemplate
    return flask.render_template(template, refs=refs)

@app.route('/bib/<bibid>')
def print_bibtex(bibid):
    mybib = cache.get('mybib')
    return mybib.getBibtexEntry( bibid, newlinestr='<br>', exported_keys=exported_bibkeys )
 
@app.route('/pdf/<bibid>')
def print_pdf(bibid):
    mybib = cache.get('mybib')
    ref = mybib.getReference(bibid) 
    if 'pdf' in ref:
        print "Downloading PDF file"
        def generate():
            yield 'test'

        response = make_response(generate)
        response.headers["Content-Disposition"] = "attachment; filename=%s.pdf" % (bibid)
        return response
    else:
        print abort(404)

#############################################################


if __name__ == '__main__':
    app.run(debug=True)
 
