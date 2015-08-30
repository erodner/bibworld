import argparse
import json
from bibdb import bibdb
import re

parser = argparse.ArgumentParser()

parser.add_argument('-o', '--out', help='Output file for the LaTeX commands', default="publications.tex")
parser.add_argument('-b', '--bibfile', help='Bibtex file', required=True)
parser.add_argument('-q', '--query', help='Query in JSON format', default=None)

args = parser.parse_args()

mybib = bibdb()
mybib.readFromBibTex ( args.bibfile, year_is_essential=False, use_raw_encoding=True )

if args.query is None:
    jsonquery = {}
else:
    with open(args.query,'r') as f:
        jsonquery = json.load(f)

refs = mybib.getReferences(**jsonquery)

bins = {}
bins['nonpapers'] = []
bins['papers'] = []
bins['articles'] = []
bins['books'] = []

for k in refs:
    p = refs[k]
    if p['type']=='book':
        bins['books'].append(k)
    elif p['type']=='article':
        if not 'journal' in p:
            raise Exception("{} has no journal field".format(k))
        if re.search('arxiv', p['journal'], re.IGNORECASE):
            bins['nonpapers'].append(k)
        else:
            bins['articles'].append(k)
    elif p['type']=='inproceedings':
        if not 'booktitle' in p:
            raise Exception("No booktitle field in {}".format(k))

        if re.search('OGRW', p['booktitle'], re.IGNORECASE):
            bins['nonpapers'].append(k)
        elif re.search('DGMP', p['booktitle'], re.IGNORECASE):
            bins['nonpapers'].append(k)
        else:
            bins['papers'].append(k)
    else:
        bins['nonpapers'].append(k)

print "Writing to {}".format(args.out)
with open(args.out, 'w') as f:
    for category in bins:
        f.write("\\addtocategory{{{0}}}{{{1}}}\n".format( category, ",".join(bins[category]) ))
