"""
build_overture_network.py
Downloads commercial-grade, verified road network for Greater Bengaluru from Overture Maps
(backed by Meta, Microsoft, Amazon, and TomTom).

Uses PyArrow S3FileSystem to directly stream from AWS S3 without Windows path errors.
Filters strictly for public drivable roads, avoiding OSM's phantom layout roads.

Saves directly to:
  Data Assets/bengaluru_roads_extended.graphml
  Data Assets/bengaluru_graph.pkl
"""

import os
import time
import math
import pickle
import shapely
import shapely.wkb
import networkx as nx
import pyarrow.fs as pafs
import pyarrow.dataset as pads
import osmnx as ox

# Greater Bengaluru Bounding Box:
# (West, South, East, North)
WEST, SOUTH, EAST, NORTH = 77.44, 12.78, 77.78, 13.22

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Data Assets"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_GRAPHML = os.path.join(OUTPUT_DIR, "bengaluru_roads_extended.graphml")
OUTPUT_PKL = os.path.join(OUTPUT_DIR, "bengaluru_graph.pkl")

def haversine_m(lat1, lng1, lat2, lng2):
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def build_graph_from_overture():
    print("=" * 65)
    print("  Overture Maps - Greater Bengaluru Road Network Extractor")
    print("  Backed by Meta, Microsoft, Amazon & TomTom")
    print("=" * 65)
    print(f"Bounding Box: West={WEST}, South={SOUTH}, East={EAST}, North={NORTH}\n")

    t0 = time.time()
    print("Connecting directly to Overture S3 public bucket (us-west-2)...")

    # Connect using anonymous S3 credentials (no AWS account needed)
    s3 = pafs.S3FileSystem(anonymous=True, region="us-west-2")
    s3_path = "overturemaps-us-west-2/release/2026-08-19.0/theme=transportation/type=segment/"

    dataset = pads.dataset(s3_path, filesystem=s3, format="parquet")

    # Valid drivable public road classes in Overture schema
    # Excludes pedestrian paths, cycle tracks, and non-drivable categories
    DRIVABLE_CLASSES = {
        'motorway', 'primary', 'secondary', 'tertiary',
        'residential', 'living_street', 'unclassified'
    }

    # Pushdown filter for bounding box and road subtype at Parquet metadata level
    filter_expr = (
        (pads.field("subtype") == "road") &
        (pads.field("bbox", "xmin") <= EAST) &
        (pads.field("bbox", "xmax") >= WEST) &
        (pads.field("bbox", "ymin") <= NORTH) &
        (pads.field("bbox", "ymax") >= SOUTH)
    )

    print("Querying and streaming Bengaluru road segments...")
    scanner = dataset.scanner(
        columns=["id", "geometry", "class", "subtype", "names"],
        filter=filter_expr
    )

    G = nx.MultiDiGraph()
    G.graph['crs'] = 'epsg:4326'

    coord_to_node = {}
    node_id_counter = 1

    def get_or_create_node(lng, lat):
        nonlocal node_id_counter
        key = (round(lng, 6), round(lat, 6))
        if key not in coord_to_node:
            nid = node_id_counter
            node_id_counter += 1
            coord_to_node[key] = nid
            G.add_node(nid, x=lng, y=lat)
            return nid
        return coord_to_node[key]

    total_segments = 0
    kept_edges = 0

    print("Building road network graph from verified segments...")
    for batch in scanner.to_batches():
        num_rows = batch.num_rows
        if num_rows == 0:
            continue

        pydict = batch.to_pydict()
        total_segments += num_rows

        subtypes = pydict.get("subtype", [])
        classes = pydict.get("class", [])
        geoms = pydict.get("geometry", [])
        names_col = pydict.get("names", [])

        for i in range(num_rows):
            st = subtypes[i] if subtypes else "road"
            if st != "road":
                continue

            road_class = classes[i] if classes else "unclassified"
            if road_class not in DRIVABLE_CLASSES:
                continue

            geom_bytes = geoms[i]
            if not geom_bytes:
                continue

            try:
                line = shapely.wkb.loads(geom_bytes)
            except Exception:
                continue

            if not isinstance(line, shapely.LineString) or len(line.coords) < 2:
                continue

            coords = list(line.coords)
            start_lng, start_lat = coords[0][0], coords[0][1]
            end_lng, end_lat = coords[-1][0], coords[-1][1]

            # Verify endpoints are within our target bounding box
            if not (WEST <= start_lng <= EAST and SOUTH <= start_lat <= NORTH):
                if not (WEST <= end_lng <= EAST and SOUTH <= end_lat <= NORTH):
                    continue

            u = get_or_create_node(start_lng, start_lat)
            v = get_or_create_node(end_lng, end_lat)

            # Compute segment length
            seg_len = 0.0
            for pt_idx in range(len(coords) - 1):
                p1, p2 = coords[pt_idx], coords[pt_idx + 1]
                seg_len += haversine_m(p1[1], p1[0], p2[1], p2[0])
            seg_len = max(1.0, round(seg_len, 2))

            # Extract road name if available
            name_val = ""
            names_obj = names_col[i] if names_col else None
            if isinstance(names_obj, dict):
                primary_name = names_obj.get("primary")
                if primary_name:
                    name_val = str(primary_name)
                elif names_obj.get("common"):
                    name_val = str(names_obj.get("common"))

            edge_attr = {
                'length': seg_len,
                'highway': road_class,
                'name': name_val,
                'geometry': line,
                'oneway': False
            }

            # Bidirectional public road connection
            G.add_edge(u, v, 0, **edge_attr)
            G.add_edge(v, u, 0, **edge_attr)
            kept_edges += 2

        print(f"  Processed {total_segments:,} segments -> {kept_edges:,} road edges built...")

    print(f"\nExtraction complete:")
    print(f"  Total raw segments inspected: {total_segments:,}")
    print(f"  Verified road edges kept:     {kept_edges:,}")
    print(f"  Total unique junctions/nodes: {len(G.nodes):,}")

    if len(G.nodes) == 0:
        print("ERROR: No road nodes were extracted.")
        return

    # Keep largest strongly connected component
    print("\nFiltering disconnected fragments...")
    largest_scc = max(nx.strongly_connected_components(G), key=len)
    G = G.subgraph(largest_scc).copy()
    print(f"Final connected network: {len(G.nodes):,} nodes, {len(G.edges):,} edges")

    # Dynamic bounds and center
    lats = [d['y'] for _, d in G.nodes(data=True)]
    lngs = [d['x'] for _, d in G.nodes(data=True)]
    bounds = {
        "min_lat": min(lats), "max_lat": max(lats),
        "min_lng": min(lngs), "max_lng": max(lngs)
    }
    center = {"lat": sum(lats) / len(lats), "lng": sum(lngs) / len(lngs)}

    # Save to GraphML
    print(f"\nSaving verified graph to {OUTPUT_GRAPHML}...")
    ox.save_graphml(G, OUTPUT_GRAPHML)
    size_mb = round(os.path.getsize(OUTPUT_GRAPHML) / (1024 * 1024), 1)
    print(f"GraphML saved: {size_mb} MB")

    # Save to PKL
    print(f"Saving binary cache to {OUTPUT_PKL}...")
    cache = {'G': G, 'G_inner': G, 'bounds': bounds, 'center': center}
    with open(OUTPUT_PKL, 'wb') as f:
        pickle.dump(cache, f)
    pkl_size_mb = round(os.path.getsize(OUTPUT_PKL) / (1024 * 1024), 1)
    print(f"Binary PKL saved: {pkl_size_mb} MB")

    elapsed = round(time.time() - t0, 1)
    print(f"\nCOMPLETED in {elapsed}s!")
    print("Your backend will now route exclusively on verified, commercial-grade roads.")

if __name__ == "__main__":
    build_graph_from_overture()
