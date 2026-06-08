"use client";

import { APIProvider } from "@vis.gl/react-google-maps";

export function Providers({ children }: { children: React.ReactNode }) {
    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY as string;

    if (!apiKey) {
        return (
            <div className="flex items-center justify-center h-screen bg-red-50 text-red-600 font-bold">
                Error: Missing NEXT_PUBLIC_GOOGLE_MAPS_API_KEY in .env file
            </div>
        );
    }

    return (
        <APIProvider apiKey={apiKey} version="weekly">
            {children}
        </APIProvider>
    );
}