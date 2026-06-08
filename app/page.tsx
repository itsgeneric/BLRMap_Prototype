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
    const [congestionLevel, setCongestionLevel] = useState<number>(3); // Slider State (1-5)
    const [metrics, setMetrics] = useState<{ dist: string; time: string } | null>(null);

    // DOM Refs for Autocomplete
    const originContainerRef = useRef<HTMLDivElement>(null);
    const destContainerRef = useRef<HTMLDivElement>(null);

    // Map Drawing State
    const [routePath, setRoutePath] = useState<google.maps.Polyline | null>(null);
    const [trafficLayer, setTrafficLayer] = useState<google.maps.TrafficLayer | null>(null);

    // Instant Traffic Layer Toggle (Only for Live Traffic)
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

        const originAutocomplete = new placesLib.PlaceAutocompleteElement({
            includedRegionCodes: ["in"],
        });
        const destAutocomplete = new placesLib.PlaceAutocompleteElement({
            includedRegionCodes: ["in"],
        });

        originContainerRef.current.appendChild(originAutocomplete);
        destContainerRef.current.appendChild(destAutocomplete);

        originAutocomplete.addEventListener("gmp-select", async (e: any) => {
            if (!e.placePrediction) return;
            const place = e.placePrediction.toPlace();
            await place.fetchFields({ fields: ["id", "location"] });
            setOrigin({ id: place.id, lat: place.location.lat(), lng: place.location.lng() });
        });

        destAutocomplete.addEventListener("gmp-select", async (e: any) => {
            if (!e.placePrediction) return;
            const place = e.placePrediction.toPlace();
            await place.fetchFields({ fields: ["id", "location"] });
            setDest({ id: place.id, lat: place.location.lat(), lng: place.location.lng() });
        });
    }, [placesLib]);

    // Helper function to trick Google into simulating various traffic severities
    const getSimulatedDepartureTime = (level: number) => {
        const d = new Date();
        d.setDate(d.getDate() + 7); // Push exactly one week into the future to guarantee validity

        switch (level) {
            case 1: // Empty: Sunday 3 AM
                d.setDate(d.getDate() + (0 - d.getDay()));
                d.setHours(3, 0, 0, 0);
                break;
            case 2: // Light: Monday 11 AM
                d.setDate(d.getDate() + (1 - d.getDay()));
                d.setHours(11, 0, 0, 0);
                break;
            case 3: // Moderate: Wednesday 3 PM
                d.setDate(d.getDate() + (3 - d.getDay()));
                d.setHours(15, 0, 0, 0);
                break;
            case 4: // Heavy: Thursday 6 PM
                d.setDate(d.getDate() + (4 - d.getDay()));
                d.setHours(18, 0, 0, 0);
                break;
            case 5: // Gridlock: Friday 7 PM
                d.setDate(d.getDate() + (5 - d.getDay()));
                d.setHours(19, 0, 0, 0);
                break;
        }
        return d.toISOString();
    };

    const calculateRoute = async () => {
        if (!origin || !dest || !geometryLib) {
            alert("Please select valid locations from the dropdowns.");
            return;
        }

        const requestBody: any = {
            origin: { placeId: origin.id },
            destination: { placeId: dest.id },
            travelMode: "TWO_WHEELER",
            units: "METRIC",
        };

        if (trafficMode === "empty") {
            requestBody.routingPreference = "TRAFFIC_UNAWARE";
        } else if (trafficMode === "realtime") {
            requestBody.routingPreference = "TRAFFIC_AWARE";
        } else if (trafficMode === "congestion") {
            requestBody.routingPreference = "TRAFFIC_AWARE_OPTIMAL";
            requestBody.departureTime = getSimulatedDepartureTime(congestionLevel);
        }

        try {
            const res = await fetch("https://routes.googleapis.com/directions/v2:computeRoutes", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": apiKey,
                    "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline",
                },
                body: JSON.stringify(requestBody),
            });

            const data = await res.json();

            if (data.routes && data.routes.length > 0) {
                const route = data.routes[0];

                const distKm = (route.distanceMeters / 1000).toFixed(2) + " KM";
                const timeMins = Math.round(parseInt(route.duration.replace("s", "")) / 60) + " Mins";
                setMetrics({ dist: distKm, time: timeMins });

                const decodedPath = geometryLib.encoding.decodePath(route.polyline.encodedPolyline);
                if (routePath) routePath.setMap(null);

                // Dynamic Route Colors based on severity
                let routeColor = "#1E88E5"; // Default Blue
                if (trafficMode === "realtime") routeColor = "#43A047"; // Live Green
                if (trafficMode === "congestion") {
                    const intensityColors = ["#FFB74D", "#FF9800", "#F57C00", "#E65100", "#B71C1C"];
                    routeColor = intensityColors[congestionLevel - 1];
                }

                const newPath = new google.maps.Polyline({
                    path: decodedPath,
                    strokeColor: routeColor,
                    strokeWeight: 6,
                    strokeOpacity: 0.8,
                    map: map,
                });
                setRoutePath(newPath);

                if (map) {
                    const bounds = new google.maps.LatLngBounds();
                    bounds.extend({ lat: origin.lat, lng: origin.lng });
                    bounds.extend({ lat: dest.lat, lng: dest.lng });
                    map.fitBounds(bounds, 50);
                }
            } else {
                alert("Routing engine failed to find a path.");
            }
        } catch (error) {
            console.error("Routing error:", error);
            alert("Failed to connect to the Routes API.");
        }
    };

    return (
        <main className="flex flex-col md:flex-row h-screen bg-gray-50 font-sans">
            <div className="w-full md:w-96 bg-white p-6 shadow-lg z-10 overflow-y-auto">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">Dynamic Routing Hub</h2>

                <div className="mb-4 relative">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Source Location</label>
                    <div ref={originContainerRef} className="w-full" />
                </div>

                <div className="mb-6 relative">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Destination Location</label>
                    <div ref={destContainerRef} className="w-full" />
                </div>

                <div className="mb-6">
                    <label className="block text-sm font-semibold text-gray-700 mb-3">Traffic Environment</label>
                    <div className="space-y-3">

                        <label className="flex items-center space-x-3 cursor-pointer p-2 hover:bg-gray-50 rounded">
                            <input type="radio" name="traffic" value="empty" checked={trafficMode === "empty"} onChange={(e) => setTrafficMode(e.target.value)} className="w-4 h-4 text-blue-600 focus:ring-blue-500" />
                            <span className="text-gray-700 font-medium">Empty Traffic</span>
                        </label>

                        <label className="flex items-center space-x-3 cursor-pointer p-2 hover:bg-gray-50 rounded">
                            <input type="radio" name="traffic" value="realtime" checked={trafficMode === "realtime"} onChange={(e) => setTrafficMode(e.target.value)} className="w-4 h-4 text-blue-600 focus:ring-blue-500" />
                            <span className="text-gray-700 font-medium">Real Time</span>
                        </label>

                        <div className="bg-gray-50 p-3 rounded border border-gray-200">
                            <label className="flex items-center space-x-3 cursor-pointer mb-3">
                                <input type="radio" name="traffic" value="congestion" checked={trafficMode === "congestion"} onChange={(e) => setTrafficMode(e.target.value)} className="w-4 h-4 text-blue-600 focus:ring-blue-500" />
                                <span className="text-gray-700 font-medium">Simulate Congestion</span>
                            </label>

                            {/* The Dynamic Slider */}
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
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-md transition duration-200 shadow-md"
                >
                    Calculate & Render Route
                </button>

                {metrics && (
                    <div className="mt-8 bg-blue-50 p-5 rounded-lg border border-blue-100 shadow-inner">
                        <div className="mb-4">
                            <p className="text-xs text-gray-500 uppercase font-semibold">Evaluated Path Distance</p>
                            <p className="text-3xl font-black text-blue-700">{metrics.dist}</p>
                        </div>
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-semibold">Estimated Two-Wheeler Time</p>
                            <p className="text-3xl font-black text-blue-700">{metrics.time}</p>
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