#!/usr/bin/env python -c
'''This is a program to scrape a tex/latex document for bibitems, and search and assemble the proper cross ref from inspires.
To use it, specify two command line arguments: 
   The input file  (-i)
   The output file (-o)

Example:
  ./tex-to-bib.py -i somefile.tex -o someotherfile.bib
'''
import urllib, time, sys
from urllib import urlopen, urlencode
from optparse import OptionParser

try:
    from pyparsing import *
except ImportError:
    print "pyparsing is a required module for this programs operation!"
    print "Please: $sudo apt-get install python-pyparsing"

parser = OptionParser()
parser.add_option("-i", "--input", dest="in_filename", help="File to analyze", default=None)
parser.add_option("-o", "--output", dest="out_filename", help="File to save to", default=None)
parser.add_option("-f", "--full", action="store_true", dest="full", default=False, help="Require full bib-time match")
parser.epilog = __doc__

(options, args) = parser.parse_args()


if options.in_filename == None or options.out_filename == None:
    parser.print_help()
    sys.exit(0)

# Definition of the bibitem stuff
label = Word(nums + alphas + ":.")

# This is the parser for a basic /bibitem 
bib_item_header = Literal(r"\bibitem{").suppress() + label + Literal("}").suppress()
bib_item_header.setName("Header")

# The rest is the "full" match process (which is mostly a useless quantity
title = Literal("``").suppress() + SkipTo(",''", include=False) + Literal(",''").suppress()

full_title = (Literal("{").suppress() + title + Literal("}").suppress()) ^ title
full_title.setName("Title of Paper")

author = Word(alphas + nums + ".~")
author.setName("Author")

author_seperator = Literal(",") ^ Literal("and")
author_seperator.setName("Author Sep")

journal_title = OneOrMore(Word(alphas + nums + r"\."))
journal_title.setName("Journal Title")

number_one = Literal(r"{\bf").suppress() + Word(nums + alphas)+ Literal("}").suppress()

number_two = Word(nums) ^ Combine(Word(nums) + Literal("-") + Word(nums))

year = Literal("(").suppress() + Word(nums, exact=4) + Literal(")").suppress()
year.setName("Year")

link = Combine(Literal(r"\href{") + Word(alphas + nums + r":/-.") + Literal("}{") + Word(alphas + nums + r".:/-") + Literal("}"))
link.setName("Url")

peri_or_semi = (Literal(".") ^ Literal(";")).suppress()

# Full scale-no bulshitting bibliography extraction
bib_entry = (bib_item_header + Group(OneOrMore(author + author_seperator.suppress())) + 
             full_title + 
             Optional(journal_title + number_one + Optional(Literal(",").suppress() + number_two) + year) + 
             Optional(Optional(Literal(",").suppress()) + link) + peri_or_semi)



# Parse searcher for the bibtex link
record_address = Combine(Literal(r'http://inspirehep.net/record/') + Word(nums) + Literal('/export/hx'))

# Parse based searcher for the bibtex block!
bibtex_block = Combine(Literal(r"<pre>").suppress() + SkipTo(Literal("</pre>")))


# Decide how to Analyze the input file:
if options.full:
    screening_parse = bib_entry
else:
    screening_parse = bib_item_header

# Analyze the input file:
raw_data = open(options.in_filename).read()
res = screening_parse.searchString(raw_data)

# Pull the results out of the parse result containers
list_of_id_strings = [r[0] for r in res]

# Url to scrape inspires
search_string = r"http://inspirehep.net/search?"

# Open the output file
output_file = open(options.out_filename, "w")

# Fof each of the idnetification bibtex headers
for string in list_of_id_strings:
    # Encode the string into a string for query (: -> %whatever)
    addy = urllib.urlencode({"p":string, "ln":"en"})

    # Perform the inspires search for the given keyword
    search_results = urlopen( search_string + addy ).read()
    
    # Grab the first result, and get its bibtex link
    bibtex_url = record_address.searchString(search_results)[0][0]

    # Open that link
    bibtex_web_fetch = urlopen(bibtex_url).read()
    
    # Scrape out the bibtex!
    bibtex = bibtex_block.searchString(bibtex_web_fetch)[0][0]
    
    # Print it an emit it to a file
    print bibtex
    output_file.write(bibtex.strip() + "\n")
    
