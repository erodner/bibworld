# coding=utf-8
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader

def bib2html ( refs, outfn, templatedir, templatename ):
    env = Environment(loader=FileSystemLoader(templatedir))
    template = env.get_template( '%s.html' % (templatename) )
    rtext = template.render(refs=refs)
    with open(outfn, 'w') as outf:
        outf.write( rtext.encode('utf8') )
