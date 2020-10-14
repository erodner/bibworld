import sys
import os
import argparse
from bibdb import bibdb
from pprint import pprint
import tengjabref
import tengjinja2
import re
import json

# Get the BibTeX and template file names
parser = argparse.ArgumentParser()
parser.add_argument("-b", help="Source Bibtex file", required=True)
parser.add_argument("-t", help="Template file", required=True)
parser.add_argument("-o", help="Output", default="out.html")
parser.add_argument("-p", help="PDF and teaser directory", default=".")
parser.add_argument("-r", help="Root URL", default="")
parser.add_argument("--engine", help="Template engine being used", default="jinja")
parser.add_argument("--query", help="Query in JSON format", default=None)
parser.add_argument(
    "--staticroot",
    help="Directory for static files that will be specified in the output",
    default="",
)
args = parser.parse_args()

bibfile = args.b
templatefile = args.t
outfn = args.o

# derive template directory from templatefile
templatedir = os.path.dirname(templatefile)
templatename = os.path.basename(templatefile)

mybib = bibdb()
mybib.readFromBibTex(bibfile)

pdfdir = args.p
mybib.addAuxFiles(os.path.join(pdfdir, "%s.pdf"), "pdf")
# compatibility for the old format
mybib.addAuxFiles(os.path.join(pdfdir, "%s.pdf.teaser.png"), "teaser")
mybib.addAuxFiles(
    os.path.join(pdfdir, "%s.teaser.png"), "teaser", removeIfUnavailable=False
)
mybib.addAuxFiles(os.path.join(pdfdir, "%s.presentation.pdf"), "presentation")
mybib.addAuxFiles(os.path.join(pdfdir, "%s.supplementary.pdf"), "supplementary")


if args.query is None:
    jsonquery = {}
else:
    with open(args.query, "r") as f:
        jsonquery = json.load(f)

refs = mybib.getReferences(**jsonquery)
print("Number of publications: {}".format(len(refs)))

print("Writing output to {}".format(outfn))
if args.engine == "jabref":
    tengjabref.bib2html(refs, outfn, templatedir, templatename)
else:
    tengjinja2.bib2html(
        refs,
        outfn,
        templatedir,
        templatename,
        staticroot=args.staticroot,
        rooturl=args.r,
    )
