import osmnx as ox
import networkx as nx

# Load the saved graph
print("Loading Bengaluru road network...")
G = ox.load_graphml("bengaluru_roads.graphml")
print(f"Loaded graph with {len(G.nodes)} nodes")

def find_shortest_path(start_lat, start_lng, end_lat, end_lng):
    """
    Find shortest path between two coordinates.
    Returns list of (lat, lng) tuples and distance.
    """
    # Find nearest nodes to the clicked points
    start_node = ox.nearest_nodes(G, start_lng, start_lat)
    end_node = ox.nearest_nodes(G, end_lng, end_lat)
    
    print(f"Start node: {start_node}, End node: {end_node}")
    
    # Calculate shortest path using length as weight
    route = nx.shortest_path(
        G, 
        start_node, 
        end_node, 
        weight='length'
    )
    
    # Convert node IDs to coordinates
    route_coords = [
        (G.nodes[node]['y'], G.nodes[node]['x']) 
        for node in route
    ]
    
    # Calculate total distance by summing edge lengths
    total_distance = 0
    for i in range(len(route) - 1):
        u, v = route[i], route[i + 1]
        
        # Access edge data for MultiDiGraph
        # Format: G[u][v][key] where key is typically 0
        edge_dict = G[u][v]
        
        # Get the first (usually only) edge
        for key in edge_dict:
            edge_data = edge_dict[key]
            if 'length' in edge_data:
                total_distance += float(edge_data['length'])
            break
    
    print(f"Route found: {len(route)} nodes, {total_distance:.2f} meters")
    
    return route_coords, total_distance

# Test with two points in Bengaluru
# MG Road area
start_lat, start_lng = 12.9716, 77.5946

# Indiranagar
end_lat, end_lng = 12.9784, 77.6408

print("\nTesting route from MG Road to Indiranagar...")
path, distance = find_shortest_path(start_lat, start_lng, end_lat, end_lng)

print(f"\nPath has {len(path)} points")
print(f"Total distance: {distance:.2f} meters ({distance/1000:.2f} km)")
print(f"First 3 points: {path[:3]}")