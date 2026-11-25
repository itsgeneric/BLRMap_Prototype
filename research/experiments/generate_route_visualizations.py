"""
Phase 11: Route Visualization Generator
Generates:
1. High-resolution publication-quality PNG maps (Matplotlib)
2. Interactive Leaflet.js HTML maps (OpenStreetMap basemap)

For 5 representative Bengaluru case studies:
- OD_01 (BNMIT to MG Road): Radial corridor - Successful multi-corridor discovery vs Yen plateau
- OD_04 (Whitefield to Marathahalli): Tech hub pinch point - Railway & lake barrier bottleneck
- OD_06 (Jayanagar to Malleshwaram): Long trans-city journey - Arterial vs collector trade-offs
- OD_12 (Frazer Town to Shivajinagar): Dense historic grid - High parallel connectivity
- OD_15 (Yelahanka to Hebbal): Highway expressway corridor (NH44) - Strict corridor adherence

Outputs:
- research/literature_survey/11_route_quality_evaluation/visualizations/map_OD_01_bnmit_to_mg_road.png
- research/literature_survey/11_route_quality_evaluation/visualizations/map_OD_01_bnmit_to_mg_road.html
- ... (repeated for OD_04, OD_06, OD_12, OD_15)
- research/literature_survey/11_route_quality_evaluation/visualizations/all_case_studies_multi_panel.png
"""

import sys
import os
import json
import copy
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from routing.graph_manager import graph_manager

IN_JSON = os.path.join(
    PROJECT_ROOT,
    "research", "literature_survey", "11_route_quality_evaluation",
    "route_quality_evaluation.json"
)
OUT_DIR = os.path.join(
    PROJECT_ROOT,
    "research", "literature_survey", "11_route_quality_evaluation",
    "visualizations"
)
os.makedirs(OUT_DIR, exist_ok=True)

CASE_STUDY_METADATA = {
    "OD_01": {
        "title": "Case Study 1: OD_01 (BNMIT to MG Road, 10.07 km)",
        "subtitle": "Successful Multi-Corridor Offset Discovery vs. Yen's KSP Micro-Detour Plateau",
        "slug": "OD_01_bnmit_to_mg_road",
    },
    "OD_04": {
        "title": "Case Study 2: OD_04 (Whitefield to Marathahalli, 8.81 km)",
        "subtitle": "Severe Physical Bottleneck (Railway & Lake Barrier) — Zero Offset Alts Survive Detour Cap",
        "slug": "OD_04_whitefield_to_marathahalli",
    },
    "OD_06": {
        "title": "Case Study 3: OD_06 (Jayanagar to Malleshwaram, 12.45 km)",
        "subtitle": "Major Trans-City Cross-Corridor — Collector Road Diversions vs Arterial Spine",
        "slug": "OD_06_jayanagar_to_malleshwaram",
    },
    "OD_12": {
        "title": "Case Study 4: OD_12 (Frazer Town to Shivajinagar, 2.73 km)",
        "subtitle": "Dense Historic Grid — High Parallel Connectivity Permits Surviving Yen & Offset Alts",
        "slug": "OD_12_frazer_town_to_shivajinagar",
    },
    "OD_15": {
        "title": "Case Study 5: OD_15 (Yelahanka to Hebbal, 8.67 km)",
        "subtitle": "Expressway Arterial Spine (NH44 Bellary Road) — Lateral Offsets Violate Detour Tolerance",
        "slug": "OD_15_yelahanka_to_hebbal",
    },
}


def render_matplotlib_map(corridor, meta, out_png):
    """Render a standalone high-resolution Matplotlib map for a corridor."""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)

    prim = corridor["primary_route"]
    prim_coords = prim["coordinates"]
    if not prim_coords:
        plt.close(fig)
        return

    # Extract coordinates [lat, lng] -> y, x
    prim_lats = [c[0] for c in prim_coords]
    prim_lngs = [c[1] for c in prim_coords]

    legend_elements = []

    # 1. Plot Yen KSP alternatives (Dashed, crimson/magenta)
    yen_colors = ["#d62728", "#e377c2", "#8c564b"]
    for idx, yen in enumerate(corridor.get("yen_ksp_alternatives", [])):
        y_coords = yen["coordinates"]
        if not y_coords:
            continue
        y_lats = [c[0] for c in y_coords]
        y_lngs = [c[1] for c in y_coords]
        col = yen_colors[idx % len(yen_colors)]
        label = (
            f"Yen Alt {idx+1} ({yen['distance_km']}km, overlap: {yen['overlap_ratio_pct']}%, "
            f"survives: {'Yes' if yen['survives_70pct_filter'] else 'No'})"
        )
        ax.plot(y_lngs, y_lats, color=col, linestyle="--", linewidth=1.8, alpha=0.85, zorder=3)
        legend_elements.append(
            mlines.Line2D([], [], color=col, linestyle="--", linewidth=1.8, label=label)
        )

    # 2. Plot Perpendicular-Offset alternatives (Solid, vibrant green/orange/purple)
    offset_colors = ["#2ca02c", "#ff7f0e", "#9467bd"]
    for idx, alt in enumerate(corridor.get("perpendicular_offset_alternatives", [])):
        a_coords = alt["coordinates"]
        if not a_coords:
            continue
        a_lats = [c[0] for c in a_coords]
        a_lngs = [c[1] for c in a_coords]
        col = offset_colors[idx % len(offset_colors)]
        label = (
            f"Offset Alt {idx+1} ({alt['distance_km']}km, overlap: {alt['overlap_ratio_pct']}%, "
            f"detour: {alt['detour_ratio_dist']}x)"
        )
        ax.plot(a_lngs, a_lats, color=col, linestyle="-", linewidth=2.4, alpha=0.9, zorder=4)
        legend_elements.append(
            mlines.Line2D([], [], color=col, linestyle="-", linewidth=2.4, label=label)
        )

    # 3. Plot Primary Route (Deep Blue, bold solid line)
    prim_label = f"Primary Route ({prim['distance_km']}km, cost: {prim['impedance_cost']:.1f}, turns: {prim['turns']['total_turns']})"
    ax.plot(prim_lngs, prim_lats, color="#1f77b4", linestyle="-", linewidth=3.2, zorder=5)
    legend_elements.insert(
        0, mlines.Line2D([], [], color="#1f77b4", linestyle="-", linewidth=3.2, label=prim_label)
    )

    # 4. Origin and Destination Markers
    start_lat, start_lng = corridor["from_coords"]
    end_lat, end_lng = corridor["to_coords"]

    ax.scatter(
        [start_lng], [start_lat],
        color="#00aa00", s=140, marker="o", edgecolors="black", linewidths=1.5,
        zorder=6, label=f"Origin: {corridor['name'].split(' to ')[0]}"
    )
    ax.scatter(
        [end_lng], [end_lat],
        color="#cc0000", s=160, marker="s", edgecolors="black", linewidths=1.5,
        zorder=6, label=f"Destination: {corridor['name'].split(' to ')[1]}"
    )

    # Annotate Origin & Destination
    ax.annotate(
        " ORIGIN", (start_lng, start_lat),
        fontsize=9, fontweight="bold", color="#006600",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#eeffee", edgecolor="#00aa00", alpha=0.9)
    )
    ax.annotate(
        " DESTINATION", (end_lng, end_lat),
        fontsize=9, fontweight="bold", color="#990000",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffeeee", edgecolor="#cc0000", alpha=0.9)
    )

    # Title & styling
    ax.set_title(f"{meta['title']}\n{meta['subtitle']}", fontsize=11, fontweight="bold", pad=12)
    ax.set_xlabel("Longitude (°E)", fontsize=10, fontweight="semibold")
    ax.set_ylabel("Latitude (°N)", fontsize=10, fontweight="semibold")
    ax.grid(True, linestyle=":", alpha=0.6, color="#888888")

    # Add descriptive statistics box
    p_road = prim["road_classes"]["macro_pct"]
    stats_text = (
        f"Primary Composition:\n"
        f" • Arterial: {p_road['arterial_pct']}%\n"
        f" • Collector: {p_road['collector_pct']}%\n"
        f" • Residential: {p_road['residential_pct']}%\n"
        f" • Maneuvers: {prim['turns']['total_turns']} (Sharp: {prim['turns']['sharp_turns']})\n"
        f" • Turn Penalty: {prim['turns']['turn_penalty_cost']}"
    )
    ax.text(
        0.02, 0.03, stats_text, transform=ax.transAxes,
        fontsize=8.5, verticalalignment="bottom",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc", alpha=0.95)
    )

    ax.legend(handles=legend_elements, loc="upper right", fontsize=8, framealpha=0.92)
    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.close(fig)
    print(f"Saved publication map PNG: {out_png}")


def render_leaflet_html_map(corridor, meta, out_html):
    """Render an interactive standalone Leaflet.js HTML map for a corridor."""
    prim = corridor["primary_route"]
    prim_coords = prim["coordinates"]
    if not prim_coords:
        return

    start_lat, start_lng = corridor["from_coords"]
    end_lat, end_lng = corridor["to_coords"]
    center_lat = (start_lat + end_lat) / 2.0
    center_lng = (start_lng + end_lng) / 2.0

    offset_alts = corridor.get("perpendicular_offset_alternatives", [])
    yen_alts = corridor.get("yen_ksp_alternatives", [])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta['title']}</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        #header {{ background: #1a2530; color: white; padding: 12px 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }}
        #header h1 {{ margin: 0; font-size: 18px; font-weight: 600; }}
        #header p {{ margin: 4px 0 0 0; font-size: 13px; color: #b0c4de; }}
        #map {{ width: 100vw; height: calc(100vh - 70px); }}
        .info-card {{
            background: white; padding: 12px 16px; border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.15); max-width: 320px; font-size: 12px; line-height: 1.5;
        }}
        .legend-badge {{ display: inline-block; width: 12px; height: 12px; margin-right: 6px; border-radius: 2px; vertical-align: middle; }}
    </style>
</head>
<body>
    <div id="header">
        <h1>{meta['title']}</h1>
        <p>{meta['subtitle']}</p>
    </div>
    <div id="map"></div>

    <script>
        var map = L.map('map').setView([{center_lat}, {center_lng}], 13);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors | BLRMap_Prototype Phase 11'
        }}).addTo(map);

        var primaryCoords = {json.dumps(prim_coords)};
        var primaryLine = L.polyline(primaryCoords, {{
            color: '#1f77b4', weight: 5, opacity: 0.9
        }}).addTo(map);
        primaryLine.bindPopup("<b>Primary Route</b><br>Distance: {prim['distance_km']} km<br>Impedance Cost: {prim['impedance_cost']}<br>Turns: {prim['turns']['total_turns']} (Sharp: {prim['turns']['sharp_turns']})<br>Arterial: {prim['road_classes']['macro_pct']['arterial_pct']}%<br>Residential: {prim['road_classes']['macro_pct']['residential_pct']}%");

        var overlayMaps = {{ "Primary Route": primaryLine }};

        // Offset alternatives
        var offsetColors = ['#2ca02c', '#ff7f0e', '#9467bd'];
        var offsetAlts = {json.dumps(offset_alts)};
        offsetAlts.forEach(function(alt, i) {{
            var col = offsetColors[i % offsetColors.length];
            var line = L.polyline(alt.coordinates, {{
                color: col, weight: 4, opacity: 0.85
            }}).addTo(map);
            line.bindPopup("<b>Perpendicular Offset Alt " + (i+1) + "</b><br>Strategy: " + alt.strategy + "<br>Distance: " + alt.distance_km + " km<br>Cost: " + alt.impedance_cost + "<br>Detour: " + alt.detour_ratio_dist + "x<br>Shared Overlap: " + alt.overlap_ratio_pct + "%<br>Turns: " + alt.turns.total_turns + "<br>Arterial: " + alt.road_classes.macro_pct.arterial_pct + "%<br>Residential: " + alt.road_classes.macro_pct.residential_pct + "%");
            overlayMaps["Offset Alt " + (i+1)] = line;
        }});

        // Yen alternatives
        var yenColors = ['#d62728', '#e377c2', '#8c564b'];
        var yenAlts = {json.dumps(yen_alts)};
        yenAlts.forEach(function(yen, i) {{
            var col = yenColors[i % yenColors.length];
            var line = L.polyline(yen.coordinates, {{
                color: col, weight: 3, opacity: 0.8, dashArray: '6, 6'
            }}).addTo(map);
            line.bindPopup("<b>Yen KSP Alt " + (i+1) + "</b><br>Distance: " + yen.distance_km + " km<br>Cost: " + yen.impedance_cost + "<br>Detour: " + yen.detour_ratio_dist + "x<br>Shared Overlap: " + yen.overlap_ratio_pct + "% (Survives <=70%: " + yen.survives_70pct_filter + ")<br>Turns: " + yen.turns.total_turns);
            overlayMaps["Yen Alt " + (i+1)] = line;
        }});

        // Start & End markers
        var startMarker = L.circleMarker([{start_lat}, {start_lng}], {{
            radius: 8, fillColor: '#00aa00', color: '#003300', weight: 2, fillOpacity: 0.95
        }}).addTo(map).bindPopup("<b>Origin:</b> {corridor['name'].split(' to ')[0]}");

        var endMarker = L.circleMarker([{end_lat}, {end_lng}], {{
            radius: 8, fillColor: '#cc0000', color: '#660000', weight: 2, fillOpacity: 0.95
        }}).addTo(map).bindPopup("<b>Destination:</b> {corridor['name'].split(' to ')[1]}");

        L.control.layers(null, overlayMaps, {{ collapsed: false }}).addTo(map);
        map.fitBounds(primaryLine.getBounds(), {{ padding: [30, 30] }});
    </script>
</body>
</html>
"""
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Saved interactive Leaflet map HTML: {out_html}")


def densify_coordinates_with_geometry(G, coord_to_node, coords):
    """
    Interpolate intermediate LineString shape points between consecutive nodes.
    Preserves exact endpoints while restoring true physical road curvature.
    """
    if not coords or len(coords) < 2:
        return coords

    dense = []
    for i in range(len(coords) - 1):
        c1 = tuple(coords[i])
        c2 = tuple(coords[i + 1])
        u = coord_to_node.get(c1)
        v = coord_to_node.get(c2)
        if u and v and G.has_edge(u, v):
            ed = min(G[u][v].values(), key=lambda d: float(d.get("length", 1.0)))
            if "geometry" in ed and hasattr(ed["geometry"], "coords"):
                pts = list(ed["geometry"].coords)
                if dense:
                    pts = pts[1:]
                for p in pts:
                    dense.append([round(p[1], 6), round(p[0], 6)])
                continue

        if not dense:
            dense.append(list(c1))
        dense.append(list(c2))

    return dense


def render_all_visualizations():
    print("=" * 80)
    print("GENERATING MAP VISUALIZATIONS FOR REPRESENTATIVE BENGALURU CORRIDORS")
    print("=" * 80)

    if not os.path.exists(IN_JSON):
        print(f"Error: Raw evaluation data not found at {IN_JSON}")
        return

    print("Loading graph for geometry densification...")
    graph_manager.load_graph()
    G = graph_manager.G
    coord_to_node = {(round(d["y"], 6), round(d["x"], 6)): n for n, d in G.nodes(data=True)}
    print(f"Graph loaded ({G.number_of_nodes()} nodes).")

    with open(IN_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    corridor_map = {c["id"]: c for c in data}
    densified_corridor_map = {}

    for cid, meta in CASE_STUDY_METADATA.items():
        if cid not in corridor_map:
            print(f"Warning: {cid} not found in evaluation dataset.")
            continue

        c_data = copy.deepcopy(corridor_map[cid])
        if "primary_route" in c_data and "coordinates" in c_data["primary_route"]:
            c_data["primary_route"]["coordinates"] = densify_coordinates_with_geometry(
                G, coord_to_node, c_data["primary_route"]["coordinates"]
            )
        for alt in c_data.get("perpendicular_offset_alternatives", []):
            if "coordinates" in alt:
                alt["coordinates"] = densify_coordinates_with_geometry(G, coord_to_node, alt["coordinates"])
        for yen in c_data.get("yen_ksp_alternatives", []):
            if "coordinates" in yen:
                yen["coordinates"] = densify_coordinates_with_geometry(G, coord_to_node, yen["coordinates"])

        densified_corridor_map[cid] = c_data

        out_png = os.path.join(OUT_DIR, f"map_{meta['slug']}.png")
        out_html = os.path.join(OUT_DIR, f"map_{meta['slug']}.html")

        print(f"\nProcessing {cid}: {c_data['name']} (geometry densified)...")
        render_matplotlib_map(c_data, meta, out_png)
        render_leaflet_html_map(c_data, meta, out_html)

    # Multi-panel composite summary figure
    render_multi_panel_summary(densified_corridor_map)


def render_multi_panel_summary(corridor_map):
    """Generate a 2x2 multi-panel composite figure comparing representative corridors."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 14), dpi=300)
    selected_cids = ["OD_01", "OD_04", "OD_06", "OD_12"]

    for ax, cid in zip(axes.flat, selected_cids):
        if cid not in corridor_map:
            continue
        c_data = corridor_map[cid]
        meta = CASE_STUDY_METADATA[cid]
        prim = c_data["primary_route"]
        prim_coords = prim["coordinates"]

        p_lats = [c[0] for c in prim_coords]
        p_lngs = [c[1] for c in prim_coords]

        # Yen paths
        for idx, yen in enumerate(c_data.get("yen_ksp_alternatives", [])[:2]):
            y_coords = yen["coordinates"]
            if y_coords:
                ax.plot([c[1] for c in y_coords], [c[0] for c in y_coords],
                        color="#d62728", linestyle="--", linewidth=1.5, alpha=0.8,
                        label=f"Yen Alt {idx+1} ({yen['overlap_ratio_pct']}% ovlp)")

        # Offset paths
        off_colors = ["#2ca02c", "#ff7f0e", "#9467bd"]
        for idx, alt in enumerate(c_data.get("perpendicular_offset_alternatives", [])):
            a_coords = alt["coordinates"]
            if a_coords:
                ax.plot([c[1] for c in a_coords], [c[0] for c in a_coords],
                        color=off_colors[idx % len(off_colors)], linestyle="-", linewidth=2.0, alpha=0.9,
                        label=f"Offset Alt {idx+1} ({alt['overlap_ratio_pct']}% ovlp)")

        # Primary path
        ax.plot(p_lngs, p_lats, color="#1f77b4", linestyle="-", linewidth=2.8,
                label=f"Primary ({prim['distance_km']}km)")

        # Markers
        s_lat, s_lng = c_data["from_coords"]
        e_lat, e_lng = c_data["to_coords"]
        ax.scatter([s_lng], [s_lat], color="#00aa00", s=100, marker="o", edgecolors="black", zorder=6)
        ax.scatter([e_lng], [e_lat], color="#cc0000", s=120, marker="s", edgecolors="black", zorder=6)

        ax.set_title(f"{cid}: {c_data['name']}\n{meta['subtitle']}", fontsize=9.5, fontweight="bold")
        ax.set_xlabel("Longitude (°E)", fontsize=8)
        ax.set_ylabel("Latitude (°N)", fontsize=8)
        ax.grid(True, linestyle=":", alpha=0.5)
        ax.legend(loc="upper right", fontsize=7.5, framealpha=0.9)

    plt.suptitle("Comparative Route Topologies across Bengaluru Urban Case Studies", fontsize=13, fontweight="bold", y=0.99)
    plt.tight_layout()
    out_composite = os.path.join(OUT_DIR, "all_case_studies_multi_panel.png")
    plt.savefig(out_composite, dpi=300)
    plt.close(fig)
    print(f"\nSaved composite multi-panel figure: {out_composite}")


if __name__ == "__main__":
    render_all_visualizations()
