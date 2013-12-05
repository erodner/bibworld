# coding=utf-8
import os
import re
import sys
from pprint import pprint

def printfile ( outf, fn ):
    with open(fn, 'r') as f:
        for line in f:
            outf.write(line.encode('utf8')) 

def printtemplate ( outf, p, fn ):
    with open(fn, 'r') as f:
        for line in f:
            for k in p.keys():
                line = re.sub( r'\\%s' % (k), p[k], line )
            outf.write(line.encode('utf8')) 


def bib2html(refs, outfn, templatedir, templatename):
    print "Template dir: ", templatedir 
    print "Template name: ", templatename

    # open header
    with open(outfn, 'w') as outf:
        printfile ( outf, '%s/%s.begin.layout' %  (templatedir, templatename) )
        for bibkey in refs.keys():
            p = refs[bibkey]
            p['bibtexkey'] = bibkey
            typeofp = p['type']

            # skip bibtex comments mostly from jabref
            if typeofp=='comment':
                continue

            layoutfile = '%s/%s.%s.layout' % (templatedir, templatename, typeofp) 
            if not os.path.isfile(layoutfile):
                layoutfile = '%s/%s.layout' % (templatedir, templatename) 
                
            printtemplate ( outf, p, layoutfile )

        printfile ( outf, '%s/%s.end.layout' %  (templatedir, templatename) )
