# Documentation of flask at http://flask.pocoo.org/docs/flask-docs.pdf
import flask
from flask import Flask
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
args = parser.parse_args()
bibfile = args.b
defaulttemplate = args.t

# server initialization
def init():
    mybib = bibdb()
    mybib.readFromBibTex ( bibfile )

    # add the references to the cache
    cache.set('mybib', mybib)
    print "Number of publications: ", len(mybib.getReferences())


# init server
init()

# start Flask server
app = Flask(__name__, template_folder=args.htmlroot, static_folder=args.htmlroot)


@app.route('/<template>')
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


#############################################################


if __name__ == '__main__':
    app.run(debug=True)
 
