import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import { useDashboardData } from '../../hooks/useDashboardData';

export function PhoneMockup() {
    const { data } = useDashboardData();
    const containerRef = useRef<HTMLDivElement>(null);
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start end", "end start"]
    });

    const rotateX = useTransform(scrollYProgress, [0, 1], [30, 0]);
    const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1]);
    const y = useTransform(scrollYProgress, [0, 1], [100, -50]);

    return (
        <div ref={containerRef} className="perspective-[2000px] w-full flex justify-center py-20 overflow-hidden">
            <motion.div
                style={{ rotateX, scale, y }}
                className="relative w-[300px] md:w-[350px] aspect-[9/19] bg-black rounded-[40px] border-[8px] border-gray-900 shadow-2xl ring-1 ring-white/10"
                initial={{ opacity: 0, y: 100 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 1, ease: "easeOut" }}
            >
                {/* Screen Content */}
                <div className="absolute inset-0 bg-gradient-to-b from-gray-900 to-black rounded-[32px] overflow-hidden flex flex-col">
                    {/* Status Bar */}
                    <div className="h-8 w-full flex justify-between items-center px-6 pt-2">
                        <span className="text-[10px] text-white/80 font-mono">9:41</span>
                        <div className="flex gap-1.5">
                            <div className="w-4 h-2.5 bg-white/20 rounded-[1px]" />
                            <div className="w-4 h-2.5 bg-white/20 rounded-[1px]" />
                            <div className="w-4.5 h-2.5 bg-white/80 rounded-[1px]" />
                        </div>
                    </div>

                    {/* App Header */}
                    <div className="mt-4 px-6 flex justify-between items-center">
                        <div className="flex gap-2">
                            <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-xs text-white">JS</div>
                        </div>
                        <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center">+</div>
                    </div>

                    {/* Main Content (Chart) */}
                    <div className="mt-6 px-6">
                        <div className="text-xs text-secondary-foreground/60 uppercase tracking-wider font-medium">Total Enrolments</div>
                        <div className="text-3xl font-serif text-white mt-1">
                            {data ? (data.kpis[0].value as number).toLocaleString(undefined, { maximumFractionDigits: 0 }) : '1,350M'}
                            <span className="text-sm text-green-400 font-sans ml-2">
                                +{data ? data.kpis[0].delta : '0.8'}%
                            </span>
                        </div>

                        {/* Real-time Chart */}
                        <div className="mt-8 h-32 w-full flex items-end gap-1">
                            {data?.trends.slice(-14).map((t, i) => (
                                <motion.div
                                    key={i}
                                    className="flex-1 bg-gradient-to-t from-blue-500/20 to-blue-500/80 rounded-t-sm"
                                    initial={{ height: 0 }}
                                    animate={{ height: `${(t.value / 150) * 100}%` }}
                                    transition={{ duration: 0.5 }}
                                />
                            )) || [40, 60, 45, 70, 65, 85, 80, 95, 90, 100, 95, 110, 105, 120].map((h, i) => (
                                <div key={i} className="flex-1 bg-white/5 h-full rounded-t-sm animate-pulse" style={{ height: `${h}%`, opacity: 0.2 }} />
                            ))}
                        </div>
                    </div>

                    {/* Cards */}
                    <div className="mt-6 px-4 flex flex-col gap-3">
                        <div className="h-16 w-full bg-white/5 rounded-xl border border-white/5 p-3 flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" /></svg>
                            </div>
                            <div>
                                <div className="text-sm text-white">Weekly Recap</div>
                                <div className="text-xs text-gray-400">July 1-7</div>
                            </div>
                        </div>
                    </div>

                    {/* Bottom Nav */}
                    <div className="mt-auto h-20 bg-white/5 backdrop-blur-md flex justify-around items-center px-4 border-t border-white/5">
                        <div className="w-12 flex flex-col items-center gap-1 active:scale-95 transition-transform cursor-pointer">
                            <div className="w-5 h-5 rounded-full bg-white/20" />
                        </div>
                        <div className="w-12 flex flex-col items-center gap-1 active:scale-95 transition-transform cursor-pointer">
                            <div className="w-5 h-5 rounded-full border border-white/20" />
                        </div>
                        <div className="w-12 flex flex-col items-center gap-1 active:scale-95 transition-transform cursor-pointer">
                            <div className="w-5 h-5 rounded-full border border-white/20" />
                        </div>
                    </div>
                </div>

                {/* Reflections */}
                <div className="absolute inset-0 rounded-[30px] pointer-events-none bg-gradient-to-tr from-white/10 to-transparent opacity-50 z-20" />
                <div className="absolute -inset-1 rounded-[42px] bg-gradient-to-b from-gray-800 to-black -z-10" />
            </motion.div>

            {/* Reflection on floor */}
            {/* <div className="absolute bottom-0 w-[300px] h-10 bg-black/20 blur-xl translate-y-20 scale-x-150 rounded-full" /> */}
        </div>
    )
}
