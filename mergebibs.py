import argparse
import json
from bibdb import bibdb
import re

parser = argparse.ArgumentParser()

parser.add_argument('-o', '--out', help='Output file for the merging', default="merge.bib")
parser.add_argument('bibfiles', nargs='+', help='Bibtex files to merge (order is important)')
parser.add_argument('-q', '--query', help='Query in JSON format for the first bib file', default=None)
parser.add_argument('-r', '--removefields', help='Remove fields from the first bib file', default="")

args = parser.parse_args()

if args.query is None:
    jsonquery = {}
else:
    with open(args.query,'r') as f:
        jsonquery = json.load(f)

rfields = args.removefields.split(' ')

mergebib = bibdb()
for index, bibfile in enumerate(args.bibfiles):
    mybib = bibdb()

    mybib.readFromBibTex ( bibfile, year_is_essential=False, use_raw_encoding=True )

    if index == 0:
        refs = mybib.getReferences(**jsonquery)
        for k in refs:
            for f in rfields:
                if f in refs[k]:
                    del refs[k][f]
    else:
        refs = mybib.getReferences()
    mergebib.update(refs, join_fields = set(['note']))

mergebib.write ( args.out )

