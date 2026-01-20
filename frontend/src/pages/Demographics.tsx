import { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import { Users, MapPin, TrendingUp, Activity } from 'lucide-react';
import { StatCard } from '../components/ui/stat-card';

const data = [
    { name: 'Jan', urban: 4000, rural: 2400 },
    { name: 'Feb', urban: 3000, rural: 1398 },
    { name: 'Mar', urban: 2000, rural: 9800 },
    { name: 'Apr', urban: 2780, rural: 3908 },
    { name: 'May', urban: 1890, rural: 4800 },
    { name: 'Jun', urban: 2390, rural: 3800 },
    { name: 'Jul', urban: 3490, rural: 4300 },
];

const ageData = [
    { name: '0-5', value: 1200 },
    { name: '5-18', value: 3400 },
    { name: '18-40', value: 8900 },
    { name: '40-60', value: 4500 },
    { name: '60+', value: 2100 },
];

export default function Demographics() {
    const containerRef = useRef(null);
    const { scrollYProgress } = useScroll({ target: containerRef });
    const y = useTransform(scrollYProgress, [0, 1], [0, -50]);

    return (
        <div ref={containerRef} className="space-y-8 animate-fade-in relative min-h-screen">
            <div className="flex flex-col gap-2 border-b border-white/5 pb-6">
                <h2 className="text-3xl font-bold tracking-tight text-white font-display">Demographic Intelligence</h2>
                <div className="flex items-center gap-2 text-muted-foreground text-sm font-mono">
                    <Users className="w-4 h-4 text-primary" />
                    <span>Population Distribution Analysis</span>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
                <StatCard kpi={{
                    id: '1', label: 'Total Population', value: 1428000000, trend: 'up', delta: 1.2, unit: '', confidence: 1, trendLabel: 'vs last year'
                }} />
                <StatCard kpi={{
                    id: '2', label: 'Rural Coverage', value: 890000000, trend: 'up', delta: 0.8, unit: '', confidence: 1
                }} />
                <StatCard kpi={{
                    id: '3', label: 'Urban Coverage', value: 538000000, trend: 'up', delta: 2.4, unit: '', confidence: 1
                }} />
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                <motion.div style={{ y }} className="col-span-2 glass-panel p-6 rounded-2xl border border-white/5 bg-[#030712]/40 backdrop-blur-xl relative overflow-hidden">
                    <div className="mb-6 flex justify-between items-end">
                        <div>
                            <h3 className="text-lg font-semibold text-white">Regional Distribution</h3>
                            <p className="text-xs text-muted-foreground font-mono mt-1">Urban vs Rural Enrollment Trends</p>
                        </div>
                        <div className="flex gap-2 text-xs">
                            <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-primary" />Urban</div>
                            <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-emerald-500" />Rural</div>
                        </div>
                    </div>
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorUrban" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorRural" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <XAxis dataKey="name" axisLine={false} tickLine={false} stroke="#475569" fontSize={12} />
                                <YAxis axisLine={false} tickLine={false} stroke="#475569" fontSize={12} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#030712', borderColor: 'rgba(255,255,255,0.1)' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Area type="monotone" dataKey="urban" stroke="#0ea5e9" strokeWidth={2} fillOpacity={1} fill="url(#colorUrban)" />
                                <Area type="monotone" dataKey="rural" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorRural)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>

                <div className="col-span-1 glass-panel p-6 rounded-2xl border border-white/5 bg-[#030712]/40 backdrop-blur-xl">
                    <h3 className="text-lg font-semibold text-white mb-6">Age Demographics</h3>
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={ageData} layout="vertical" margin={{ left: -20 }}>
                                <XAxis type="number" hide />
                                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} stroke="#94a3b8" fontSize={12} width={40} />
                                <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ backgroundColor: '#030712', borderColor: 'rgba(255,255,255,0.1)' }} />
                                <Bar dataKey="value" radius={[4, 4, 4, 4]} barSize={32}>
                                    {ageData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#3b82f6' : '#60a5fa'} fillOpacity={0.8} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Ambient decorative elements */}
            <div className="fixed bottom-0 right-0 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[128px] pointer-events-none -z-10" />
        </div>
    );
}
