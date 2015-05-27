import argparse
import json
from bibdb import bibdb
import re

parser = argparse.ArgumentParser()

parser.add_argument('-b', '--bibfile', help='main bibtex file', required=True)
parser.add_argument('-f', '--factors', help='JSON file with impact factors', required=True)
parser.add_argument('-s', '--start', help='time span start', default=2000, type=int)
parser.add_argument('-e', '--end', help='time span end', default=3000, type=int)
parser.add_argument('-q', '--query', help='Query in JSON format', default=None)

args = parser.parse_args()

mybib = bibdb()
mybib.readFromBibTex ( args.bibfile )

if args.query is None:
    jsonquery = {}
else:
    with open(args.query,'r') as f:
        jsonquery = json.load(f)

with open(args.factors,'r') as f:
    factors = json.load(f)

refs = mybib.getReferences(**jsonquery)
sumfactors = 0
sumfactors_per_year = {}
for k in refs:
    bib = refs[k]
    if not 'year' in bib:
        continue
    y = int(bib['year'])
    if y>=args.start and y<=args.end:
        identifier = None
        if 'booktitle' in bib:
            identifier = bib['booktitle']
        if 'journal' in bib:
            identifier = bib['journal']

        found = False
        for f in factors:
           if not identifier is None:
                if re.search(f, identifier):
                    print k, identifier, f, factors[f]
                    found = True
                    sumfactors += factors[f]
                    if not y in sumfactors_per_year:
                        sumfactors_per_year[y] = 0.0
                    sumfactors_per_year[y] += factors[f]
                    break

        if not found:
            print "Unknown: {}".format(identifier)

print "Sum of impact factors: {}".format(sumfactors)
for y in sumfactors_per_year:
    print "Sum of impact factors (per year): {} {}".format(y, sumfactors_per_year[y])

