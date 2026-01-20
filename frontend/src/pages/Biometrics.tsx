import { useState } from 'react';
import { motion } from 'framer-motion';
import { Fingerprint, ScanEye, ShieldCheck, AlertCircle, Terminal, Search } from 'lucide-react';


const BioScanner = () => {
    const [scanning, setScanning] = useState(false);
    const [result, setResult] = useState<'idle' | 'success' | 'failed'>('idle');

    const handleScan = () => {
        setScanning(true);
        setResult('idle');
        setTimeout(() => {
            setScanning(false);
            setResult(Math.random() > 0.2 ? 'success' : 'failed');
        }, 3000);
    };

    return (
        <div className="glass-panel p-8 rounded-xl border border-white/5 bg-[#030712]/80 flex flex-col items-center justify-center relative overflow-hidden min-h-[400px]">
            <h3 className="text-lg font-bold text-white mb-8 font-display">Identity Verification Sandbox</h3>

            <div className="relative w-48 h-48 mb-8 group cursor-pointer" onClick={handleScan}>
                {/* Fingerprint Glyph */}
                <Fingerprint className={`w-full h-full transition-colors duration-500 ${result === 'success' ? 'text-emerald-500' :
                    result === 'failed' ? 'text-red-500' :
                        scanning ? 'text-primary' : 'text-gray-700'
                    }`} strokeWidth={0.5} />

                {/* Scanning Beam */}
                {scanning && (
                    <motion.div
                        initial={{ top: '0%' }}
                        animate={{ top: '100%' }}
                        transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                        className="absolute left-0 right-0 h-2 bg-primary/50 blur-[4px] shadow-[0_0_20px_rgba(14,165,233,0.5)]"
                    />
                )}

                {/* Ripple Effect on Idle */}
                {!scanning && result === 'idle' && (
                    <div className="absolute inset-0 rounded-full animate-ping opacity-10 bg-primary" />
                )}
            </div>

            <div className="text-center space-y-2 relative z-10">
                {scanning && <div className="text-primary font-mono text-sm animate-pulse">ACQUIRING_BIOMETRICS...</div>}

                {result === 'success' && (
                    <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
                        <div className="text-emerald-500 font-bold text-xl flex items-center gap-2 justify-center">
                            <ShieldCheck className="w-6 h-6" />
                            IDENTITY VERIFIED
                        </div>
                        <div className="text-gray-500 text-xs font-mono mt-1">UID: 9xxx-xxxx-8821</div>
                    </motion.div>
                )}

                {result === 'failed' && (
                    <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
                        <div className="text-red-500 font-bold text-xl flex items-center gap-2 justify-center">
                            <AlertCircle className="w-6 h-6" />
                            MATCH NOT FOUND
                        </div>
                        <div className="text-gray-500 text-xs font-mono mt-1">ERROR_CODE: BIO_MISMATCH_04</div>
                    </motion.div>
                )}

                {result === 'idle' && !scanning && (
                    <button
                        onClick={handleScan}
                        className="px-6 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-gray-300 transition-all font-mono hover:border-primary/50 hover:text-primary"
                    >
                        INITIATE_SCAN_SEQUENCE
                    </button>
                )}
            </div>

            {/* Background Grid */}
            <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] [mask-image:radial-gradient(ellipse_50%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-20 pointer-events-none" />
        </div>
    );
};

export default function Biometrics() {
    return (
        <div className="space-y-8 animate-fade-in relative min-h-screen">
            <div className="flex flex-col gap-2 border-b border-white/5 pb-6">
                <h2 className="text-3xl font-bold tracking-tight text-white font-display">Biometric Surveillance</h2>
                <div className="flex items-center gap-2 text-muted-foreground text-sm font-mono">
                    <Fingerprint className="w-4 h-4 text-emerald-500" />
                    <span>Live Authentication Stream</span>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-4">
                <div className="glass-panel p-6 rounded-xl border border-white/5 bg-[#030712]/60 flex items-center justify-between">
                    <div>
                        <p className="text-xs text-muted-foreground font-mono uppercase">Auth Rate</p>
                        <h3 className="text-2xl font-bold text-white mt-1">98.2%</h3>
                    </div>
                    <div className="p-3 rounded-full bg-emerald-500/10 text-emerald-500">
                        <ShieldCheck className="w-5 h-5" />
                    </div>
                </div>
                <div className="glass-panel p-6 rounded-xl border border-white/5 bg-[#030712]/60 flex items-center justify-between">
                    <div>
                        <p className="text-xs text-muted-foreground font-mono uppercase">Failures</p>
                        <h3 className="text-2xl font-bold text-white mt-1">1.8%</h3>
                    </div>
                    <div className="p-3 rounded-full bg-rose-500/10 text-rose-500">
                        <AlertCircle className="w-5 h-5" />
                    </div>
                </div>
                <div className="glass-panel p-6 rounded-xl border border-white/5 bg-[#030712]/60 flex items-center justify-between">
                    <div>
                        <p className="text-xs text-muted-foreground font-mono uppercase">Fingerprint</p>
                        <h3 className="text-2xl font-bold text-white mt-1">45M</h3>
                    </div>
                    <div className="p-3 rounded-full bg-blue-500/10 text-blue-500">
                        <Fingerprint className="w-5 h-5" />
                    </div>
                </div>
                <div className="glass-panel p-6 rounded-xl border border-white/5 bg-[#030712]/60 flex items-center justify-between">
                    <div>
                        <p className="text-xs text-muted-foreground font-mono uppercase">Iris Scans</p>
                        <h3 className="text-2xl font-bold text-white mt-1">12M</h3>
                    </div>
                    <div className="p-3 rounded-full bg-purple-500/10 text-purple-500">
                        <ScanEye className="w-5 h-5" />
                    </div>
                </div>
            </div>

            <div className="grid lg:grid-cols-3 gap-8">
                {/* Interactive Scanner */}
                <div className="lg:col-span-1">
                    <BioScanner />
                </div>

                {/* Logs Table (Existing) */}
                <div className="lg:col-span-2 glass-panel rounded-xl border border-white/5 bg-[#030712]/40 backdrop-blur-xl overflow-hidden flex flex-col">
                    <div className="p-6 border-b border-white/5 flex items-center justify-between shrink-0">
                        <div className="flex items-center gap-2">
                            <Terminal className="w-4 h-4 text-primary" />
                            <h3 className="font-mono text-sm text-white">LIVE_TRANSACTION_LOGS</h3>
                        </div>
                        <div className="relative">
                            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
                            <input type="text" placeholder="Filter logs..." className="h-8 w-64 bg-white/5 border border-white/10 rounded-md pl-8 pr-3 text-xs text-white focus:outline-none focus:border-primary/50 placeholder:text-muted-foreground/50 transition-colors" />
                        </div>
                    </div>
                    {/* Re-inserting the table content here manually since I'm overwriting the block */}
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="bg-white/5 text-muted-foreground font-mono text-xs uppercase tracking-wider">
                                <tr>
                                    <th className="px-6 py-4 font-medium">Log ID</th>
                                    <th className="px-6 py-4 font-medium">Method</th>
                                    <th className="px-6 py-4 font-medium">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {[
                                    { id: 'LOG-001', method: 'Fingerprint', status: 'success' },
                                    { id: 'LOG-002', method: 'Iris', status: 'error' },
                                    { id: 'LOG-003', method: 'OTP', status: 'pending' },
                                    { id: 'LOG-004', method: 'FaceID', status: 'success' },
                                    { id: 'LOG-005', method: 'Fingerprint', status: 'success' },
                                    { id: 'LOG-006', method: 'Iris', status: 'success' },
                                ].map((log) => (
                                    <tr key={log.id} className="hover:bg-white/5 transition-colors">
                                        <td className="px-6 py-3 font-mono text-xs text-muted-foreground">{log.id}</td>
                                        <td className="px-6 py-3 text-gray-300">{log.method}</td>
                                        <td className="px-6 py-3">
                                            <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${log.status === 'success' ? 'bg-emerald-500/10 text-emerald-500' :
                                                log.status === 'error' ? 'bg-red-500/10 text-red-500' : 'bg-yellow-500/10 text-yellow-500'
                                                }`}>{log.status}</span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
