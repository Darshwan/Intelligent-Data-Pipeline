import { fetchFromAPI } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Waves } from "lucide-react";

export default async function HydrologyPage() {
    // Reusing dashboard alerts for now as full hydrology endpoint isn't separate, 
    // but usually we'd have /hydrology. Using alerts is fine for "Useful" view.
    const data = await fetchFromAPI("/alerts?hours=24");

    return (
        <div className="flex flex-col gap-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Hydrology Monitor</h1>
                <p className="text-slate-500">
                    Real-time water levels and flood warnings across major river basins.
                </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {data?.map((alert: any, i: number) => (
                    <Card key={i} className="overflow-hidden">
                        <div className={`h-2 w-full ${alert.severity === 'Danger' ? 'bg-red-500' : 'bg-yellow-500'}`} />
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-base font-semibold">{alert.station}</CardTitle>
                            <Waves className={`h-5 w-5 ${alert.severity === 'Danger' ? 'text-red-500' : 'text-yellow-500'}`} />
                        </CardHeader>
                        <CardContent>
                            <div className="mt-2 flex items-baseline gap-2">
                                <span className="text-3xl font-bold">{alert.water_level}</span>
                                <span className="text-sm text-slate-500">meters</span>
                            </div>
                            <div className="mt-4 space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-slate-500">Warning Level</span>
                                    <span className="font-medium">{alert.warning_level}m</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-slate-500">Danger Level</span>
                                    <span className="font-medium text-red-500">{alert.danger_level}m</span>
                                </div>
                            </div>
                            <div className="mt-4">
                                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${alert.severity === 'Danger'
                                        ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                                    }`}>
                                    {alert.severity?.toUpperCase()}
                                </span>
                            </div>
                        </CardContent>
                    </Card>
                ))}
                {(!data || data.length === 0) && (
                    <div className="col-span-3 text-center py-12 text-slate-500">
                        No active flood alerts at this time.
                    </div>
                )}
            </div>
        </div>
    );
}
