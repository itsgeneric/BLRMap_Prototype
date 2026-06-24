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
    const [metrics, setMetrics] = useState<{ dist: string; time: string; strategy: string } | null>(null);
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
        // ADD geometryLib and map to this safety check
        if (!origin || !dest || !geometryLib || !map) {
            alert("Please select valid locations, and wait for the map to load.");
            return;
        }
        setIsCalculating(true);

        // ... the rest of the mock data logic remains exactly the same ...

        // 1. THE MOCK DATA: A hardcoded list of back-alley intersections (Max 25 points)
        // This simulates what your Python OSMnx server WILL return in the future.
        const mockOsmWaypoints = [
            { lat: 12.9430, lng: 77.6320 }, // Point 1: Ejipura Main Road
            { lat: 12.9560, lng: 77.6530 }, // Point 2: Wind Tunnel Road (HAL Backwall)
            { lat: 12.9450, lng: 77.6750 }, // Point 3: Yemalur / Bellandur Lake Road
            { lat: 12.9380, lng: 77.7120 }, // Point 4: Panathur Railway Underpass
            { lat: 12.9510, lng: 77.7350 }, // Point 5: Varthur Kodi / Whitefield Backroads
        ];

        // 2. Format the mock coordinates into Google's strict RouteMatrix schema
        const googleIntermediates = mockOsmWaypoints.map((coord) => ({
            location: {
                latLng: {
                    latitude: coord.lat,
                    longitude: coord.lng
                }
            },
            via: true
        }));

        // 3. The Payload: Notice we are injecting our mock data into the 'intermediates' array
        const requestBody: any = {
            origin: { placeId: origin.id },
            destination: { placeId: dest.id },
            intermediates: googleIntermediates,
            travelMode: "TWO_WHEELER",
            units: "METRIC",
            routingPreference: "TRAFFIC_AWARE_OPTIMAL",
            // Force Google to obey our waypoints rather than taking liberties
            routeModifiers: { avoidHighways: false, avoidTolls: false }
        };

        try {
            const response = await fetch("https://routes.googleapis.com/directions/v2:computeRoutes", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": apiKey,
                    "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline",
                },
                body: JSON.stringify(requestBody),
            });

            const data = await response.json();

            if (data.routes && data.routes.length > 0) {
                const route = data.routes[0];

                // Clear old paths
                activePolylines.forEach(p => p.setMap(null));

                // Decode and draw the new forced path
                const decodedPath = geometryLib.encoding.decodePath(route.polyline.encodedPolyline);
                const newPath = new google.maps.Polyline({
                    path: decodedPath,
                    strokeColor: "#10B981", // Emerald green for our custom shortcut
                    strokeWeight: 6,
                    strokeOpacity: 1.0,
                    map: map,
                });

                setActivePolylines([newPath]);

                // Update UI Metrics
                setMetrics({
                    dist: (route.distanceMeters / 1000).toFixed(2) + " KM",
                    time: Math.round(parseInt(route.duration.replace("s", "")) / 60) + " Mins",
                    strategy: "Custom OSM-Forced Grid Route"
                });
            }
        } catch (error) {
            console.error("Hybrid routing failed:", error);
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
                    <div className="bg-purple-50 p-4 rounded-lg border border-purple-200 shadow-sm">
                        <p className="text-xs text-purple-600 uppercase font-bold mb-2">⭐ The Ultimate Path</p>

                        <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-semibold text-gray-700">Distance</span>
                            <span className="text-xl font-black text-purple-900">{metrics.dist}</span>
                        </div>

                        <div className="flex justify-between items-center mb-3">
                            <span className="text-sm font-semibold text-gray-700">Time</span>
                            <span className="text-xl font-black text-purple-900">{metrics.time}</span>
                        </div>

                        <div className="pt-3 border-t border-purple-200/50">
                            <span className="text-xs text-purple-500 font-semibold uppercase block mb-1">Strategy Used</span>
                            <span className="text-sm font-bold text-purple-800 bg-purple-200/50 px-2 py-1 rounded inline-block">
                    {metrics.strategy}
                </span>
                        </div>
                    </div>
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