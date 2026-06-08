from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import osmnx as ox
import networkx as nx
import math

app = Flask(__name__)
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

print("Loading Bengaluru road graph...")
G = ox.load_graphml("bengaluru_graph.graphml")
print("Graph loaded.")

def get_edge_weight(u, v, data, congestion=False):
    length = data.get("length", 1)
    road_type = data.get("highway", "residential")
    if isinstance(road_type, list):
        road_type = road_type[0]

    # Realistic Bengaluru speeds
    speed_map = {
        "motorway": 60, "trunk": 45, "primary": 35,
        "secondary": 25, "tertiary": 20,
        "residential": 12, "service": 8, "unclassified": 15
    }
    speed = speed_map.get(road_type, 12)

    if congestion:
        congestion_map = {
            "motorway": 2.5, "trunk": 2.2, "primary": 2.0,
            "secondary": 1.6, "tertiary": 1.3,
            "residential": 1.0, "service": 1.0, "unclassified": 1.1
        }
    else:
        congestion_map = {k: 1.0 for k in ["motorway","trunk","primary",
    "secondary","tertiary","residential","service","unclassified"]}

    factor = congestion_map.get(road_type, 1.0)
    travel_time = (length / 1000) / speed * 60
    return travel_time * factor

@app.route("/")
def home():
    if not API_KEY:
        return "Error: GOOGLE_MAPS_API_KEY is missing from the .env file.", 500
    return render_template("index.html", api_key=API_KEY)

@app.route("/route")
def get_route():
    try:
        olat = float(request.args.get("olat"))
        olng = float(request.args.get("olng"))
        dlat = float(request.args.get("dlat"))
        dlng = float(request.args.get("dlng"))
        congestion = request.args.get("congestion", "false") == "true"

        orig_node = ox.nearest_nodes(G, olng, olat)
        dest_node = ox.nearest_nodes(G, dlng, dlat)

        def heuristic(u, v):
            u_lat = G.nodes[u]["y"]
            u_lng = G.nodes[u]["x"]
            v_lat = G.nodes[v]["y"]
            v_lng = G.nodes[v]["x"]
            return math.sqrt((u_lat - v_lat)**2 + (u_lng - v_lng)**2) * 111000

        path = nx.astar_path(
            G, orig_node, dest_node,
            heuristic=heuristic,
            weight=lambda u, v, data: get_edge_weight(u, v, data, congestion)
        )

        coords = [{"lat": G.nodes[n]["y"], "lng": G.nodes[n]["x"]} for n in path]

        total_distance = 0
        total_time = 0
        for i in range(len(path) - 1):
            edge_data = G.get_edge_data(path[i], path[i+1])
            edge = edge_data[0] if edge_data else {}
            total_distance += edge.get("length", 0)
            total_time += get_edge_weight(path[i], path[i+1], edge, congestion)

        return jsonify({
            "status": "OK",
            "path": coords,
            "distance_km": round(total_distance / 1000, 2),
            "time_mins": round(total_time, 1)
        })

    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route("/congestion_overlay")
def congestion_overlay():
    try:
        north = float(request.args.get("north"))
        south = float(request.args.get("south"))
        east = float(request.args.get("east"))
        west = float(request.args.get("west"))

        segments = []
        for u, v, data in G.edges(data=True):
            u_lat = G.nodes[u]["y"]
            u_lng = G.nodes[u]["x"]
            v_lat = G.nodes[v]["y"]
            v_lng = G.nodes[v]["x"]

            if not (south <= u_lat <= north and west <= u_lng <= east):
                continue

            road_type = data.get("highway", "unclassified")
            if isinstance(road_type, list):
                road_type = road_type[0]

            congestion_map = {
                "motorway": "red", "trunk": "red",
                "primary": "orange", "secondary": "orange",
                "tertiary": "yellow",
                "residential": "green", "service": "green",
                "unclassified": "green"
            }
            color = congestion_map.get(road_type, "green")

            segments.append({
                "start": {"lat": u_lat, "lng": u_lng},
                "end": {"lat": v_lat, "lng": v_lng},
                "color": color
            })

        return jsonify({"status": "OK", "segments": segments})

    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)