from pyparsing import *
import networkx as nx
from optparse import OptionParser
import sys, os

graph = nx.DiGraph()

parser = OptionParser()
parser.add_option("-i", "--input", dest="in_directory", help="File to analyze", default=None)
(options, args) = parser.parse_args()

if options.in_directory == None:
    parser.print_help()
    sys.exit(0)

in_dir = options.in_directory

endings = [".cpp", ".cxx", ".c", ".h", ".hpp"]

paths = [os.path.join(in_dir, f)  for f in os.listdir(in_dir)]

screened = []

for path in paths:
    ext = os.path.splitext(path)[-1]
    print ext
    if ext not in endings:
        continue
    screened.append(path)

include = (Literal("#include").suppress() + 
           (Literal('"') | Literal("<")).suppress() + Word(alphas+nums+r"./\\") + (Literal('"') | Literal('"')).suppress())

for p in screened: 
    self_filename = os.path.split(p)[-1]
    raw_data = open(p).read()
    print "*****", p, "*****"
    includes = include.searchString(raw_data)

    for i in includes:
        graph.add_edge(self_filename, i[0])

        
