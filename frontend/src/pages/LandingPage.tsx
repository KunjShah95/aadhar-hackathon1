import { motion } from 'framer-motion';
import { ArrowRight, Shield, Activity, Users, Mail, Globe, Lock, Cpu, Menu, X } from 'lucide-react';
import { useState, useEffect } from 'react';
import Pricing from './pricing/Pricing';

// Navbar Component
const Navbar = () => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <nav className="fixed w-full z-50 bg-[#030712]/80 backdrop-blur-md border-b border-white/5">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <div className="flex-shrink-0 flex items-center gap-2">
                        <Activity className="h-8 w-8 text-primary" />
                        <span className="text-white font-bold text-xl font-display">Aadhaar.AI</span>
                    </div>
                    <div className="hidden md:block">
                        <div className="ml-10 flex items-baseline space-x-4">
                            <a href="#home" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">Home</a>
                            <a href="#features" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">Features</a>
                            <a href="#pricing" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">Pricing</a>
                            <a href="#model" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">AI Model</a>
                            <a href="#about" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">About</a>
                            <a href="#contact" className="bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 px-4 py-2 rounded-md text-sm font-medium transition-all">Contact Us</a>
                        </div>
                    </div>
                    <div className="-mr-2 flex md:hidden">
                        <button
                            onClick={() => setIsOpen(!isOpen)}
                            className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none"
                        >
                            {isOpen ? <X className="block h-6 w-6" /> : <Menu className="block h-6 w-6" />}
                        </button>
                    </div>
                </div>
            </div>
            {/* Mobile Menu */}
            {isOpen && (
                <div className="md:hidden bg-[#030712] border-b border-white/5">
                    <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
                        <a href="#home" className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium">Home</a>
                        <a href="#features" className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium">Features</a>
                        <a href="#pricing" className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium">Pricing</a>
                        <a href="#model" className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium">AI Model</a>
                        <a href="#about" className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium">About</a>
                        <a href="#contact" className="text-primary block px-3 py-2 rounded-md text-base font-medium">Contact Us</a>
                    </div>
                </div>
            )}
        </nav>
    );
};

// Hero Section
const Hero = () => {
    return (
        <section id="home" className="relative min-h-screen flex items-center justify-center pt-16 overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0 bg-[#020408]">
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f2937_1px,transparent_1px),linear-gradient(to_bottom,#1f2937_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-20" />
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-primary/20 rounded-full blur-[100px] opacity-30 pointer-events-none" />
            </div>

            <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <div className="inline-flex items-center px-3 py-1 rounded-full border border-primary/20 bg-primary/10 text-primary text-xs font-mono mb-6 backdrop-blur-sm">
                        <span className="flex h-2 w-2 rounded-full bg-primary mr-2 animate-pulse" />
                        POWERED BY LIGHTGBM
                    </div>
                    <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-6 font-display">
                        Next-Gen Aadhaar <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-400">
                            Analytics Intelligence
                        </span>
                    </h1>
                    <p className="mt-4 text-xl text-gray-400 max-w-3xl mx-auto mb-10">
                        Harnessing the power of advanced machine learning to provide real-time demographic insights, biometric surveillance, and fraud detection at scale.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <button onClick={() => window.location.href = '/dashboard'} className="inline-flex items-center justify-center px-8 py-4 rounded-lg bg-primary text-white font-medium hover:bg-primary/90 transition-all shadow-[0_0_20px_rgba(14,165,233,0.3)]">
                            Access Dashboard <ArrowRight className="ml-2 h-5 w-5" />
                        </button>
                        <a href="#model" className="inline-flex items-center justify-center px-8 py-4 rounded-lg border border-white/10 bg-white/5 text-white font-medium hover:bg-white/10 transition-all backdrop-blur-sm">
                            Try Model API
                        </a>
                    </div>
                </motion.div>
            </div>
        </section>
    );
};

// Features Section
const Features = () => {
    const features = [
        { icon: Users, title: "Demographic Analysis", desc: "Granular population breakdown by region, age, and urban/rural distribution." },
        { icon: Shield, title: "Biometric Security", desc: "Real-time monitoring of authentication logs with anomaly detection." },
        { icon: Globe, title: "Geospatial Tracking", desc: "Live mapping of enrollment centers and activity hotspots across India." },
        { icon: Cpu, title: "AI Predictions", desc: "LightGBM-powered forecasting for enrollment trends and server load." }
    ];

    return (
        <section id="features" className="py-24 bg-[#030712] border-t border-white/5 relative">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold text-white font-display mb-4">Deep Science Capabilities</h2>
                    <p className="text-gray-400 max-w-2xl mx-auto">Our platform integrates cutting-edge visualizations with robust backend processing.</p>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {features.map((f, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: i * 0.1 }}
                            className="bg-white/5 border border-white/10 p-6 rounded-2xl hover:bg-white/10 transition-colors group"
                        >
                            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <f.icon className="w-6 h-6 text-primary" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">{f.title}</h3>
                            <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

// Model Playground Section
const ModelPlayground = () => {
    const [score, setScore] = useState(0.0012);

    useEffect(() => {
        const interval = setInterval(() => {
            setScore(() => +(Math.random() * 0.05).toFixed(4));
        }, 2000);
        return () => clearInterval(interval);
    }, []);

    return (
        <section id="model" className="py-24 bg-[#020408] relative overflow-hidden">
            <div className="absolute inset-0 bg-[#0ea5e9]/5 [mask-image:radial-gradient(ellipse_at_center,black,transparent)] pointer-events-none" />
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                <div className="grid lg:grid-cols-2 gap-12 items-center">
                    <div>
                        <div className="inline-flex items-center px-3 py-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 text-emerald-500 text-xs font-mono mb-6">
                            <Lock className="w-3 h-3 mr-2" />
                            SECURE ENDPOINT: /api/predict
                        </div>
                        <h2 className="text-3xl md:text-4xl font-bold text-white font-display mb-6">Experience the Power of LightGBM</h2>
                        <p className="text-gray-400 mb-8">
                            Our core prediction engine uses a highly optimized LightGBM model trained on over 1.4 billion records.
                            It delivers sub-millisecond inference latency for real-time fraud scoring.
                        </p>
                        <ul className="space-y-4 mb-8">
                            {['99.9% Accuracy in Demo Scenarios', 'Optimized for Low-Latency', 'Handles High-Cardinality Categorical Features'].map((item, i) => (
                                <li key={i} className="flex items-center text-gray-300">
                                    <div className="w-1.5 h-1.5 rounded-full bg-primary mr-3" />
                                    {item}
                                </li>
                            ))}
                        </ul>
                        <button className="px-6 py-3 bg-white text-black font-semibold rounded-lg hover:bg-gray-200 transition-colors">
                            View Documentation
                        </button>
                    </div>
                    <div className="relative">
                        <div className="absolute -inset-1 bg-gradient-to-r from-primary to-emerald-500 rounded-2xl blur opacity-30" />
                        <div className="relative bg-[#030712] border border-white/10 rounded-2xl p-8 font-mono text-sm">
                            <div className="flex items-center gap-2 mb-4 border-b border-white/5 pb-4">
                                <div className="w-3 h-3 rounded-full bg-red-500" />
                                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                                <div className="w-3 h-3 rounded-full bg-green-500" />
                                <span className="ml-2 text-muted-foreground">model_inference.py</span>
                            </div>
                            <div className="space-y-2 text-gray-400">
                                <p><span className="text-purple-400">import</span> lightgbm <span className="text-purple-400">as</span> lgb</p>
                                <p><span className="text-purple-400">import</span> numpy <span className="text-purple-400">as</span> np</p>
                                <br />
                                <p className="text-gray-500"># Load pre-trained model</p>
                                <p>model = lgb.Booster(model_file=<span className="text-green-400">'best_model.pkl'</span>)</p>
                                <br />
                                <p className="text-gray-500"># Run inference</p>
                                <p>prediction = model.predict([</p>
                                <p className="pl-4">feature_vector</p>
                                <p>])</p>
                                <br />
                                <p><span className="text-blue-400">print</span>(f<span className="text-green-400">"Fraud Score: {score}"</span>)</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

// Footer
const Footer = () => {
    return (
        <footer id="contact" className="bg-[#020408] border-t border-white/5 py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid md:grid-cols-4 gap-8">
                    <div className="col-span-2">
                        <div className="flex items-center gap-2 mb-4">
                            <Activity className="h-6 w-6 text-primary" />
                            <span className="text-white font-bold text-lg font-display">Aadhaar.AI</span>
                        </div>
                        <p className="text-gray-400 text-sm max-w-sm">
                            The next generation of identity analytics. Secure, fast, and intelligent processing for the world's largest biometric database.
                        </p>
                    </div>
                    <div>
                        <h4 className="text-white font-semibold mb-4">Platform</h4>
                        <ul className="space-y-2 text-sm text-gray-400">
                            <li><a href="#" className="hover:text-primary transition-colors">Overview</a></li>
                            <li><a href="#" className="hover:text-primary transition-colors">Analytics</a></li>
                            <li><a href="#" className="hover:text-primary transition-colors">API Docs</a></li>
                        </ul>
                    </div>
                    <div>
                        <h4 className="text-white font-semibold mb-4">Legal</h4>
                        <ul className="space-y-2 text-sm text-gray-400">
                            <li><a href="#" className="hover:text-primary transition-colors">Privacy Policy</a></li>
                            <li><a href="#" className="hover:text-primary transition-colors">Terms of Service</a></li>
                            <li><a href="#" className="hover:text-primary transition-colors">Security</a></li>
                        </ul>
                    </div>
                </div>
                <div className="mt-12 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center text-sm text-gray-500">
                    <p>&copy; 2026 Aadhaar Hackathon Team. All rights reserved.</p>
                    <div className="flex gap-4 mt-4 md:mt-0">
                        <Mail className="w-4 h-4 hover:text-white cursor-pointer" />
                        <Globe className="w-4 h-4 hover:text-white cursor-pointer" />
                    </div>
                </div>
            </div>
        </footer>
    );
}

export default function LandingPage() {
    return (
        <div className="bg-[#020408] min-h-screen text-white selection:bg-primary/20">
            <Navbar />
            <Hero />
            <Features />
            <section id="pricing" className="py-24 bg-[#030712] border-t border-white/5 relative">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <Pricing />
                </div>
            </section>
            <ModelPlayground />
            <Footer />
        </div>
    );
}
