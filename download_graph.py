import osmnx as ox

print("Downloading Bengaluru road graph... this will take a minute")
G = ox.graph_from_place("Bangalore, India", network_type="drive")
ox.save_graphml(G, "bengaluru_graph.graphml")
print("Done! bengaluru_graph.graphml saved.")