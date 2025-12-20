"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
    BarChart3,
    Database,
    Globe,
    Home,
    Waves,
    Activity,
    Cloud
} from "lucide-react"

const navItems = [
    { name: "Dashboard", href: "/", icon: Home },
    { name: "Earthquakes", href: "/earthquakes", icon: Activity },
    { name: "Weather", href: "/weather", icon: Cloud },
    { name: "Hydrology", href: "/hydrology", icon: Waves },

    { name: "Economy", href: "/economy", icon: BarChart3 },
    { name: "Catalog", href: "/catalog", icon: Database },
]

export function Sidebar() {
    const pathname = usePathname()

    return (
        <div className="hidden border-r bg-slate-50/40 dark:bg-slate-950/40 md:block w-64 h-screen fixed left-0 top-0">
            <div className="flex h-full max-h-screen flex-col gap-2">
                <div className="flex h-14 items-center border-b px-6">
                    <Link href="/" className="flex items-center gap-2 font-semibold">
                        <Globe className="h-6 w-6" />
                        <span>Nepal Data Hub</span>
                    </Link>
                </div>
                <div className="flex-1 overflow-auto py-2">
                    <nav className="grid items-start px-4 text-sm font-medium">
                        {navItems.map((item) => {
                            const Icon = item.icon
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        "flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:text-slate-900 dark:hover:text-slate-50",
                                        pathname === item.href
                                            ? "bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-50"
                                            : "text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
                                    )}
                                >
                                    <Icon className="h-4 w-4" />
                                    {item.name}
                                </Link>
                            )
                        })}
                    </nav>
                </div>
            </div>
        </div>
    )
}
