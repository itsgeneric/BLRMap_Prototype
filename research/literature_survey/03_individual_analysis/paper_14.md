# Individual Paper Analysis: Paper [14]

**Analysis Level:** Abstract & Detailed Publication Record Analysed  
**Citation Key:** `boeing2017osmnx`  
**Target Pillar:** Pillar 5 – OpenStreetMap & GIS Network Analytics  

---

### A. Bibliographic Information
* **Title:** OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks
* **Author:** Geoff Boeing
* **Publication Year:** 2017
* **Journal:** *Computers, Environment and Urban Systems*, Volume 65, pages 126–139 (14 pages)
* **Publisher:** Elsevier
* **DOI:** [10.1016/j.compenvurbsys.2017.05.004](https://doi.org/10.1016/j.compenvurbsys.2017.05.004)

---

### B. Research Problem
* **Core Problem:** Empirical urban street network analysis and routing research historically suffered from a severe bottleneck: acquiring, cleaning, constructing, and analyzing spatially explicit, non-planar street networks from raw OpenStreetMap (OSM) data was cumbersome, technically fragmented, and prone to severe topological errors. Raw OSM data consists of raw XML nodes, ways, and relations containing numerous artificial intermediate vertices (used solely to capture roadway curvature) rather than true street intersections.
* **Importance:** Urban planners, transport scientists, and routing engine developers require mathematically rigorous, topologically sound graph representations that preserve geometric curvature, directionality, and comprehensive infrastructural attributes.
* **Motivation:** Design and release an open-source Python toolchain (OSMnx) that automates the acquisition, topological simplification, metric analysis, and visualization of street networks from OpenStreetMap.

---

### C. Existing Research / Background
* **Previous Approaches:**
  1. *GIS Desktop Software (ArcGIS, QGIS):* Powerful visualization, but difficult to integrate into programmatic, automated graph algorithms or modern data science workflows.
  2. *Raw OpenStreetMap Parsers:* Built primitive graph representations that either treated every coordinate node as a graph vertex (exploding the graph size with false degree-2 nodes) or improperly flattened non-planar structures (such as overpasses, tunnels, and multi-level interchanges).
* **Identified Limitations:** Failure to topologically correct raw OSM data produces inaccurate connectivity metrics, inflated shortest-path search spaces, and erroneous node degree distributions.

---

### D. Methodology
* **Network Acquisition Pipeline:**
  - Interfaces programmatically with the Overpass API to query road networks by bounding box, polygon, address, or geographic distance buffer.
  - Supports configurable network filter profiles (e.g., `drive`, `walk`, `bike`, or custom infrastructure filters).
* **Graph Modeling as Directed MultiGraphs:**
  - Models street networks as non-planar directed multigraphs ($MultiDiGraph$) using NetworkX, allowing multiple parallel edges between the same two junctions (e.g., divided dual carriageways, service roads, separate turn ramps).
  - Explicitly preserves edge attributes: segment length, highway classification (`motorway`, `primary`, `secondary`, `tertiary`, `residential`, `living_street`), lane counts, maximum speed limits, one-way designations, and exact geospatial geometries (Shapely `LineString`).
* **Topological Simplification Algorithm:**
  - Identifies and consolidates all intermediate vertices of degree 2 that do not represent true intersections or dead ends.
  - Combines incident road segments into a single directed edge while storing the exact intermediate curvature coordinates within the edge's `geometry` attribute, preserving both spatial accuracy and topological purity.
* **Spatial Metric Capabilities:**
  - Computes street orientation entropy (compass rose distributions), average circuity, intersection density, connected component connectivity, and clustering coefficients.

---

### E. Results and Findings
* **Network Simplification & Memory Efficiency:** Topological simplification reduces raw node counts by **50% to 75%** while retaining 100% of the true spatial geometry and route connectivity, drastically speeding up graph search algorithms like Dijkstra and A\*.
* **Reproducibility & Scale:** Demonstrated automated downloading, construction, and analysis of complete street networks for 27,000 municipalities across the United States and global metropolitan areas within minutes.
* **Non-Planar Accuracy:** Proves that preserving overpasses, underpasses, and multi-tier highways as non-intersecting edges prevents false turning maneuvers that plague naive planar 2D GIS models.
* **Author Conclusion:** Programmatic graph extraction and strict topological simplification bridge the gap between crowdsourced geospatial data and rigorous network analysis.

---

### F. Limitations
* **Author-Stated Limitations:**
  1. Network construction time depends on public Overpass API server response times and rate-limiting throttles for large metropolitan bounding boxes.
  2. Data fidelity is fundamentally bounded by the quality and completeness of crowdsourced OpenStreetMap contributions in a given geographic region.
* **Critical Reading / Additional Limitations:**
  1. OSMnx is a graph construction and network analytics package; it does not provide an integrated high-performance routing engine with turn restrictions, dynamic traffic updates, or customizable multi-criteria heuristics.
  2. Processing very large regional networks (e.g., entire states or nations) in pure Python/NetworkX incurs heavy RAM consumption compared to compiled C++ graph structures.

---

### G. Relevance to My Project
* **Foundational Tooling & Graph Ingestion:** **Directly relevant.** OSMnx is the foundational tool used to download, clean, and export the entire road network of Bengaluru (`bengaluru_roads_full.graphml`) for our routing engine.
* **Attribute Preservation for Two-Wheeler Routing:** By retaining `highway`, `length`, `oneway`, and `geometry` attributes, OSMnx provides the essential metadata that our `routing/algorithms.py` and `routing/graph_manager.py` require to calculate road-type penalties (`main_road_penalty`, `inner_road_multiplier`, `service_multiplier`).
* **Geometric Turn Calculation:** The preservation of Shapely `LineString` coordinate geometries enables our engine to accurately compute segment bearings and intersection turning angles for our turn-aware A\* heuristic.

---

### H. Research Contribution
* Provides the standard academic and practical methodology for acquiring, cleaning, topologically simplifying, and modeling OpenStreetMap networks as directed multigraphs with rich infrastructural and geometric attributes.

---

### I. Potential Application
* **Existing Project Implementation:** Directly utilized in our data preparation pipeline (`data_pipeline/download_blr_osm.py` and `routing/graph_manager.py`) to build the spatial graph powering all route computations.
* **Feasibility Evaluation:** High operational feasibility; already functioning as the core geospatial foundation of our project.
