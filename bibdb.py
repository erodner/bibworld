# coding=utf-8
import re
import os
import json

class bibdb:
  
    reflist = []

    def __init__(self):
        pass

    """ try to match entries by searching terms in specific fields """
    def matchEntry ( self, sdicts, p ):
        if not 'year' in p:
            return True

        for key in sdicts: 
            if not key in p:
                return False
            value = p[key]
            pattern = sdicts[key]
            if not re.search(pattern, value):
                return False
        return True
	
    """ try to match entries by searching in all fields """
    def matchEntryAllKeys ( self, pattern, p ):
        if not 'year' in p:
            return True

        for key in p: 
            value = p[key]
            if re.search(pattern, value):
                return True
        return False

    """ get single reference """
    def getReference (self, k):
        return self.reflist[k]

           

    """ get references (possibly filtered) """
    def getReferences (self, **kwargs):
        # now filter references according to 
        # the keyword arguments
        refs = {}
        for k in self.reflist.keys():
            p = self.reflist[k]
            if self.matchEntry( kwargs, p ): 
                # add the entry to the filter result list
                refs[k] = p

        return refs

    """ get references filtered by searching for a term in all fields """
    def searchReferences (self, term):
        refs = {}
        for k in self.reflist.keys():
            p = self.reflist[k]
            if self.matchEntryAllKeys( term, p ): 
                # add the entry to the filter result list
                refs[k] = p

        return refs

    """ check available auxiliary files like pdfs or teaser images """
    def addAuxFiles (self, formattemplate, tag, verbose=True, removeIfUnavailable=True):
        for k in self.reflist.keys():
            fname = formattemplate % ( k )
            if os.path.isfile( fname ):
                if verbose:
                    print "Adding %s document: %s" % ( tag, fname )
                self.reflist[k][tag] = fname
            elif removeIfUnavailable:
                # rather remove the tag when available
                if tag in self.reflist[k]:
                    del self.reflist[k][tag]

    """ get a single BibTex entry and restrict the export fields """
    def getBibtexEntry ( self, key, exported_keys=None, newlinestr="\n" ):
        if not key in self.reflist:
            return ""
        else:
            entry = ""
            p = self.reflist[key]
            entry = entry + "@%s{%s,%s" % ( p['type'], p['id'], newlinestr )
            for k in p.keys():
                if exported_keys and not k in exported_keys:
                    continue
                else:
                    entry = entry + "  %s = {%s},%s" % ( k, p[k], newlinestr )
            entry = entry +  "}%s" % (newlinestr)
            return entry

    """ read bibtex entries from a file """
    def readFromBibTex(self, bibfile, verbose=True):
        # The following code is a modified version of 
        # bibtex2html @ github (by Gustavo de Oliverira)

        metabibkeys = {'jabref-meta'}

        if verbose:
            print "Reading references from: ", bibfile

        with open(bibfile, 'r') as f:
            datalist = f.readlines()
            # Discard unwanted characters and commented lines
            datalist = [s.strip(' \n\t') for s in datalist]
            datalist = [s for s in datalist if s[:2] != '%%']


            # Convert a list into a string
            data = u''
            for s in datalist: 
                if re.match('^\s*%', s): 
                    continue
                if re.match('^\s*$', s):
                    continue
 
                try:
                  s = unicode(s + ' ', errors='ignore')
                except UnicodeDecodeError, e:
                  print s

                s = re.sub( r'\{?\\"o\}?', u'ö', s )
                s = re.sub( r'\{?\\"u\}?', u'ü', s )
                s = re.sub( r'\{?\\"a\}?', u'ä', s )
                s = re.sub( r'\{?\\ss\}?', u'ß', s )
                
                data += s + u' '


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
                    if verbose:
                        print "No BibTex ID given or error during parsing"

                #print "Adding %s" % (bibid)
                rejected = False

                if not rejected:
                   if not 'year' in keydict and keydict['type'] != 'bibworldnode':
                      if verbose:
                          print "BibTex entry %s has no year specified and will therefore be ignored!" % (bibid)
                      rejected = True

                if not rejected:
                    for mbib in metabibkeys:
                        if re.search( mbib, bibid ):
                            rejected = True
                            break

                if not rejected:
                    self.reflist[bibid] = keydict


