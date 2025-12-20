"use client"

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import "leaflet/dist/leaflet.css";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// Dynamic imports for Leaflet components to avoid SSR issues
const MapContainer = dynamic(
    () => import("react-leaflet").then((mod) => mod.MapContainer),
    { ssr: false }
);
const TileLayer = dynamic(
    () => import("react-leaflet").then((mod) => mod.TileLayer),
    { ssr: false }
);
const CircleMarker = dynamic(
    () => import("react-leaflet").then((mod) => mod.CircleMarker),
    { ssr: false }
);
const Popup = dynamic(
    () => import("react-leaflet").then((mod) => mod.Popup),
    { ssr: false }
);

export function EarthquakeMap({ earthquakes }: { earthquakes: any[] }) {
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    if (!isMounted) {
        return <div className="h-[400px] w-full bg-slate-100 dark:bg-slate-900 rounded-xl animate-pulse" />;
    }

    return (
        <Card className="col-span-4">
            <CardHeader>
                <CardTitle>Seismic Map</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                <div className="h-[400px] w-full rounded-b-xl overflow-hidden relative z-0">
                    <MapContainer
                        center={[28.3949, 84.1240]} // Nepal Center
                        zoom={7}
                        style={{ height: "100%", width: "100%" }}
                        scrollWheelZoom={false}
                    >
                        <TileLayer
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                        />
                        {earthquakes.map((quake) => (
                            <CircleMarker
                                key={quake.id}
                                center={[quake.latitude, quake.longitude]}
                                radius={quake.magnitude * 2}
                                pathOptions={{
                                    color: quake.magnitude >= 5 ? "#EF4444" : "#F59E0B",
                                    fillColor: quake.magnitude >= 5 ? "#EF4444" : "#F59E0B",
                                    fillOpacity: 0.6,
                                }}
                            >
                                <Popup>
                                    <div className="text-sm">
                                        <strong>M{quake.magnitude}</strong> {quake.place}
                                        <br />
                                        <span className="text-xs text-slate-500">
                                            {new Date(quake.time).toLocaleString()}
                                        </span>
                                    </div>
                                </Popup>
                            </CircleMarker>
                        ))}
                    </MapContainer>
                </div>
            </CardContent>
        </Card>
    );
}
