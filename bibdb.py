# coding=utf-8
import re

class bibdb:
  
    reflist = []

    def __init__(self):
        print "Initialize bibdb"

    def getReferences (self):
        return self.reflist

    def readFromBibTex(self, bibfile):
        # The following code is a modified version of 
        # bibtex2html @ github (by Gustavo de Oliverira

        print "Reading references from: ", bibfile

        with open(bibfile, 'r') as f:
            datalist = f.readlines()
            # Discard unwanted characters and commented lines
            datalist = [s.strip(' \n\t') for s in datalist]
            datalist = [s for s in datalist if s[:2] != '%%']


            # Convert a list into a string
            data = ''
            for s in datalist: 
                if re.match('^\s*%', s): 
                    continue
                if re.match('^\s*$', s):
                    continue
                    
                s = re.sub( r'\{?\\"o\}?', 'ö', s )
                s = re.sub( r'\{?\\"u\}?', 'ü', s )
                s = re.sub( r'\{?\\"a\}?', 'ä', s )
                data += unicode(s + ' ', "utf8")


            # Split the data at the separators @ and put it in a list
            biblist = data.split('@')
            # Discard empty strings from the list
            biblist = [s for s in biblist if s != '']


            # Create a list of lists containing the strings "key = value" of each bibitem
            listlist = []
            for s in biblist:
                type, sep, s = s.partition('{')
                id, sep, s = s.partition(',')
                s = s.rpartition('}')[0]
                keylist = ['type = ' + type.lower(), 'id = ' + id]

                number = 0
                flag = 0
                i = 0
                while len(s) > 0 and i<len(s):
                    if s[i] == '{':
                        number += 1
                        flag = 1
                    elif s[i] == '}':
                        number -= 1

                    if number == 0 and flag == 1:
                        keylist.append(s[:i+1])
                        s = s[i+1:]
                        flag = 0
                        i = 0
                        continue

                    i += 1

                keylist = [t.strip(' ,\t\n') for t in keylist]
                listlist.append(keylist)

            # Create a list of dicts containing key : value of each bibitem
            self.reflist = {}
            for l in listlist:
                keydict = {}
                for s in l:
                    key, sep, value = s.partition('=')
                    key = key.strip(' ,\n\t{}')
                    key = key.lower()
                    value = value.strip(' ,\n\t{}')
                    keydict[key] = value
                
                if 'id' in keydict:
                    bibid = keydict['id']
                else:
                    print "No BibTex ID given or error during parsing"


                self.reflist[bibid] = keydict


                 
