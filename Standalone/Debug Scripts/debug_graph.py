import osmnx as ox

G = ox.load_graphml("bengaluru_roads.graphml")

# Get a sample edge and print its attributes
sample_edge = list(G.edges(data=True))[0]
print("Sample edge:", sample_edge)

# Check if 'length' key exists in edges
edge_u, edge_v, edge_data = sample_edge
print(f"\nEdge attributes: {edge_data.keys()}")