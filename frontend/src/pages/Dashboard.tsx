import { useDashboardData } from '../hooks/useDashboardData';
import { StatCard } from '../components/ui/stat-card';
import { AlertTriangle, CheckCircle, RefreshCcw, ShieldCheck } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="glass-panel p-3 rounded-lg border border-white/10 shadow-xl">
                <p className="text-xs font-mono text-muted-foreground mb-1">{label}</p>
                <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                    <span className="text-sm font-bold text-white">
                        {payload[0].value.toLocaleString()}
                    </span>
                </div>
            </div>
        );
    }
    return null;
};

export default function Dashboard() {
    const { data, status } = useDashboardData();

    if (status === 'loading') {
        return (
            <div className="flex h-[60vh] items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="relative">
                        <div className="w-12 h-12 rounded-full border-t-2 border-r-2 border-primary animate-spin" />
                        <div className="absolute inset-0 w-12 h-12 rounded-full border-2 border-primary/20" />
                    </div>
                    <span className="text-xs font-mono text-primary animate-pulse tracking-[0.2em]">INITIALIZING CORE SYSTEMS...</span>
                </div>
            </div>
        );
    }

    if (!data) return null;

    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1,
                delayChildren: 0.2
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0, transition: { duration: 0.4 } }
    };

    return (
        <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className="space-y-8"
        >
            {/* Page Header */}
            <motion.div variants={itemVariants} className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-6">
                <div>
                    <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-white font-display">
                        Command Center
                    </h1>
                    <p className="text-muted-foreground mt-2 max-w-2xl text-sm leading-relaxed">
                        Real-time telemetry and biometric stream analysis from the UIDAI ecosystem network.
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-medium text-emerald-400">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        <span>Connected to Secure Grid</span>
                    </div>
                    <button className="p-2 text-muted-foreground hover:text-white hover:bg-white/5 rounded-lg transition-colors">
                        <RefreshCcw className="w-4 h-4" />
                    </button>
                </div>
            </motion.div>

            {/* KPI Grid */}
            <motion.div variants={itemVariants} className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                {data.kpis.map(kpi => (
                    <StatCard key={kpi.id} kpi={kpi} />
                ))}
            </motion.div>

            {/* Main Content Grid */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">

                {/* Chart Section */}
                <motion.div variants={itemVariants} className="col-span-4 rounded-2xl border border-white/5 bg-[#030712]/40 backdrop-blur-xl p-6 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-6 opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <span className="w-2 h-2 rounded-full bg-primary" />
                            Live Stream
                        </div>
                    </div>

                    <div className="mb-6">
                        <h3 className="font-semibold text-lg tracking-tight text-white mb-1">Response Latency</h3>
                        <p className="text-xs text-muted-foreground font-mono uppercase tracking-wider">Average transaction time (ms)</p>
                    </div>

                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data.trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                <XAxis
                                    dataKey="date"
                                    stroke="#475569"
                                    fontSize={10}
                                    tickLine={false}
                                    axisLine={false}
                                    tickFormatter={(val) => val.split('-')[2]} // Just day
                                />
                                <YAxis
                                    stroke="#475569"
                                    fontSize={10}
                                    tickLine={false}
                                    axisLine={false}
                                    tickFormatter={(val) => `${val / 1000}k`}
                                />
                                <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#0ea5e9', strokeWidth: 1, strokeDasharray: '4 4' }} />
                                <Area
                                    type="monotone"
                                    dataKey="value"
                                    stroke="#0ea5e9"
                                    strokeWidth={2}
                                    fillOpacity={1}
                                    fill="url(#colorValue)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>

                {/* Anomalies Panel */}
                <motion.div variants={itemVariants} className="col-span-3 rounded-2xl border border-white/5 bg-[#030712]/40 backdrop-blur-xl p-6 flex flex-col">
                    <div className="mb-6 flex items-center justify-between">
                        <div>
                            <h3 className="font-semibold text-lg tracking-tight text-white mb-1">System Anomalies</h3>
                            <p className="text-xs text-muted-foreground font-mono uppercase tracking-wider">AI-Detected Irregularities</p>
                        </div>
                        <span className="text-xs px-2 py-0.5 rounded bg-white/5 text-muted-foreground border border-white/5">{data.anomalies.length} Active</span>
                    </div>

                    <div className="space-y-3 flex-1 overflow-y-auto pr-2 custom-scrollbar">
                        <AnimatePresence>
                            {data.anomalies.map(anomaly => (
                                <motion.div
                                    key={anomaly.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className={`relative p-4 rounded-lg border transition-all hover:bg-white/5 group ${anomaly.severity === 'high' ? 'border-red-500/20 bg-red-500/5' :
                                        anomaly.severity === 'medium' ? 'border-amber-500/20 bg-amber-500/5' :
                                            'border-white/5 bg-white/5'
                                        }`}
                                >
                                    <div className="flex items-start gap-3">
                                        <div className={`mt-0.5 p-1 rounded-full ${anomaly.severity === 'high' ? 'bg-red-500/10 text-red-500' :
                                            anomaly.severity === 'medium' ? 'bg-amber-500/10 text-amber-500' :
                                                'bg-blue-500/10 text-blue-500'
                                            }`}>
                                            <AlertTriangle className="w-4 h-4" />
                                        </div>
                                        <div className="flex-1 space-y-1">
                                            <div className="flex items-center justify-between">
                                                <p className="text-sm font-medium text-white">{anomaly.metric}</p>
                                                <span className="text-[10px] text-muted-foreground opacity-60 group-hover:opacity-100 transition-opacity">
                                                    {new Date(anomaly.detectedAt).toLocaleTimeString()}
                                                </span>
                                            </div>
                                            <p className="text-xs text-muted-foreground leading-relaxed">
                                                {anomaly.description}
                                            </p>
                                            <div className="pt-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity translate-y-2 group-hover:translate-y-0 duration-300">
                                                <button className="text-[10px] bg-primary/20 hover:bg-primary/30 text-primary px-3 py-1 rounded-md transition-colors">
                                                    Investigate
                                                </button>
                                                <button className="text-[10px] hover:text-white text-muted-foreground px-2 py-1">
                                                    Dismiss
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>

                        {data.anomalies.length === 0 && (
                            <div className="flex flex-col items-center justify-center h-48 text-muted-foreground/40 space-y-3">
                                <CheckCircle className="h-10 w-10 text-emerald-500/20" />
                                <p className="text-sm">All systems nominal</p>
                            </div>
                        )}
                    </div>
                </motion.div>
            </div>
        </motion.div>
    );
}
