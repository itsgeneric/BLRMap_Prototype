import osmnx as ox
from routing.graph_manager import graph_manager
from routing.algorithms import two_wheeler_astar, build_two_wheeler_penalties, calc_route_distance

def test_offline_route(from_lat, from_lng, to_lat, to_lng):
    print("Initializing Graph Manager...")
    graph_manager.load_graph()
    
    start_node = ox.nearest_nodes(graph_manager.G, from_lng, from_lat)
    end_node = ox.nearest_nodes(graph_manager.G, to_lng, to_lat)
    
    penalties = build_two_wheeler_penalties(main_road_penalty=1.5, inner_road_multiplier=0.9)
    route = two_wheeler_astar(graph_manager.G, start_node, end_node, graph_manager, penalties=penalties)
    
    dist_km = calc_route_distance(graph_manager.G, route) / 1000.0
    print(f"Route calculated successfully!")
    print(f"Nodes in path: {len(route)}")
    print(f"Total distance: {dist_km:.2f} km")

if __name__ == "__main__":
    # Test coordinates: BNMIT -> MG Road
    test_offline_route(12.9237, 77.5714, 12.9756, 77.6066)