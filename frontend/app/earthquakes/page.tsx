import { fetchFromAPI } from "@/lib/api";
import { EarthquakeMap } from "@/components/dashboard/earthquake-map";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function EarthquakesPage() {
    const data = await fetchFromAPI("/earthquakes?limit=200");

    return (
        <div className="flex flex-col gap-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Earthquake Monitor</h1>
                <p className="text-slate-500">
                    Real-time seismic activity tracking across Nepal.
                </p>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Map takes 2 cols */}
                <div className="lg:col-span-2">
                    <EarthquakeMap earthquakes={data || []} />
                </div>

                {/* List takes 1 col */}
                <Card className="h-[465px] flex flex-col">
                    <CardHeader>
                        <CardTitle>Recent Events</CardTitle>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-auto pr-2">
                        <div className="space-y-4">
                            {data?.map((q: any) => (
                                <div key={q.id} className="flex items-start justify-between border-b pb-4 last:border-0 last:pb-0">
                                    <div className="space-y-1">
                                        <p className="text-sm font-medium leading-none">
                                            {q.place}
                                        </p>
                                        <p className="text-xs text-slate-500">
                                            {new Date(q.time).toLocaleTimeString()} · Depth: {q.depth}km
                                        </p>
                                    </div>
                                    <div className={`flex items-center justify-center h-8 w-10 index-1 rounded text-xs font-bold text-white ${q.magnitude >= 5 ? "bg-red-500" : "bg-orange-500"}`}>
                                        {q.magnitude}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
