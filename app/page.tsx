"use client";

import { useState, useEffect, useRef } from "react";
import { Map, useMap, useMapsLibrary, AdvancedMarker } from "@vis.gl/react-google-maps";

export default function Home() {
const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY as string;
const map = useMap();
const placesLib = useMapsLibrary("places");
const geometryLib = useMapsLibrary("geometry");

// State Management
const [origin, setOrigin] = useState<{ id: string; lat: number; lng: number } | null>(null);
const [dest, setDest] = useState<{ id: string; lat: number; lng: number } | null>(null);
const [trafficMode, setTrafficMode] = useState<string>("empty");
const [congestionLevel, setCongestionLevel] = useState<number>(3);
const [metrics, setMetrics] = useState<{ fastest: any; shortest: any } | null>(null);
const [isCalculating, setIsCalculating] = useState(false);

// DOM Refs for Autocomplete
const originContainerRef = useRef<HTMLDivElement>(null);
const destContainerRef = useRef<HTMLDivElement>(null);

// Map Drawing State
const [activePolylines, setActivePolylines] = useState<google.maps.Polyline[]>([]);
const [trafficLayer, setTrafficLayer] = useState<google.maps.TrafficLayer | null>(null);

// Instant Traffic Layer Toggle
useEffect(() => {
    if (!map) return;
    let layer = trafficLayer;
    if (!layer) {
        layer = new google.maps.TrafficLayer();
        setTrafficLayer(layer);
    }
    layer.setMap(trafficMode === "realtime" ? map : null);
}, [map, trafficMode, trafficLayer]);

// Autocomplete Setup
useEffect(() => {
    if (!placesLib || !originContainerRef.current || !destContainerRef.current) return;

    originContainerRef.current.innerHTML = "";
    destContainerRef.current.innerHTML = "";

    const originAutocomplete = new placesLib.PlaceAutocompleteElement({ includedRegionCodes: ["in"] });
    const destAutocomplete = new placesLib.PlaceAutocompleteElement({ includedRegionCodes: ["in"] });

    originContainerRef.current.appendChild(originAutocomplete);
    destContainerRef.current.appendChild(destAutocomplete);

    const handleOriginSelect = async (e: any) => {
        if (!e.placePrediction) return;
        const place = e.placePrediction.toPlace();
        await place.fetchFields({ fields: ["id", "location"] });
        setOrigin({ id: place.id, lat: place.location.lat(), lng: place.location.lng() });
    };

    const handleDestSelect = async (e: any) => {
        if (!e.placePrediction) return;
        const place = e.placePrediction.toPlace();
        await place.fetchFields({ fields: ["id", "location"] });
        setDest({ id: place.id, lat: place.location.lat(), lng: place.location.lng() });
    };

    originAutocomplete.addEventListener("gmp-select", handleOriginSelect);
    destAutocomplete.addEventListener("gmp-select", handleDestSelect);

    return () => {
        originAutocomplete.removeEventListener("gmp-select", handleOriginSelect);
        destAutocomplete.removeEventListener("gmp-select", handleDestSelect);
    };
}, [placesLib]);

const getSimulatedDepartureTime = (level: number) => {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    switch (level) {
        case 1: d.setDate(d.getDate() + (0 - d.getDay())); d.setHours(3, 0, 0, 0); break;
        case 2: d.setDate(d.getDate() + (1 - d.getDay())); d.setHours(11, 0, 0, 0); break;
        case 3: d.setDate(d.getDate() + (3 - d.getDay())); d.setHours(15, 0, 0, 0); break;
        case 4: d.setDate(d.getDate() + (4 - d.getDay())); d.setHours(18, 0, 0, 0); break;
        case 5: d.setDate(d.getDate() + (5 - d.getDay())); d.setHours(19, 0, 0, 0); break;
    }
    return d.toISOString();
};

const calculateRoute = async () => {
    if (!origin || !dest || !geometryLib || !map) {
        alert("Please select valid locations from the dropdowns.");
        return;
    }

    setIsCalculating(true);
    activePolylines.forEach(p => p.setMap(null));
    setActivePolylines([]);

    const baseRequestBody: any = {
        origin: { placeId: origin.id },
        destination: { placeId: dest.id },
        travelMode: "TWO_WHEELER",
        units: "METRIC",
        computeAlternativeRoutes: true,
    };

    if (trafficMode === "empty") baseRequestBody.routingPreference = "TRAFFIC_UNAWARE";
    else if (trafficMode === "realtime") baseRequestBody.routingPreference = "TRAFFIC_AWARE";
    else if (trafficMode === "congestion") {
        baseRequestBody.routingPreference = "TRAFFIC_AWARE_OPTIMAL";
        baseRequestBody.departureTime = getSimulatedDepartureTime(congestionLevel);
    }

    // Two parallel strategies to flood the pool with options without breaking the map grid
    const strategies = [
        {
            id: "standard",
            label: "Standard Routes",
            body: { ...baseRequestBody, routeModifiers: { avoidTolls: true } } // Default 2W behavior
        },
        {
            id: "expressway",
            label: "NICE Road Enabled",
            body: { ...baseRequestBody, routeModifiers: { avoidTolls: false } } // Unlocks NICE
        }
    ];

    try {
        const results = await Promise.all(
            strategies.map(async (strat) => {
                const response = await fetch("https://routes.googleapis.com/directions/v2:computeRoutes", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Goog-Api-Key": apiKey,
                        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline",
                    },
                    body: JSON.stringify(strat.body),
                });
                const data = await response.json();
                return data.routes || [];
            })
        );

        // Flatten, parse, and strictly deduplicate overlapping routes using the polyline string
        // Explicitly call the native JS Map
        const uniqueRoutesMap = new globalThis.Map();
        results.flat().forEach((route: any) => {
            const encoded = route.polyline.encodedPolyline;
            if (!uniqueRoutesMap.has(encoded)) {
                uniqueRoutesMap.set(encoded, {
                    distanceMeters: route.distanceMeters,
                    durationSeconds: parseInt(route.duration.replace("s", "")),
                    encodedPolyline: encoded,
                    distStr: (route.distanceMeters / 1000).toFixed(2) + " KM",
                    timeStr: Math.round(parseInt(route.duration.replace("s", "")) / 60) + " Mins"
                });
            }
        });

        const allParsedRoutes = Array.from(uniqueRoutesMap.values());

        if (allParsedRoutes.length === 0) {
            alert("Routing engine failed to find any paths.");
            setIsCalculating(false);
            return;
        }

        // Client-Side Data Mining: Isolate the two most important routes
        const fastestRoute = allParsedRoutes.reduce((prev, curr) =>
            (prev.durationSeconds < curr.durationSeconds) ? prev : curr
        );

        const shortestRoute = allParsedRoutes.reduce((prev, curr) =>
            (prev.distanceMeters < curr.distanceMeters) ? prev : curr
        );

        setMetrics({ fastest: fastestRoute, shortest: shortestRoute });

        // Render logic
        const newPolylines = allParsedRoutes.map((route) => {
            const isFastest = route === fastestRoute;
            const isShortest = route === shortestRoute;
            const isBoth = isFastest && isShortest;

            const decodedPath = geometryLib.encoding.decodePath(route.encodedPolyline);

            let strokeColor = "#9CA3AF"; // Gray for ignored alternatives
            let zIndex = 10;
            let opacity = 0.4;
            let weight = 4;

            if (isBoth) {
                strokeColor = "#8B5CF6"; // Purple (Ultimate Route)
                zIndex = 100;
                opacity = 1.0;
                weight = 6;
            } else if (isFastest) {
                strokeColor = "#2563EB"; // Blue (Fastest Time)
                zIndex = 90;
                opacity = 1.0;
                weight = 6;
            } else if (isShortest) {
                strokeColor = "#10B981"; // Green (Sneaky Shortcut / Shortest Distance)
                zIndex = 80;
                opacity = 1.0;
                weight = 6;
            }

            return new google.maps.Polyline({
                path: decodedPath,
                strokeColor,
                strokeWeight: weight,
                strokeOpacity: opacity,
                zIndex,
                map: map,
            });
        });

        setActivePolylines(newPolylines);

        const bounds = new google.maps.LatLngBounds();
        bounds.extend({ lat: origin.lat, lng: origin.lng });
        bounds.extend({ lat: dest.lat, lng: dest.lng });
        map.fitBounds(bounds, 50);

    } catch (error) {
        console.error("Multi-routing error:", error);
        alert("Failed to connect to the Routes API.");
    } finally {
        setIsCalculating(false);
    }
};

return (
    <main className="flex flex-col md:flex-row h-screen bg-gray-50 font-sans">
        <div className="w-full md:w-96 bg-white p-6 shadow-lg z-10 overflow-y-auto">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Bengaluru 2W Logic</h2>

            <div className="mb-4 relative">
                <label className="block text-sm font-semibold text-gray-700 mb-2">Source Location</label>
                <div ref={originContainerRef} className="w-full min-h-[40px] border border-gray-300 rounded" />
            </div>

            <div className="mb-6 relative">
                <label className="block text-sm font-semibold text-gray-700 mb-2">Destination Location</label>
                <div ref={destContainerRef} className="w-full min-h-[40px] border border-gray-300 rounded" />
            </div>

            <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-3">Traffic Environment</label>
                <div className="space-y-3">
                    <label className="flex items-center space-x-3 cursor-pointer p-2 hover:bg-gray-50 rounded">
                        <input type="radio" name="traffic" value="empty" checked={trafficMode === "empty"} onChange={(e) => setTrafficMode(e.target.value)} className="w-4 h-4 text-blue-600" />
                        <span className="text-gray-700 font-medium">Empty Traffic</span>
                    </label>

                    <label className="flex items-center space-x-3 cursor-pointer p-2 hover:bg-gray-50 rounded">
                        <input type="radio" name="traffic" value="realtime" checked={trafficMode === "realtime"} onChange={(e) => setTrafficMode(e.target.value)} className="w-4 h-4 text-blue-600" />
                        <span className="text-gray-700 font-medium">Real Time</span>
                    </label>

                    <div className="bg-gray-50 p-3 rounded border border-gray-200">
                        <label className="flex items-center space-x-3 cursor-pointer mb-3">
                            <input type="radio" name="traffic" value="congestion" checked={trafficMode === "congestion"} onChange={(e) => setTrafficMode(e.target.value)} className="w-4 h-4 text-blue-600" />
                            <span className="text-gray-700 font-medium">Simulate Congestion</span>
                        </label>

                        {trafficMode === "congestion" && (
                            <div className="pl-7 pr-2">
                                <div className="flex justify-between text-xs text-gray-500 mb-1">
                                    <span>Light</span>
                                    <span className="text-red-500 font-bold">Gridlock</span>
                                </div>
                                <input
                                    type="range"
                                    min="1"
                                    max="5"
                                    value={congestionLevel}
                                    onChange={(e) => setCongestionLevel(parseInt(e.target.value))}
                                    className="w-full h-2 bg-gray-300 rounded-lg appearance-none cursor-pointer accent-orange-500"
                                />
                                <div className="text-center text-xs mt-2 font-semibold text-gray-600">
                                    Intensity Level: {congestionLevel} / 5
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <button
                onClick={calculateRoute}
                disabled={isCalculating}
                className={`w-full text-white font-bold py-3 rounded-md transition duration-200 shadow-md ${isCalculating ? "bg-gray-400 cursor-not-allowed" : "bg-gray-900 hover:bg-black"}`}
            >
                {isCalculating ? "Mining Alternatives..." : "Find Best 2W Paths"}
            </button>

            {metrics && (
                <div className="mt-6 space-y-4">
                    {/* Purple state if both paths are identical */}
                    {metrics.fastest === metrics.shortest ? (
                        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200 shadow-sm">
                            <p className="text-xs text-purple-600 uppercase font-bold mb-2">⭐ The Ultimate Path</p>
                            <div className="flex justify-between">
                                <span className="text-xl font-black text-purple-900">{metrics.fastest.distStr}</span>
                                <span className="text-xl font-black text-purple-900">{metrics.fastest.timeStr}</span>
                            </div>
                        </div>
                    ) : (
                        <>
                            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 shadow-sm">
                                <p className="text-xs text-blue-600 uppercase font-bold mb-2">🔵 Fastest Time (Arterial/NICE)</p>
                                <div className="flex justify-between">
                                    <span className="text-xl font-black text-blue-900">{metrics.fastest.distStr}</span>
                                    <span className="text-xl font-black text-blue-900">{metrics.fastest.timeStr}</span>
                                </div>
                            </div>
                            <div className="bg-green-50 p-4 rounded-lg border border-green-200 shadow-sm">
                                <p className="text-xs text-green-600 uppercase font-bold mb-2">🟢 Sneaky Shortcut (Shortest Dist)</p>
                                <div className="flex justify-between">
                                    <span className="text-xl font-black text-green-900">{metrics.shortest.distStr}</span>
                                    <span className="text-xl font-black text-green-900">{metrics.shortest.timeStr}</span>
                                </div>
                            </div>
                        </>
                    )}
                </div>
            )}
        </div>

        <div className="flex-grow h-[50vh] md:h-full relative">
            <Map
                defaultCenter={{ lat: 12.9716, lng: 77.5946 }}
                defaultZoom={12}
                mapId="DEMO_MAP_ID"
                disableDefaultUI={true}
            >
                {origin && <AdvancedMarker position={{ lat: origin.lat, lng: origin.lng }} title="Origin" />}
                {dest && <AdvancedMarker position={{ lat: dest.lat, lng: dest.lng }} title="Destination" />}
            </Map>
        </div>
    </main>
);


}