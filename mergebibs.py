import argparse
import json
from bibdb import bibdb
import re

parser = argparse.ArgumentParser()

parser.add_argument('-o', '--out', help='Output file for the merging', default="merge.bib")
parser.add_argument('bibfiles', nargs='+', help='Bibtex files to merge (order is important)')

args = parser.parse_args()

mergebib = None
for bibfile in args.bibfiles:
    mybib = bibdb()
    mybib.readFromBibTex ( bibfile, year_is_essential=False, use_raw_encoding=True )

    if mergebib is None:
        mergebib = bibdb(mybib)
    else:
        refs = mybib.getReferences()
        mergebib.update(refs)

mergebib.write ( args.out )

