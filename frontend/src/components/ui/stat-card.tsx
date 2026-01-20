import { motion, useMotionTemplate, useMotionValue } from "framer-motion"
import { ArrowUpIcon, ArrowDownIcon, MinusIcon, Activity } from "lucide-react"
import { KPI } from "../../types"
import { cn, formatNumber } from "../../utils"
import { Card } from "./card"

interface StatCardProps {
    kpi: KPI;
}

export function StatCard({ kpi }: StatCardProps) {
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    function handleMouseMove({ currentTarget, clientX, clientY }: React.MouseEvent) {
        const { left, top } = currentTarget.getBoundingClientRect();
        mouseX.set(clientX - left);
        mouseY.set(clientY - top);
    }

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, ease: [0.23, 1, 0.32, 1] }} // "Apple" ease
            className="group relative"
            onMouseMove={handleMouseMove}
        >
            <div className="absolute -inset-px rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-r from-primary/50 to-science-400/50 blur-[1px] -z-10" />

            <Card className="relative overflow-hidden bg-[#030712]/50 backdrop-blur-xl border-white/5 h-full transition-all duration-300 group-hover:bg-[#030712]/70 group-hover:-translate-y-1 group-hover:translate-x-[1px]">
                {/* Spotlight Gradient */}
                <motion.div
                    className="pointer-events-none absolute -inset-px rounded-xl opacity-0 transition duration-300 group-hover:opacity-100"
                    style={{
                        background: useMotionTemplate`
                            radial-gradient(
                                650px circle at ${mouseX}px ${mouseY}px,
                                rgba(14, 165, 233, 0.15),
                                transparent 80%
                            )
                        `,
                    }}
                />

                <div className="p-6">
                    <div className="flex items-center justify-between">
                        <div className="space-y-1">
                            <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground/70 font-display">
                                {kpi.label}
                            </p>
                            <div className="flex items-baseline space-x-2">
                                <span className="text-3xl font-bold tracking-tight text-white font-mono">
                                    {formatNumber(kpi.value)}
                                </span>
                                {kpi.unit && (
                                    <span className="text-sm font-medium text-muted-foreground font-display">
                                        {kpi.unit}
                                    </span>
                                )}
                            </div>
                        </div>
                        <div className={cn(
                            "flex items-center justify-center w-10 h-10 rounded-full border bg-white/5 backdrop-blur-sm transition-colors",
                            kpi.isAnomaly ? "border-red-500/50 bg-red-500/10 text-red-400 animate-pulse-slow" : "border-white/10 text-primary"
                        )}>
                            <Activity className="w-5 h-5" />
                        </div>
                    </div>

                    <div className="mt-4 flex items-center justify-between text-xs">
                        <div className={cn(
                            "flex items-center space-x-1 px-2 py-0.5 rounded border backdrop-blur-md",
                            kpi.trend === 'up'
                                ? "text-emerald-400 border-emerald-500/20 bg-emerald-500/5"
                                : kpi.trend === 'down'
                                    ? "text-rose-400 border-rose-500/20 bg-rose-500/5"
                                    : "text-muted-foreground border-white/10 bg-white/5"
                        )}>
                            {kpi.trend === 'up' && <ArrowUpIcon className="w-3 h-3" />}
                            {kpi.trend === 'down' && <ArrowDownIcon className="w-3 h-3" />}
                            {kpi.trend === 'neutral' && <MinusIcon className="w-3 h-3" />}
                            <span className="font-medium font-mono">
                                {kpi.delta > 0 ? '+' : ''}{kpi.delta}%
                            </span>
                        </div>
                        <span className="text-muted-foreground/50 font-medium">
                            vs last period
                        </span>
                    </div>
                </div>

                {/* Bottom Active Beam */}
                <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-primary/50 to-transparent scale-x-0 group-hover:scale-x-100 transition-transform duration-700 ease-out" />
            </Card>
        </motion.div>
    )
}
