# Documentation of flask at http://flask.pocoo.org/docs/flask-docs.pdf
import flask
from flask import Flask, make_response, abort, send_file
from bibdb import bibdb
import argparse
import os
import subprocess

# initialize cache 
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-b', help='Source Bibtex file', default='/usr/local/virtualenvs/bibworld/bib/paper.bib')
parser.add_argument('--htmlroot', help='Template folder', default='example-template-jinja2')
parser.add_argument('-t', help='Default template', default='biborblist.html')
parser.add_argument('-p', help='PDF directory', default='/home/publications/')
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
    mybib.addTeaserImages ( pdfdir )

    # add the references to the cache
    cache.set('mybib', mybib, timeout=60*20)
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
    if mybib is None:
        init()
        mybib = cache.get('mybib')

    refs = mybib.getReferences()
    if not template:
        template = defaulttemplate
    return flask.render_template(template, refs=refs)

@app.route('/author/<author>')
@app.route('/author/<author>/<template>')
def print_author(author, template=None):
    mybib = cache.get('mybib')
    if mybib is None:
        init()
        mybib = cache.get('mybib')

    refs = mybib.getReferences(author=author)
    if not template:
        template = defaulttemplate
    return flask.render_template(template, refs=refs)

@app.route('/searchbyfield/<field>/<term>')
@app.route('/searchbyfield/<field>/<term>/<template>')
def print_searchfield(field, term, template=None):
    mybib = cache.get('mybib')
    if mybib is None:
        init()
        mybib = cache.get('mybib')

    kwargs = {field: term}
    refs = mybib.getReferences(**kwargs)
    if not template:
        template = defaulttemplate
    return flask.render_template(template, refs=refs)

@app.route('/search/<term>')
@app.route('/search/<term>/<template>')
def print_search(term, template=None):
    mybib = cache.get('mybib')
    if mybib is None:
        init()
        mybib = cache.get('mybib')

    refs = mybib.searchReferences(term)
    print refs
    if not template:
        template = defaulttemplate
    return flask.render_template(template, refs=refs)


@app.route('/year/<year>')
@app.route('/year/<year>/<template>')
def print_year(year, template=None):
    mybib = cache.get('mybib')
    if mybib is None:
        init()
        mybib = cache.get('mybib')

    refs = mybib.getReferences(year=year)
    if not template:
        template = defaulttemplate
    return flask.render_template(template, refs=refs)

@app.route('/bib/<bibid>')
def print_bibtex(bibid):
    mybib = cache.get('mybib')
    if mybib is None:
        init()
        mybib = cache.get('mybib')

    return mybib.getBibtexEntry( bibid, newlinestr='<br>', exported_keys=exported_bibkeys )
 
@app.route('/teaser/<bibid>')
def print_teaserimage(bibid):
    mybib = cache.get('mybib')
    if mybib is None:
        init()
        mybib = cache.get('mybib')

    ref = mybib.getReference(bibid) 
    if 'teaser' in ref:
        return send_file( ref['teaser'] )
    else:
        print abort(404)


@app.route('/pdf/<bibid>')
def print_pdf(bibid):
    mybib = cache.get('mybib')
    if mybib is None:
        init()
        mybib = cache.get('mybib')

    ref = mybib.getReference(bibid) 
    if 'pdf' in ref:
        return send_file( ref['pdf'] )
    else:
        print abort(404)

@app.route('/refresh')
def refresh():
    # try to perform a git update before the refresh
    gitdir = os.path.dirname( bibfile )

    gitmsg = 'No git installed or git error. Updating locally only from %s/%s.' % (bibfile, gitdir)

    try:
    	import git
        g = git.cmd.Git( gitdir )
        gitmsg = g.pull('origin', 'master')
    except git.GitCommandError, e:
        print "Error updating git repo at %s" % (gitdir)
        gitmsg = "Exception: %s" % (e)

 
    #    bashCommand = "export HOME=/usr/local/virtualenvs/bibworld/fakehome/; cd %s; git pull origin master" % (gitdir)
    #	 process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    # 	 gitmsg = process.communicate()[0]
   
    # try:	 
    #	gitmsg = subprocess.check_output(['git', '--git-dir', gitdir, 'pull', 'origin', 'master'], shell=True)
    # except Exception, e:
    #	print e
    #	gitmsg = "Exception: %s" % (e)

    print "gitmsg: %s" % (gitmsg)

    # reread everything
    init()   

    return flask.redirect('/')

#############################################################

if __name__ == '__main__':
    app.run(debug=True)
