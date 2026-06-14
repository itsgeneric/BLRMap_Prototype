


## Setup Instructions

### 1. Install dependencies
pip install flask python-dotenv
pip install shapely pyproj rtree
pip install pandas geopandas
pip install osmnx networkx


### 2. Download Bengaluru road graph (one time only)
python download_graph.py

### 3. Run the app
python app.py

Open http://127.0.0.1:5000

## What's Built 


### Custom Routing Algorithm
- OSMnx road graph of Bengaluru (129MB, OpenStreetMap data)
- A* pathfinding with geographic heuristic
- Dynamic edge weight formula:
  weight = (distance / speed) × congestion_factor
- Road type speed mapping (motorway 80kmph → residential 25kmph)
- Congestion penalties applied to main roads during peak hours


## Key Observation
For short distances in Bengaluru, our algorithm consistently finds routes 
through residential roads that are similar in distance but faster during 
congestion — validating the hypothesis that less-used roads are underutilized 
during peak hours.