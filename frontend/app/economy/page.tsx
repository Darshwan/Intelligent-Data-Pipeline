import { fetchFromAPI } from "@/lib/api";
import { ForexChart } from "@/components/dashboard/forex-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function EconomyPage() {
    const data = await fetchFromAPI("/forex?limit=50");

    return (
        <div className="flex flex-col gap-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Economy & Markets</h1>
                <p className="text-slate-500">
                    Foreign exchange rates and financial indicators.
                </p>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
                <ForexChart data={data || []} />

                <Card>
                    <CardHeader>
                        <CardTitle>Currency Board</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {data?.slice(0, 6).map((rate: any, i: number) => (
                                <div key={i} className="flex justify-between items-center border-b pb-2 last:border-0 last:pb-0">
                                    <div className="flex items-center gap-3">
                                        <div className="bg-slate-100 dark:bg-slate-800 p-2 rounded">
                                            <span className="font-bold">{rate.currency}</span>
                                        </div>
                                        <span className="text-sm text-slate-500">Unit: {rate.unit}</span>
                                    </div>
                                    <div className="text-right">
                                        <div className="font-bold text-lg">Rs. {rate.sell}</div>
                                        <div className="text-xs text-green-500">Buy: {rate.buy}</div>
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
