import sys
import os
import argparse
from bibdb import bibdb
from pprint import pprint
import tengjabref
import tengjinja2
import re

# add a git extension to fapuli


# Get the BibTeX and template file names
parser = argparse.ArgumentParser()
parser.add_argument('-b', help='Source Bibtex file', required=True)
parser.add_argument('-t', help='HTML template file', required=True)
parser.add_argument('-o', help='HTML output', default='out.html')
parser.add_argument('--engine', help='Template engine being used', default='jabref')
args = parser.parse_args()

bibfile = args.b
templatefile = args.t
outfn = args.o

# derive template directory from templatefile
templatedir = os.path.dirname ( templatefile )
templatename = os.path.basename ( templatefile )
m = re.search( '^(\w+)\.', templatename )
templatename = m.group(1)

mybib = bibdb()
mybib.readFromBibTex ( bibfile )

refs = mybib.getReferences()
print "Number of publications: ", len(refs)
#pprint(refs)

print "Writing HTML output to", outfn
if args.engine=='jabref':
    tengjabref.bib2html( refs, outfn, templatedir, templatename )
else:
    tengjinja2.bib2html( refs, outfn, templatedir, templatename )
