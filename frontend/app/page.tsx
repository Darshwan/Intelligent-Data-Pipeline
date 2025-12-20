import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Droplets, Waves, DollarSign } from "lucide-react";
import { fetchFromAPI } from "@/lib/api";

export default async function Dashboard() {
  const dashboardData = await fetchFromAPI('/dashboard');
  const forexData = await fetchFromAPI('/forex?limit=1');

  // Parse data
  const quakeCount = dashboardData?.earthquakes?.length || 0;
  const weatherCount = dashboardData?.weather?.length || 0;
  const alertCount = dashboardData?.alerts?.length || 0;

  // Get USD Rate safely
  const usdRate = forexData?.[0]?.currency === 'USD' ? forexData[0].sell : 'N/A';

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Command Center</h1>
        <p className="text-slate-500 dark:text-slate-400">Real-time situational awareness.</p>
      </div>

      {/* KPI Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Seismic Events</CardTitle>
            <Activity className="h-4 w-4 text-slate-500 dark:text-slate-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{quakeCount}</div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Last 24 hours
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Weather Nodes</CardTitle>
            <Droplets className="h-4 w-4 text-slate-500 dark:text-slate-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{weatherCount}</div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Active Stations
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Flood Alerts</CardTitle>
            <Waves className="h-4 w-4 text-slate-500 dark:text-slate-400" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${alertCount > 0 ? "text-red-500" : ""}`}>
              {alertCount}
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Current Warning Level
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">USD / NPR</CardTitle>
            <DollarSign className="h-4 w-4 text-slate-500 dark:text-slate-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Rs. {usdRate}</div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Latest Sell Rate
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Area - Placeholder for now */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {listRecent(dashboardData?.earthquakes)}
            </div>
          </CardContent>
        </Card>
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-green-500"></div>
              <span className="text-sm text-slate-600">Pipelines Operational</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function listRecent(quakes: any[]) {
  if (!quakes) return null;
  return quakes.slice(0, 5).map((q: any) => (
    <div key={q.id} className="flex items-center">
      <div className={`h-2 w-2 rounded-full mr-2 ${q.magnitude >= 5 ? 'bg-red-500' : 'bg-orange-400'}`}></div>
      <div className="ml-2 space-y-1">
        <p className="text-sm font-medium leading-none">M{q.magnitude} Earthquake</p>
        <p className="text-xs text-slate-500 dark:text-slate-400">{q.place}</p>
      </div>
      <div className="ml-auto font-medium text-xs text-slate-500">{new Date(q.time).toLocaleTimeString()}</div>
    </div>
  ));
}
