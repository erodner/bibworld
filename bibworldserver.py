# Documentation of flask at http://flask.pocoo.org/docs/flask-docs.pdf
import flask
from flask import Flask, make_response, abort, send_file, request
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
parser.add_argument('--noxaccel', help='do not use X-Accel-Redirect (apache required)', action='store_true')
args = parser.parse_args()
bibfile = args.b
pdfdir = args.p
defaulttemplate = args.t
use_x_accel_redirect = not args.noxaccel
oldstamp = None

# fixed settings
# bibtex keys that will be exported and provided in the downloaded bibtex keys
exported_bibkeys = {'title', 'author', 'booktitle', 'pages', 'journal', 'year', 'volume', 'number'}

""" server initialization (loading bibtex keys and setting up the cache) """
def init():
    if oldstamp is None or oldstamp > os.path.getmtime(bibfile):
	    mybib = bibdb()
	    mybib.readFromBibTex ( bibfile )
	    mybib.addAuxFiles ( os.path.join( pdfdir, '%s.pdf' ), 'pdf' )
      # compatibility for the old format
	    mybib.addAuxFiles ( os.path.join( pdfdir, '%s.pdf.teaser.png' ), 'teaser' )
	    mybib.addAuxFiles ( os.path.join( pdfdir, '%s.teaser.png' ), 'teaser', removeIfUnavailable=False )
	    mybib.addAuxFiles ( os.path.join( pdfdir, '%s.presentation.pdf' ), 'presentation' )
	    mybib.addAuxFiles ( os.path.join( pdfdir, '%s.supplementary.pdf' ), 'supplementary' )

	    # add the references to the cache
	    cache.set('mybib', mybib, timeout=60*60*72)
    else:
	    print "Database is still up to date"
	    cache.set('mybib', mybib, timeout=60*60*72)
    
    print "Number of publications: ", len(mybib.getReferences())


#
# server initialization
#

# init server
init()

# start Flask server
app = Flask(__name__, template_folder=args.htmlroot, static_folder=args.htmlroot)

#
# Helper functions
#
def webserver_send_file ( fn, mimetype ):
    # http://stackoverflow.com/questions/5410255/preferred-method-for-downloading-a-file-generated-on-the-fly-in-flask
    basefn = fn.replace ( pdfdir, '/staticfiles/' ) 
    response = make_response()
    response.headers['Cache-Control']  = 'no-cache'
    response.headers['Content-Type']   = mimetype
    response.headers['X-Accel-Redirect'] = basefn
    print "Sending file %s as %s with X-Accel-Direct" % ( fn, basefn )
    return response

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
 
@app.route('/bibsearch/<term>')
def print_bibtexsearch(term):
    mybib = cache.get('mybib')
    if mybib is None:
        init()
        mybib = cache.get('mybib')

    refs = mybib.searchReferences(term)
    output = ""
    for bibid in refs:
        output = output + mybib.getBibtexEntry( bibid, newlinestr='<br>', exported_keys=exported_bibkeys ) + '<br>'
    return output

def send_aux_file( bibid, tag, mimetype ):
    mybib = cache.get('mybib')
    if mybib is None:
        init()
        mybib = cache.get('mybib')

    ref = mybib.getReference(bibid) 
    if tag in ref:
        if not use_x_accel_redirect:
            return send_file( ref[tag], cache_timeout=60 )
        else:
            return webserver_send_file( ref[tag], mimetype )
    else:
        print abort(404)


@app.route('/pdf/<bibid>')
@app.route('/pdf/<bibid>.pdf')
def print_pdf(bibid):
    return send_aux_file( bibid, 'pdf', "application/pdf" )

@app.route('/teaser/<bibid>')
@app.route('/teaser/<bibid>.png')
def print_teaser(bibid):
    return send_aux_file( bibid, 'teaser', "image/png" )

@app.route('/presentation/<bibid>')
@app.route('/presentation/<bibid>.pdf')
def print_presentation(bibid):
    return send_aux_file( bibid, 'presentation', "application/pdf" )

@app.route('/supplementary/<bibid>')
@app.route('/supplementary/<bibid>.pdf')
def print_supplementary(bibid):
    return send_aux_file( bibid, 'supplementary', "application/pdf" )




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

    oldstamp = None
    # reread everything
    init()   

    return flask.redirect('/')

#############################################################

from bibgraph import getGraphJSON
app.jinja_env.globals.update(getgraph=getGraphJSON)

if __name__ == '__main__':
    use_x_accel_redirect = False
    app.run(debug=True)
