import React from 'react';
import { cn } from '../../utils/cn';
import { motion } from 'framer-motion';

interface StatCardProps {
    title: string;
    value: string | number;
    icon?: React.ReactNode;
    trend?: {
        value: number;
        isPositive: boolean;
    };
    className?: string;
    delay?: number;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, trend, className, delay = 0 }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay, duration: 0.4, ease: "easeOut" }}
            className={cn(
                "bg-[#0f172a]/60 backdrop-blur-xl border border-white/5 rounded-2xl p-6 relative overflow-hidden group",
                "hover:border-cyan-500/30 hover:shadow-[0_0_30px_-5px_rgba(6,182,212,0.15)] transition-all duration-500",
                className
            )}
        >
            {/* PBR Glare Effect */}
            <div className="absolute inset-0 bg-gradient-to-tr from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />

            <div className="flex justify-between items-start relative z-10">
                <div>
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-1.5">{title}</p>
                    <h3 className="text-3xl font-bold text-white tracking-tight drop-shadow-sm font-mono">
                        {value}
                    </h3>
                </div>
                {icon && (
                    <div className="p-3 bg-cyan-950/30 rounded-xl border border-cyan-500/10 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.1)] group-hover:scale-110 transition-transform duration-500">
                        {icon}
                    </div>
                )}
            </div>

            {trend && (
                <div className="mt-5 flex items-center relative z-10">
                    <div className={cn(
                        "text-xs font-bold px-2 py-1 rounded-md flex items-center border",
                        trend.isPositive
                            ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
                            : "text-rose-400 bg-rose-500/10 border-rose-500/20"
                    )}>
                        {trend.isPositive ? "▲" : "▼"} {trend.value}%
                    </div>
                    <span className="text-slate-500 text-[10px] font-medium uppercase tracking-wider ml-2.5 opacity-60">vs prev. period</span>
                </div>
            )}

            {/* Experimental Active Border Beam */}
            <div className="absolute bottom-0 left-0 h-[1px] w-0 bg-cyan-500 group-hover:w-full transition-all duration-700 ease-out" />
        </motion.div>
    );
};

export default StatCard;
