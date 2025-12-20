import { fetchFromAPI } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Database, FileJson, Activity } from "lucide-react";

export default async function CatalogPage() {
    const datasets = await fetchFromAPI("/catalog");

    return (
        <div className="flex flex-col gap-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Data Catalog</h1>
                <p className="text-slate-500">
                    Explore managed datasets, schemas, and metadata.
                </p>
            </div>

            <div className="grid gap-6">
                {datasets?.map((ds: any) => (
                    <Card key={ds.id} className="group transition-all hover:shadow-md">
                        <CardHeader>
                            <div className="flex items-start justify-between">
                                <div className="space-y-1">
                                    <CardTitle className="text-xl flex items-center gap-2">
                                        <Database className="h-5 w-5 text-blue-500" />
                                        {ds.name}
                                    </CardTitle>
                                    <CardDescription>{ds.description}</CardDescription>
                                </div>
                                <div className="flex gap-2">
                                    <div className="px-2 py-1 bg-slate-100 rounded text-xs font-mono text-slate-600">
                                        {ds.schema_version}
                                    </div>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="grid md:grid-cols-2 gap-4 text-sm mt-2">
                                <div className="flex flex-col gap-1">
                                    <span className="text-slate-500">Owner Pipeline</span>
                                    <span className="font-medium">{ds.owner}</span>
                                </div>
                                <div className="flex flex-col gap-1">
                                    <span className="text-slate-500">Access</span>
                                    <div className="flex gap-2">
                                        <span className="inline-flex items-center gap-1 text-blue-600 bg-blue-50 px-2 py-0.5 rounded text-xs font-medium">
                                            <FileJson className="h-3 w-3" /> JSON API
                                        </span>
                                        <span className="inline-flex items-center gap-1 text-green-600 bg-green-50 px-2 py-0.5 rounded text-xs font-medium">
                                            <Activity className="h-3 w-3" /> Real-time
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}
