import { fetchFromAPI } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Cloud, Droplets, Thermometer, Wind } from "lucide-react";

export default async function WeatherPage() {
    const data = await fetchFromAPI("/weather?hours=24");

    return (
        <div className="flex flex-col gap-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Weather Stations</h1>
                <p className="text-slate-500">
                    Real-time conditions from OpenWeatherMap nodes.
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {data?.map((w: any, i: number) => (
                    <Card key={i}>
                        <CardHeader>
                            <div className="flex justify-between items-start">
                                <CardTitle className="text-xl">{w.city}</CardTitle>
                                <Cloud className="h-6 w-6 text-slate-500" />
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-center justify-between mb-4">
                                <div>
                                    <span className="text-4xl font-bold">{w.temperature}°</span>
                                    <span className="text-xl text-slate-500 ml-1">C</span>
                                </div>
                                <div className="text-right">
                                    <div className="font-medium text-slate-700 dark:text-slate-300">{w.condition}</div>
                                    <div className="text-xs text-slate-500">{new Date(w.time).toLocaleTimeString()}</div>
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div className="flex items-center gap-2">
                                    <Droplets className="h-4 w-4 text-blue-500" />
                                    <span>Humidity: {w.humidity}%</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Wind className="h-4 w-4 text-slate-500" />
                                    <span>Pressure: {w.pressure}</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}
