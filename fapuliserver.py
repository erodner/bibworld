# Documentation of flask at http://flask.pocoo.org/docs/flask-docs.pdf
import flask
from flask import Flask
from bibdb import bibdb
import argparse
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()

# Get the file name
parser = argparse.ArgumentParser()
parser.add_argument('-b', help='Source Bibtex file', required=True)
parser.add_argument('--htmlroot', help='Template folder', default='example-template-jinja2')
args = parser.parse_args()
bibfile = args.b

def init():
    mybib = bibdb()
    mybib.readFromBibTex ( bibfile )
    refs = mybib.getReferences()
    cache.set('refs', refs)
    print "Number of publications: ", len(refs)


init()

app = Flask(__name__, template_folder=args.htmlroot, static_folder=args.htmlroot)

@app.route('/')
def start():
    refs = cache.get('refs')
    return flask.render_template('publist.html', refs=refs)

if __name__ == '__main__':
    app.run(debug=True)
