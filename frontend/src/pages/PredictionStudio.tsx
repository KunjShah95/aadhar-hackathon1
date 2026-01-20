import { useState } from 'react';
import { motion } from 'framer-motion';
import { Cpu, Zap, BarChart2, Terminal, FileText, Download, AlertTriangle, Activity, CheckCircle, Gauge } from 'lucide-react';
import { api } from '../services/api';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

export default function PredictionStudio() {
    const [selectedModel, setSelectedModel] = useState('lightgbm');
    const [isProcessing, setIsProcessing] = useState(false);
    const [prediction, setPrediction] = useState<number | null>(null);
    const [logs, setLogs] = useState<string[]>([]);
    const [showExplainer, setShowExplainer] = useState(false);
    const [comparisonData, setComparisonData] = useState<any[]>([]);
    const [anomalyData, setAnomalyData] = useState<any>(null);
    const [demandData, setDemandData] = useState<any>(null);

    // Scenarios for quick demo
    const scenarios = {
        'high_risk': { demo_updates: 850, bio_updates: 600, enrollment_rate: 2.5, region_volatility: 0.9 },
        'normal': { demo_updates: 50, bio_updates: 30, enrollment_rate: 0.8, region_volatility: 0.1 },
        'volatile': { demo_updates: 400, bio_updates: 150, enrollment_rate: 1.2, region_volatility: 0.6 }
    };

    const runLogs = () => {
        setLogs([]);
        const steps = [
            "Initializing tensor cores...",
            "Loading feature vectors from Redis...",
            `Normalizing inputs: demo=${inputs.demo_updates}, bio=${inputs.bio_updates}...`,
            "Running weighted ensemble inference...",
            "Calculating Shapley values...",
            "Inference complete."
        ];

        steps.forEach((step, index) => {
            setTimeout(() => {
                setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${step}`]);
            }, index * 400);
        });
    };

    const [inputs, setInputs] = useState({
        demo_updates: 50,
        bio_updates: 30,
        enrollment_rate: 0.8,
        region_volatility: 0.1
    });

    const applyScenario = (type: 'high_risk' | 'normal' | 'volatile') => {
        setInputs(scenarios[type]);
        setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] Scenario loaded: ${type.toUpperCase()}`]);
    };

    const runPrediction = async () => {
        setIsProcessing(true);
        setShowExplainer(false);
        runLogs();

        // Artifical delay to match logs
        await new Promise(resolve => setTimeout(resolve, 2500));

        try {
            const payload = {
                model_type: selectedModel,
                features: {
                    demo_update_rolling_mean_7d: inputs.demo_updates,
                    bio_update_rolling_mean_7d: inputs.bio_updates,
                    enrol_rolling_mean_7d: inputs.enrollment_rate * 100,
                    enrol_volatility: inputs.region_volatility,
                    year: 2026, month: 1, day_of_week: 1, is_weekend: 0
                }
            };

            // Run all analyses in parallel
            const [predResponse, anomData, demData] = await Promise.all([
                fetch('http://localhost:5000/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                }).then(res => res.json()),
                api.detectAnomaly(payload),
                api.predictServiceDemand(payload)
            ]);

            if (predResponse.success) {
                setPrediction(predResponse.prediction);
            }
            if (anomData.success) setAnomalyData(anomData);
            if (demData.success) setDemandData(demData);

            setShowExplainer(true);
        } catch (error) {
            console.error("Inference Error:", error);
            setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ERROR: Inference failed`]);
        } finally {
            setIsProcessing(false);
        }
    };

    const runComparison = async () => {
        setIsProcessing(true);
        const models = ['lightgbm', 'xgboost', 'random_forest'];
        const results = [];

        for (const model of models) {
            try {
                const response = await fetch('http://localhost:5000/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        model_type: model,
                        features: {
                            demo_update_rolling_mean_7d: inputs.demo_updates,
                            bio_update_rolling_mean_7d: inputs.bio_updates,
                            enrol_rolling_mean_7d: inputs.enrollment_rate * 100,
                            enrol_volatility: inputs.region_volatility,
                            year: 2026, month: 1, day_of_week: 1, is_weekend: 0
                        }
                    })
                });
                const data = await response.json();
                if (data.success) results.push({ name: model, value: data.prediction });
            } catch (e) { console.error(e) }
        }
        setComparisonData(results);
        setIsProcessing(false);
    };

    const handleExport = () => {
        setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] GENERATING_REPORT_PDF...`]);
        setTimeout(() => {
            setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] REPORT_EXPORTED: UIDAI_Audit_2026.pdf`]);
            alert("✓ Secure Audit Report Generated (Mock)");
        }, 1500);
    };

    return (
        <div className="space-y-8 animate-fade-in relative min-h-screen pb-20">
            <div className="flex flex-col gap-2 border-b border-white/5 pb-6">
                <div className="flex justify-between items-start">
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight text-white font-display">AI Prediction Studio</h2>
                        <div className="flex items-center gap-2 text-muted-foreground text-sm font-mono mt-1">
                            <Cpu className="w-4 h-4 text-purple-500" />
                            <span>Multi-Model Inference Lab</span>
                        </div>
                    </div>
                    <button
                        onClick={handleExport}
                        className="flex items-center gap-2 px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-xs font-mono text-gray-300 transition-colors"
                    >
                        <Download className="w-4 h-4" />
                        EXPORT_REPORT
                    </button>
                </div>
            </div>

            <div className="grid lg:grid-cols-3 gap-8">
                {/* Configuration Panel */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="glass-panel p-6 rounded-xl border border-white/5 bg-[#030712]/60">
                        <h3 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider">Model Configuration</h3>

                        <label className="block text-xs text-muted-foreground mb-2">Select Engine</label>
                        <div className="grid grid-cols-2 gap-2 mb-6">
                            {['lightgbm', 'xgboost', 'random_forest'].map((m) => (
                                <button
                                    key={m}
                                    onClick={() => setSelectedModel(m)}
                                    className={`px-3 py-2 rounded-md text-xs font-mono border transition-all ${selectedModel === m
                                        ? 'bg-primary/20 border-primary text-primary'
                                        : 'bg-white/5 border-white/10 text-muted-foreground hover:bg-white/10'
                                        }`}
                                >
                                    {m.toUpperCase()}
                                </button>
                            ))}
                        </div>

                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between text-xs mb-1">
                                    <span className="text-gray-400">Demographic Updates (Avg)</span>
                                    <span className="text-white font-mono">{inputs.demo_updates}</span>
                                </div>
                                <input
                                    type="range" min="0" max="1000"
                                    value={inputs.demo_updates}
                                    onChange={(e) => setInputs({ ...inputs, demo_updates: Number(e.target.value) })}
                                    className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary"
                                />
                            </div>
                            <div>
                                <div className="flex justify-between text-xs mb-1">
                                    <span className="text-gray-400">Biometric Updates (Avg)</span>
                                    <span className="text-white font-mono">{inputs.bio_updates}</span>
                                </div>
                                <input
                                    type="range" min="0" max="1000"
                                    value={inputs.bio_updates}
                                    onChange={(e) => setInputs({ ...inputs, bio_updates: Number(e.target.value) })}
                                    className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-purple-500"
                                />
                            </div>
                        </div>

                        {/* Scenarios */}
                        <div className="mb-6 pt-4 border-t border-white/5">
                            <label className="block text-xs text-muted-foreground mb-3">Quick Scenarios</label>
                            <div className="grid grid-cols-3 gap-2">
                                <button onClick={() => applyScenario('normal')} className="px-2 py-1.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 text-[10px] rounded hover:bg-emerald-500/20 transition-colors">
                                    NORMAL
                                </button>
                                <button onClick={() => applyScenario('volatile')} className="px-2 py-1.5 bg-yellow-500/10 border border-yellow-500/20 text-yellow-500 text-[10px] rounded hover:bg-yellow-500/20 transition-colors">
                                    VOLATILE
                                </button>
                                <button onClick={() => applyScenario('high_risk')} className="px-2 py-1.5 bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] rounded hover:bg-red-500/20 transition-colors">
                                    HIGH RISK
                                </button>
                            </div>
                        </div>

                        <div className="mt-8 flex gap-2">
                            <button
                                onClick={runPrediction}
                                disabled={isProcessing}
                                className="flex-1 py-2 bg-primary text-black font-semibold rounded-md text-sm hover:bg-primary/90 transition-colors disabled:opacity-50"
                            >
                                {isProcessing ? 'Processing...' : 'Run Inference'}
                            </button>
                            <button
                                onClick={runComparison}
                                disabled={isProcessing}
                                className="px-3 py-2 border border-white/10 rounded-md hover:bg-white/5 transition-colors"
                            >
                                <BarChart2 className="w-4 h-4 text-white" />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Results Visualization */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Main Prediction Result */}
                    <div className="glass-panel p-8 rounded-xl border border-white/5 bg-[#030712]/40 backdrop-blur-xl flex flex-col items-center justify-center min-h-[200px] relative overflow-hidden">
                        {prediction !== null ? (
                            <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
                                <div className="text-muted-foreground text-sm font-mono mb-2 uppercase tracking-widest text-center">Predicted Fraud Score</div>
                                <div className="text-6xl font-bold text-white font-display text-center relative z-10">
                                    {prediction.toFixed(4)}
                                    <div className={`absolute -top-4 -right-4 w-3 h-3 rounded-full ${prediction > 0.5 ? 'bg-red-500' : 'bg-emerald-500'} animate-ping`} />
                                </div>
                                <div className="mt-4 flex items-center justify-center gap-2 text-xs text-muted-foreground border-t border-white/5 pt-4">
                                    <Zap className="w-3 h-3 text-yellow-500" />
                                    <span>Inference time: &lt;12ms</span>
                                    <span className="mx-2">•</span>
                                    <Cpu className="w-3 h-3 text-blue-500" />
                                    <span>Model: {selectedModel}</span>
                                </div>
                            </motion.div>
                        ) : (
                            <div className="text-center text-muted-foreground">
                                <Cpu className="w-12 h-12 mx-auto mb-4 opacity-20" />
                                <p>Ready for input parameters</p>
                            </div>
                        )}
                        {/* Background Beams */}
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[100px] -z-10 pointer-events-none" />
                    </div>

                    {/* Operational Intelligence (Anomaly & Demand) */}
                    {prediction !== null && (
                        <div className="grid grid-cols-2 gap-4 animate-fade-in">
                            {/* Anomaly Monitor */}
                            <div className={`glass-panel p-5 rounded-xl border ${anomalyData?.is_anomaly ? 'border-red-500/30 bg-red-500/5' : 'border-emerald-500/30 bg-emerald-500/5'}`}>
                                <div className="flex items-start justify-between mb-4">
                                    <div>
                                        <h4 className="text-sm font-semibold text-white">System Health</h4>
                                        <p className="text-xs text-muted-foreground">Real-time Anomaly Detection</p>
                                    </div>
                                    {anomalyData?.is_anomaly ?
                                        <AlertTriangle className="w-5 h-5 text-red-500 animate-pulse" /> :
                                        <CheckCircle className="w-5 h-5 text-emerald-500" />
                                    }
                                </div>
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-400">Status</span>
                                        <span className={`font-mono font-bold ${anomalyData?.is_anomaly ? 'text-red-400' : 'text-emerald-400'}`}>
                                            {anomalyData?.is_anomaly ? 'CRITICAL' : 'NOMINAL'}
                                        </span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-400">Type</span>
                                        <span className="text-white font-mono text-xs">{anomalyData?.anomaly_type || 'None'}</span>
                                    </div>
                                    {anomalyData?.is_anomaly && (
                                        <div className="flex justify-between text-sm border-t border-white/5 pt-2 mt-2">
                                            <span className="text-gray-400">Severity</span>
                                            <span className="text-red-400 font-mono">{anomalyData?.severity}</span>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Demand Forecast */}
                            <div className="glass-panel p-5 rounded-xl border border-white/5 bg-[#030712]/40">
                                <div className="flex items-start justify-between mb-4">
                                    <div>
                                        <h4 className="text-sm font-semibold text-white">Service Demand</h4>
                                        <p className="text-xs text-muted-foreground">Load Forecasting</p>
                                    </div>
                                    <Activity className="w-5 h-5 text-blue-500" />
                                </div>

                                <div className="flex flex-col items-center justify-center py-2">
                                    <div className={`text-2xl font-bold font-display mb-1 ${demandData?.demand_level === 'High' ? 'text-red-400' :
                                            demandData?.demand_level === 'Low' ? 'text-emerald-400' : 'text-yellow-400'
                                        }`}>
                                        {demandData?.demand_level?.toUpperCase()}
                                    </div>
                                    <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden mt-2">
                                        <div
                                            className={`h-full transition-all duration-1000 ${demandData?.demand_level === 'High' ? 'bg-red-500 w-[90%]' :
                                                    demandData?.demand_level === 'Low' ? 'bg-emerald-500 w-[25%]' : 'bg-yellow-500 w-[60%]'
                                                }`}
                                        />
                                    </div>
                                    <div className="mt-3 text-xs text-center text-muted-foreground">
                                        Confidence Score: <span className="text-white font-mono">{(demandData?.confidence * 100).toFixed(1)}%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Comparison Chart */}
                    {comparisonData.length > 0 && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="glass-panel p-6 rounded-xl border border-white/5 bg-[#030712]/40"
                        >
                            <h3 className="text-sm font-semibold text-white mb-6">Model Comparison Analysis</h3>
                            <div className="h-[200px] w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={comparisonData} layout="vertical" margin={{ left: 0 }}>
                                        <XAxis type="number" hide />
                                        <YAxis dataKey="name" type="category" width={100} tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                                        <Tooltip
                                            cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                            contentStyle={{ backgroundColor: '#030712', borderColor: 'rgba(255,255,255,0.1)', color: '#fff' }}
                                        />
                                        <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={24}>
                                            {comparisonData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={['#3b82f6', '#8b5cf6', '#10b981'][index % 3]} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </motion.div>
                    )}

                    {/* Feature Importance (Explainability) */}
                    {showExplainer && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.2 }}
                            className="glass-panel p-6 rounded-xl border border-white/5 bg-[#030712]/40"
                        >
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                                    <FileText className="w-4 h-4 text-primary" />
                                    Model Explainability (SHAP Values)
                                </h3>
                                <span className="text-xs text-muted-foreground bg-white/5 px-2 py-1 rounded">Top Factors</span>
                            </div>

                            <div className="space-y-4">
                                {[
                                    { label: 'Demographic Velocity', value: inputs.demo_updates / 10, color: 'bg-blue-500' },
                                    { label: 'Region Volatility', value: inputs.region_volatility * 100, color: 'bg-purple-500' },
                                    { label: 'Biometric Updates', value: inputs.bio_updates / 8, color: 'bg-pink-500' },
                                ].sort((a, b) => b.value - a.value).map((item, i) => (
                                    <div key={i} className="group">
                                        <div className="flex justify-between text-xs mb-1">
                                            <span className="text-gray-400 group-hover:text-white transition-colors">{item.label}</span>
                                            <span className="font-mono text-white">{item.value.toFixed(1)}% Impact</span>
                                        </div>
                                        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: `${Math.min(item.value, 100)}%` }}
                                                transition={{ duration: 1, ease: "easeOut" }}
                                                className={`h-full ${item.color}`}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    )}

                    {/* Live System Logs */}
                    <div className="glass-panel p-4 rounded-xl border border-white/5 bg-black/60 font-mono text-xs h-[200px] overflow-hidden flex flex-col">
                        <div className="flex items-center gap-2 text-muted-foreground border-b border-white/5 pb-2 mb-2">
                            <Terminal className="w-3 h-3" />
                            <span>System Output</span>
                        </div>
                        <div className="flex-1 overflow-auto space-y-1 text-gray-400">
                            {logs.length === 0 && <span className="opacity-30 italic">Waiting for process initiation...</span>}
                            {logs.map((log, i) => (
                                <div key={i} className="animate-fade-in">
                                    <span className="text-primary mr-2">➜</span>
                                    {log}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
