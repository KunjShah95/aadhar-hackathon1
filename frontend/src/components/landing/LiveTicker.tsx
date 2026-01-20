import { motion } from 'framer-motion';
import { useDashboardData } from '../../hooks/useDashboardData';
import { ArrowDown, ArrowUp } from 'lucide-react';

export function LiveTicker() {
    const { data } = useDashboardData();

    if (!data) return <div className="h-12 bg-[#030712]/90 border-y border-white/5" />;

    // Create 4 copies for smooth infinite scroll on large screens
    const tickerContent = [...data.kpis, ...data.kpis, ...data.kpis, ...data.kpis];

    return (
        <div className="w-full bg-[#030712]/90 backdrop-blur-md border-y border-white/5 py-2 overflow-hidden flex items-center h-12 relative z-40">
            <div className="flex items-center gap-2 px-4 border-r border-white/10 shrink-0 bg-[#030712]/90 z-10 h-full relative">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-xs font-mono text-emerald-500 font-bold tracking-wider">LIVE NET</span>
            </div>

            <div className="relative overflow-hidden w-full flex-1">
                <motion.div
                    className="flex items-center gap-12 px-4 whitespace-nowrap"
                    animate={{ x: ["0%", "-25%"] }}
                    transition={{ repeat: Infinity, duration: 30, ease: "linear" }}
                >
                    {tickerContent.map((kpi, i) => (
                        <div key={`${kpi.id}-${i}`} className="flex items-center gap-3 shrink-0">
                            <span className="text-xs text-gray-500 uppercase font-mono">{kpi.label}</span>
                            <span className="text-sm font-bold text-white font-mono">
                                {typeof kpi.value === 'number' ? kpi.value.toLocaleString() : kpi.value}
                                <span className="text-xs text-gray-500 ml-0.5">{kpi.unit}</span>
                            </span>
                            <div className={`flex items-center text-xs ${kpi.trend === 'up' ? 'text-emerald-500' : kpi.trend === 'down' ? 'text-red-500' : 'text-gray-500'}`}>
                                {kpi.trend === 'up' ? <ArrowUp className="w-3 h-3" /> : kpi.trend === 'down' ? <ArrowDown className="w-3 h-3" /> : null}
                                {Math.abs(kpi.delta)}%
                            </div>
                        </div>
                    ))}
                </motion.div>
            </div>
        </div>
    );
}
