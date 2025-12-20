"use client"

import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

export function ForexChart({ data }: { data: any[] }) {
    // Process data to get latest rate per currency
    // Assumes input is list of history, we just want latest snapshot for bar chart
    // Or distinct currencies

    // Dedup by currency (keep first/latest)
    const uniqueData = Array.from(new Map(data.map(item => [item['currency'], item])).values());

    // Fix Recharts SSR hydration mismatch
    const [isMounted, setIsMounted] = React.useState(false);

    React.useEffect(() => {
        setIsMounted(true);
    }, []);

    if (!isMounted) return <div className="h-[350px] w-full animate-pulse bg-slate-100 rounded-lg"></div>;

    return (
        <Card className="col-span-4">
            <CardHeader>
                <CardTitle>Exchange Rates (vs NPR)</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[350px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={uniqueData}>
                            <XAxis
                                dataKey="currency"
                                stroke="#888888"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                            />
                            <YAxis
                                stroke="#888888"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                                tickFormatter={(value) => `Rs ${value}`}
                            />
                            <Tooltip
                                cursor={{ fill: 'transparent' }}
                                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                            />
                            <Bar dataKey="sell" radius={[4, 4, 0, 0]}>
                                {uniqueData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.currency === 'USD' ? '#2563EB' : '#64748B'} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
}
