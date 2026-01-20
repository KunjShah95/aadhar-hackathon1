import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ZoomIn, ZoomOut, Crosshair,
    Shield, Activity,
    Search, Wifi
} from 'lucide-react';

// Enhanced types for our threat map
interface Node {
    id: string;
    x: number;
    y: number;
    label: string;
    status: 'secure' | 'warning' | 'critical';
    threatScore: number;
    activeUsers: number;
    anomalies: number;
}

const INITIAL_NODES: Node[] = [
    { id: 'DEL', x: 280, y: 150, label: 'Delhi Prime', status: 'secure', threatScore: 12, activeUsers: 45200, anomalies: 2 },
    { id: 'MUM', x: 180, y: 320, label: 'Mumbai Hub', status: 'critical', threatScore: 89, activeUsers: 67100, anomalies: 145 },
    { id: 'BLR', x: 240, y: 440, label: 'Bangalore Net', status: 'warning', threatScore: 45, activeUsers: 32400, anomalies: 12 },
    { id: 'HYD', x: 280, y: 380, label: 'Hyderabad Grid', status: 'secure', threatScore: 8, activeUsers: 28900, anomalies: 0 },
    { id: 'CHE', x: 300, y: 460, label: 'Chennai Link', status: 'secure', threatScore: 5, activeUsers: 21000, anomalies: 1 },
    { id: 'KOL', x: 450, y: 240, label: 'Kolkata Zone', status: 'warning', threatScore: 62, activeUsers: 19500, anomalies: 34 },
];

export default function LiveMap() {
    const [nodes, setNodes] = useState<Node[]>(INITIAL_NODES);
    const [selectedNode, setSelectedNode] = useState<Node | null>(null);
    const [radarAngle, setRadarAngle] = useState(0);

    // Simulate live data updates
    useEffect(() => {
        const interval = setInterval(() => {
            setNodes(prev => prev.map(node => {
                // Randomly fluctuate threat scores
                const change = Math.floor(Math.random() * 10) - 4; // -4 to +5
                const newScore = Math.max(0, Math.min(100, node.threatScore + change));

                let status: Node['status'] = 'secure';
                if (newScore > 75) status = 'critical';
                else if (newScore > 40) status = 'warning';

                return {
                    ...node,
                    threatScore: newScore,
                    status,
                    activeUsers: node.activeUsers + Math.floor(Math.random() * 20) - 10,
                    anomalies: status === 'critical' ? node.anomalies + 1 : node.anomalies
                };
            }));
        }, 2000);

        // Radar rotation loop
        const radarLoop = setInterval(() => {
            setRadarAngle(prev => (prev + 2) % 360);
        }, 50);

        return () => {
            clearInterval(interval);
            clearInterval(radarLoop);
        };
    }, []);

    const getStatusColor = (status: Node['status']) => {
        switch (status) {
            case 'critical': return '#ef4444'; // Red-500
            case 'warning': return '#f59e0b'; // Amber-500
            case 'secure': return '#3b82f6'; // Blue-500
        }
    };

    return (
        <div className="space-y-6 animate-fade-in h-[calc(100vh-100px)] flex flex-col relative overflow-hidden">
            {/* Header / Stats Bar */}
            <div className="flex flex-col gap-4 border-b border-white/5 pb-4 z-10 shrink-0">
                <div className="flex justify-between items-end">
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight text-white font-display flex items-center gap-3">
                            Geospatial Threat Intel
                            <span className="text-xs px-2 py-1 bg-red-500/10 text-red-500 border border-red-500/20 rounded font-mono">LIVE FEED</span>
                        </h2>
                        <div className="flex items-center gap-2 text-muted-foreground text-sm font-mono mt-1">
                            <Activity className="w-4 h-4 text-emerald-500 animate-pulse" />
                            <span>Monitoring 1.4B Identity Nodes</span>
                        </div>
                    </div>

                    {/* Quick Stats Ticker */}
                    <div className="flex gap-6 text-right font-mono text-xs">
                        <div>
                            <div className="text-gray-500">GLOBAL_THREAT_INDEX</div>
                            <div className="text-xl font-bold text-white">
                                {(nodes.reduce((acc, n) => acc + n.threatScore, 0) / nodes.length).toFixed(1)}%
                            </div>
                        </div>
                        <div>
                            <div className="text-gray-500">ACTIVE_ANOMALIES</div>
                            <div className="text-xl font-bold text-red-500 animate-pulse">
                                {nodes.reduce((acc, n) => acc + n.anomalies, 0)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Map Interaction Layer */}
            <div className="flex-1 glass-panel rounded-2xl border border-white/5 bg-[#030712]/80 relative overflow-hidden group">

                {/* HUD Controls */}
                <div className="absolute top-4 right-4 z-20 flex flex-col gap-2 bg-black/40 backdrop-blur-md p-2 rounded-lg border border-white/10">
                    <button className="p-2 hover:bg-white/10 rounded text-white transition-colors"><ZoomIn className="w-4 h-4" /></button>
                    <button className="p-2 hover:bg-white/10 rounded text-white transition-colors"><ZoomOut className="w-4 h-4" /></button>
                    <button className="p-2 hover:bg-white/10 rounded text-white transition-colors"><Crosshair className="w-4 h-4" /></button>
                    <div className="h-px bg-white/10 my-1" />
                    <button className="p-2 hover:bg-white/10 rounded text-white transition-colors"><Wifi className="w-4 h-4" /></button>
                </div>

                {/* Grid & Map Background */}
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f2937_1px,transparent_1px),linear-gradient(to_bottom,#1f2937_1px,transparent_1px)] bg-[size:40px_40px] opacity-10 pointer-events-none" />

                {/* Central Map Visualization */}
                <div className="absolute inset-0 flex items-center justify-center">
                    {/* Rotating Radar Rings */}
                    <div className="relative w-[700px] h-[700px] rounded-full border border-blue-500/5 animate-spin-slow-reverse opacity-20" />
                    <div className="absolute w-[500px] h-[500px] rounded-full border border-blue-500/10" />

                    {/* Scanning Line */}
                    <div
                        className="absolute w-[700px] h-[700px] rounded-full pointer-events-none"
                        style={{ background: `conic - gradient(from ${radarAngle}deg, transparent 60 %, rgba(59, 130, 246, 0.1) 90 %, rgba(59, 130, 246, 0.3) 100 %)` }}
                    />

                    {/* SVG Map Layer */}
                    <svg viewBox="0 0 600 600" className="w-[600px] h-[600px] z-10">
                        {/* Network Connections */}
                        <motion.path
                            d="M280,150 L180,320 L240,440 L300,460 M280,150 L450,240 L280,380 M180,320 L280,380"
                            fill="none"
                            stroke="#3b82f6"
                            strokeWidth="1"
                            strokeOpacity="0.1"
                            initial={{ pathLength: 0 }}
                            animate={{ pathLength: 1 }}
                            transition={{ duration: 2 }}
                        />

                        {/* City Nodes */}
                        {nodes.map((node) => {
                            const color = getStatusColor(node.status);
                            return (
                                <g
                                    key={node.id}
                                    onClick={() => setSelectedNode(node)}
                                    className="cursor-pointer hover:opacity-80 transition-opacity"
                                >
                                    {/* Pulse Effect for Critical/Warning */}
                                    {node.status !== 'secure' && (
                                        <circle
                                            cx={node.x} cy={node.y} r="20"
                                            fill={color} opacity="0.2"
                                            className="animate-ping"
                                        />
                                    )}

                                    {/* Outer Ring */}
                                    <circle
                                        cx={node.x} cy={node.y} r="6"
                                        stroke={color} strokeWidth="2"
                                        fill="#000"
                                    />

                                    {/* Inner Dot */}
                                    <circle cx={node.x} cy={node.y} r="3" fill={color} />

                                    {/* Label */}
                                    <text
                                        x={node.x + 15} y={node.y + 4}
                                        fill="white" fontSize="10" fontFamily="monospace"
                                        className="font-bold opacity-70"
                                    >
                                        {node.id}
                                    </text>
                                </g>
                            );
                        })}
                    </svg>
                </div>

                {/* Selected Sector Analysis Panel */}
                <AnimatePresence>
                    {selectedNode && (
                        <motion.div
                            initial={{ x: 400, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            exit={{ x: 400, opacity: 0 }}
                            className="absolute right-0 top-0 bottom-0 w-80 bg-[#030712]/95 border-l border-white/10 backdrop-blur-xl p-6 z-30 shadow-2xl"
                        >
                            <div className="flex justify-between items-start mb-8">
                                <div>
                                    <h3 className="text-2xl font-bold text-white font-display">{selectedNode.label}</h3>
                                    <span className="text-xs text-muted-foreground font-mono">SECTOR_ID: {selectedNode.id}-X99</span>
                                </div>
                                <button onClick={() => setSelectedNode(null)} className="text-gray-500 hover:text-white">✕</button>
                            </div>

                            <div className="space-y-6">
                                {/* Threat Gauge */}
                                <div className="p-4 rounded-lg bg-white/5 border border-white/10">
                                    <div className="flex justify-between mb-2">
                                        <span className="text-xs text-gray-400 uppercase">Threat Level</span>
                                        <span
                                            className="text-xs font-bold px-2 py-0.5 rounded"
                                            style={{ backgroundColor: `${getStatusColor(selectedNode.status)} 20`, color: getStatusColor(selectedNode.status) }}
                                        >
                                            {selectedNode.status.toUpperCase()}
                                        </span>
                                    </div>
                                    <div className="text-4xl font-bold text-white mb-2">{selectedNode.threatScore}%</div>
                                    <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
                                        <div
                                            className="h-full transition-all duration-500"
                                            style={{ width: `${selectedNode.threatScore}% `, backgroundColor: getStatusColor(selectedNode.status) }}
                                        />
                                    </div>
                                </div>

                                {/* Metrics Grid */}
                                <div className="grid grid-cols-2 gap-3">
                                    <div className="p-3 bg-white/5 rounded border border-white/5">
                                        <div className="text-xs text-gray-400 mb-1">Users Active</div>
                                        <div className="text-lg font-mono text-white">{selectedNode.activeUsers.toLocaleString()}</div>
                                    </div>
                                    <div className="p-3 bg-white/5 rounded border border-white/5">
                                        <div className="text-xs text-gray-400 mb-1">Anomalies</div>
                                        <div className="text-lg font-mono text-red-500">{selectedNode.anomalies}</div>
                                    </div>
                                    <div className="p-3 bg-white/5 rounded border border-white/5">
                                        <div className="text-xs text-gray-400 mb-1">Latency</div>
                                        <div className="text-lg font-mono text-emerald-500">12ms</div>
                                    </div>
                                    <div className="p-3 bg-white/5 rounded border border-white/5">
                                        <div className="text-xs text-gray-400 mb-1">Encryption</div>
                                        <div className="text-lg font-mono text-blue-500">AES-256</div>
                                    </div>
                                </div>

                                {/* Action Buttons */}
                                <div className="space-y-2 mt-8">
                                    <button className="w-full py-2 bg-red-500/10 border border-red-500/20 text-red-500 hover:bg-red-500/20 rounded text-sm font-semibold transition-colors flex items-center justify-center gap-2">
                                        <Shield className="w-4 h-4" />
                                        Deploy Countermeasures
                                    </button>
                                    <button className="w-full py-2 bg-blue-500/10 border border-blue-500/20 text-blue-500 hover:bg-blue-500/20 rounded text-sm font-semibold transition-colors flex items-center justify-center gap-2">
                                        <Search className="w-4 h-4" />
                                        Deep Scan Sector
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}


