# Visualizes XML neurons as given by
# http://morphml.org/
import networkx as nx
import xml.parsers.expat
from optparse import OptionParser
from numpy import *

parser = OptionParser()
parser.add_option("-i", "--input", dest="in_filename", help="Neuroml file", default=None)
parser.add_option("-o", "--output", dest="out_filename", help=".ply file", default=None)

(options, args) = parser.parse_args()

if options.in_filename == None or options.out_filename == None:
    parser.print_help()
    sys.exit(0)



current_cell_graph = nx.DiGraph()
current_cell_name  = None
current_segment    = None

edge_data = {}

# handler functions
def start_element(name, attrs):
    global current_cell_graph, current_segment
    # print name
    if name=="cell":
        #print "current_cell_graph set"
        current_segment = None
    if name=="segment":
        # Note the current segment
        id_number = int(attrs["id"])
        current_segment = id_number

        # Add the segment as a node
        current_cell_graph.add_node(id_number, attr_dict = attrs)

        # Connect it to its parent if it has one
        if "parent" in attrs:
            current_cell_graph.add_edge(id_number, int(attrs["parent"]))

    # if current_segment == None:
    #     return

    if name in ["distal", "proximal"]:
        node_data = current_cell_graph.node[current_segment]        
        pre_letter = name[0]
        
        for key, value in attrs.items():
            node_data[pre_letter + key] = float(value)

def end_element(name):
    pass
    #print 'End element:', name
def char_data(data):
    pass
    #print 'Character data:', repr(data)

p = xml.parsers.expat.ParserCreate()

p.StartElementHandler = start_element
# p.EndElementHandler = end_element
# p.CharacterDataHandler = char_data

parsed = p.Parse(open(options.in_filename).read())


from mayavi import mlab

unique_cables = set()
cables = []
xyzds  = []
ids    = []

points = []

for n1, data in current_cell_graph.nodes_iter(data=True): 
    # print n1, data["cable"]
    cables.append(int(data["cable"]))
    # print data
    xyz_t = zeros(4)
    n_points = 0
    if "px" in data:
        xyz_t += [float(data[s]) for s in ["px", "py", "pz", "pdiameter"]]
        n_points += 1
        
    if "dx" in data:
        xyz_t += [float(data[s]) for s in ["dx", "dy", "dz", "ddiameter"]]
        n_points += 1

    xyz_t /= n_points

    ids.append(int(data["id"]))
    xyzds.append(xyz_t)


cables = array(cables)
xyzds  = array(xyzds)
ids    = array(ids)
inds   = arange(ids.size, dtype=uint32)

id_to_index = dict(zip(ids, inds))

unique_cables = set(cables)

connections = [(id_to_index[n1], id_to_index[n2]) for n1, n2 in current_cell_graph.edges()]

x, y, z, s = xyzds.T
    
pts = mlab.pipeline.scalar_scatter(x, y, z, s)
pts.mlab_source.dataset.lines = array(connections)
tube = mlab.pipeline.tube(mlab.pipeline.stripper(pts))

tube.filter.radius_factor = 100.
tube.filter.vary_radius = 'vary_radius_by_scalar'
surface = mlab.pipeline.surface(tube)

ply_data = tube.outputs[0]

poly_data = mlab.pipeline.triangle_filter(ply_data).outputs[0]

# print poly_data.points, poly_data.points.to_array()
# print poly_data.polys,  poly_data.polys.to_array()

points = poly_data.points.to_array()
polys  = poly_data.polys .to_array().reshape((-1,4))

text_header = '''ply
format ascii 1.0
comment Auto-Encoded By Matts dumper from %s
element vertex %i
property float32 x
property float32 y
property float32 z
element face %i
property list uint8 int32 vertex_indices
end_header
'''


f = open(options.out_filename, "w")
points_polys_count = (options.out_filename, points.shape[0], polys.shape[0])
print "Writing %s \n\t- %i points \n\t- %i polys. . ." % points_polys_count
f.write(text_header % points_polys_count)
savetxt(f, points, fmt="%f")
savetxt(f, polys,  fmt="%i")


#mlab.pipeline.volume(mlab.pipeline.gaussian_splatter(pts))
