# coding=utf-8
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader

from functools import partial

# needed for advanced templates with parameters
#from flask import request, test_request_context


def url_for(typeparameter, filename, staticroot):
    return staticroot + filename

class requestclass:
    args = {}
    def __init__(self, args):
        self.args = args
     


def bib2html ( refs, outfn, templatedir, templatename, staticroot="", rooturl="" ):
    env = Environment(loader=FileSystemLoader(templatedir))
    request = requestclass(args = {})
    env.globals['url_for'] = partial(url_for, staticroot=staticroot)
    env.globals['request'] = request
    #with test_request_context('/hello', method='POST'):
    template = env.get_template( '%s.html' % (templatename) )
    rtext = template.render(refs=refs, rooturl=rooturl)
    with open(outfn, 'w') as outf:
        outf.write( rtext.encode('utf8') )
