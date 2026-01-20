import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Activity, Bell, Settings, User, Search, Menu, X, ArrowRight } from 'lucide-react';
import { useState, useEffect } from 'react';

export function MainLayout({ children }: { children: React.ReactNode }) {
    const [showNotifications, setShowNotifications] = useState(false);
    const [showMobileMenu, setShowMobileMenu] = useState(false);
    const [showCmd, setShowCmd] = useState(false);
    const [lang, setLang] = useState<'en' | 'hi'>('en'); // Language State
    const navigate = useNavigate();
    const [notifications, setNotifications] = useState([
        { id: 1, title: "High Latency Detected", desc: "North-East Region Cluster", time: "2m ago", type: "alert" },
        { id: 2, title: "Model Retrained", desc: "Fraud_Detection_v2.4 ready", time: "1h ago", type: "success" },
        { id: 3, title: "System Maintenance", desc: "Scheduled for 02:00 AM UTC", time: "4h ago", type: "info" },
    ]);

    const commands = [
        { id: 'dashboard', label: 'Go to Dashboard', path: '/', icon: Activity },
        { id: 'prediction', label: 'Prediction Studio', path: '/prediction-studio', icon: Search },
        { id: 'demographics', label: 'Demographics Overview', path: '/demographics', icon: User },
        { id: 'biometrics', label: 'Biometrics Lab', path: '/biometrics', icon: Activity },
    ];

    useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                setShowCmd((open) => !open);
            }
        };
        document.addEventListener('keydown', down);
        return () => document.removeEventListener('keydown', down);
    }, []);

    const handleCommand = (path: string) => {
        navigate(path);
        setShowCmd(false);
    };
    return (
        <div className="relative min-h-screen bg-background text-foreground font-sans selection:bg-primary/30 overflow-hidden">

            {/* Ambient Background Layer - "The Deep" */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary/20 blur-[120px] animate-spotlight opacity-40 mix-blend-screen" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[40%] h-[40%] rounded-full bg-science-500/10 blur-[100px] animate-float delay-1000 opacity-30 mix-blend-screen" />
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150 mix-blend-overlay"></div>
            </div>

            {/* Header - "HUD Top Bar" */}
            <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-[#030712]/70 backdrop-blur-xl supports-[backdrop-filter]:bg-[#030712]/40">
                <div className="container flex h-16 max-w-screen-2xl items-center justify-between px-4 md:px-8">
                    {/* Left Side: Logo & Mobile Toggle */}
                    <div className="flex items-center gap-4">
                        {/* Mobile Menu Toggle */}
                        <button
                            className="md:hidden p-2 text-muted-foreground hover:text-white transition-colors"
                            onClick={() => setShowMobileMenu(!showMobileMenu)}
                        >
                            {showMobileMenu ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                        </button>

                        {/* Logo Area */}
                        <div className="flex items-center space-x-3 group cursor-pointer" onClick={() => navigate('/')}>
                            <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 group-hover:border-primary/50 transition-colors duration-300">
                                <Activity className="h-5 w-5 text-primary animate-pulse-slow" />
                            </div>
                            <span className="font-display font-bold text-lg tracking-tight bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent group-hover:to-white transition-all duration-300 hidden sm:inline-block">
                                {lang === 'en' ? 'Aadhaar' : 'आधार'}
                                <span className="font-light text-primary mx-1">/</span>
                                {lang === 'en' ? 'OS' : 'OS'}
                            </span>
                        </div>
                    </div>

                    {/* Desktop Flight Navigation */}
                    <nav className="hidden md:flex items-center space-x-1 border-l border-white/5 pl-6 h-8">
                        <Link to="/" className="px-3 py-1.5 text-sm font-medium text-muted-foreground hover:text-primary hover:bg-white/5 rounded-md transition-all duration-200">
                            Overview
                        </Link>
                        <Link to="/demographics" className="px-3 py-1.5 text-sm font-medium text-muted-foreground hover:text-primary hover:bg-white/5 rounded-md transition-all duration-200">
                            Demographics
                        </Link>
                        <Link to="/biometrics" className="px-3 py-1.5 text-sm font-medium text-muted-foreground hover:text-primary hover:bg-white/5 rounded-md transition-all duration-200">
                            Biometrics
                        </Link>
                        <Link to="/live-map" className="px-3 py-1.5 text-sm font-medium text-muted-foreground hover:text-primary hover:bg-white/5 rounded-md transition-all duration-200">
                            Live Map
                        </Link>
                        <Link to="/prediction-studio" className="px-3 py-1.5 text-sm font-medium text-muted-foreground hover:text-primary hover:bg-white/5 rounded-md transition-all duration-200">
                            AI Studio
                        </Link>
                        <Link to="/pricing" className="px-3 py-1.5 text-sm font-medium text-muted-foreground hover:text-primary hover:bg-white/5 rounded-md transition-all duration-200">
                            Commercial
                        </Link>
                    </nav>

                    {/* HUD Controls */}
                    <div className="flex items-center gap-2 sm:gap-3">
                        {/* Language Toggle Badge - Visible on all screens but compact on mobile */}
                        <div className="flex bg-white/5 rounded border border-white/10 p-0.5 mr-2">
                            <button
                                onClick={() => setLang('en')}
                                className={`px-1.5 py-0.5 text-[10px] font-bold rounded ${lang === 'en' ? 'bg-primary text-black' : 'text-gray-500 hover:text-white'}`}
                            >EN</button>
                            <button
                                onClick={() => setLang('hi')}
                                className={`px-1.5 py-0.5 text-[10px] font-bold rounded ${lang === 'hi' ? 'bg-primary text-black' : 'text-gray-500 hover:text-white'}`}
                            >HI</button>
                        </div>

                        <div className="hidden md:flex relative group">
                            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                            <input
                                type="text"
                                placeholder="Search ecosystem... (Ctrl+K)"
                                onClick={() => setShowCmd(true)}
                                readOnly
                                className="h-9 w-64 cursor-pointer rounded-lg bg-white/5 border border-white/10 pl-9 pr-4 text-sm outline-none focus:border-primary/50 focus:bg-white/10 focus:ring-1 focus:ring-primary/20 transition-all placeholder:text-muted-foreground/50"
                            />
                        </div>

                        {/* Mobile Search Icon */}
                        <button
                            className="md:hidden p-2 text-muted-foreground hover:text-white"
                            onClick={() => setShowCmd(true)}
                        >
                            <Search className="h-5 w-5" />
                        </button>

                        <div className="h-6 w-px bg-white/10 mx-2 hidden md:block" />

                        <button
                            onClick={() => setShowNotifications(!showNotifications)}
                            className={`relative p-2 transition-colors rounded-lg hover:bg-white/5 ${showNotifications ? 'text-white bg-white/5' : 'text-muted-foreground'}`}
                        >
                            <Bell className="h-5 w-5" />
                            <span className="absolute top-2 right-2 h-1.5 w-1.5 rounded-full bg-red-500 ring-2 ring-background animate-pulse" />
                        </button>

                        {/* Notification Dropdown */}
                        {showNotifications && (
                            <div className="absolute top-16 right-4 sm:right-20 w-80 bg-[#030712]/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl z-50 overflow-hidden animate-in slide-in-from-top-2 fade-in duration-200">
                                <div className="flex items-center justify-between p-4 border-b border-white/5">
                                    <h3 className="font-semibold text-sm text-white">Notifications</h3>
                                    <button onClick={() => setShowNotifications(false)} className="text-muted-foreground hover:text-white">
                                        <X className="w-4 h-4" />
                                    </button>
                                </div>
                                <div className="max-h-[300px] overflow-y-auto">
                                    {notifications.map((n) => (
                                        <div key={n.id} className="p-4 border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer group">
                                            <div className="flex gap-3">
                                                <div className={`mt-1 h-2 w-2 rounded-full flex-shrink-0 ${n.type === 'alert' ? 'bg-red-500' :
                                                    n.type === 'success' ? 'bg-emerald-500' : 'bg-blue-500'
                                                    }`} />
                                                <div>
                                                    <p className="text-sm text-balance text-white font-medium group-hover:text-primary transition-colors">{n.title}</p>
                                                    <p className="text-xs text-muted-foreground mt-1">{n.desc}</p>
                                                    <p className="text-[10px] text-gray-500 mt-2 font-mono">{n.time}</p>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <div className="p-3 bg-white/5 text-center">
                                    <button className="text-xs text-primary hover:text-primary/80 transition-colors font-medium">
                                        View All Activity
                                    </button>
                                </div>
                            </div>
                        )}

                        <button className="hidden md:block p-2 text-muted-foreground hover:text-white transition-colors rounded-lg hover:bg-white/5">
                            <Settings className="h-5 w-5" />
                        </button>

                        <div className="pl-2">
                            <div className="h-9 w-9 rounded-full bg-gradient-to-tr from-primary/20 to-science-400/20 flex items-center justify-center border border-white/10 hover:border-primary/50 cursor-pointer transition-all active:scale-95 group">
                                <User className="h-4 w-4 text-primary group-hover:text-white transition-colors" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Mobile Navigation Drawer */}
                {showMobileMenu && (
                    <div className="md:hidden border-t border-white/10 bg-[#030712]/95 backdrop-blur-xl animate-in slide-in-from-top-2 fade-in duration-200 absolute w-full z-40">
                        <nav className="flex flex-col p-4 space-y-2">
                            <Link
                                to="/"
                                className="px-4 py-3 text-sm font-medium text-muted-foreground hover:text-primary hover:bg-white/5 rounded-lg transition-all duration-200 flex items-center gap-3"
                                onClick={() => setShowMobileMenu(false)}
                            >
                                <Activity className="w-4 h-4" /> Overview
                            </Link>
                            <Link
                                to="/demographics"
                                className="px-4 py-3 text-sm font-medium text-muted-foreground hover:text-primary hover:bg-white/5 rounded-lg transition-all duration-200 flex items-center gap-3"
                                onClick={() => setShowMobileMenu(false)}
                            >
                                <User className="w-4 h-4" /> Demographics
                            </Link>
                            <Link
                                to="/biometrics"
                                className="px-4 py-3 text-sm font-medium text-muted-foreground hover:text-primary hover:bg-white/5 rounded-lg transition-all duration-200 flex items-center gap-3"
                                onClick={() => setShowMobileMenu(false)}
                            >
                                <Activity className="w-4 h-4" /> Biometrics
                            </Link>
                            <Link
                                to="/live-map"
                                className="px-4 py-3 text-sm font-medium text-muted-foreground hover:text-primary hover:bg-white/5 rounded-lg transition-all duration-200 flex items-center gap-3"
                                onClick={() => setShowMobileMenu(false)}
                            >
                                <Activity className="w-4 h-4" /> Live Map
                            </Link>
                            <Link
                                to="/prediction-studio"
                                className="px-4 py-3 text-sm font-medium text-muted-foreground hover:text-primary hover:bg-white/5 rounded-lg transition-all duration-200 flex items-center gap-3"
                                onClick={() => setShowMobileMenu(false)}
                            >
                                <Search className="w-4 h-4" /> AI Studio
                            </Link>
                            <Link
                                to="/pricing"
                                className="px-4 py-3 text-sm font-medium text-muted-foreground hover:text-primary hover:bg-white/5 rounded-lg transition-all duration-200 flex items-center gap-3"
                                onClick={() => setShowMobileMenu(false)}
                            >
                                <Activity className="w-4 h-4" /> Commercial
                            </Link>
                        </nav>
                    </div>
                )}
            </header>

            {/* Main Stage */}
            <main className="relative z-10 flex-1 container max-w-screen-2xl py-8 px-4 md:px-8 space-y-8 min-h-[calc(100vh-4rem)]">
                {children}
            </main>

            {/* Command Palette Overlay */}
            {showCmd && (
                <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-start justify-center pt-[20vh] animate-in fade-in duration-200">
                    <div className="w-full max-w-lg bg-[#0d1117] border border-white/10 rounded-xl shadow-2xl overflow-hidden animate-in zoom-in-95 leading-none">
                        <div className="flex items-center px-4 border-b border-white/10">
                            <Search className="w-5 h-5 text-muted-foreground mr-3" />
                            <input
                                autoFocus
                                placeholder="Type a command or search..."
                                className="flex-1 py-4 bg-transparent text-white outline-none placeholder:text-muted-foreground"
                            />
                            <div className="px-1.5 py-0.5 rounded border border-white/10 bg-white/5 text-[10px] text-muted-foreground">ESC</div>
                        </div>
                        <div className="py-2 max-h-[300px] overflow-y-auto">
                            <div className="px-2 pb-1 text-[10px] uppercase tracking-wider text-muted-foreground font-mono">Navigation</div>
                            {commands.map((cmd) => (
                                <button
                                    key={cmd.id}
                                    onClick={() => handleCommand(cmd.path)}
                                    className="w-full px-4 py-3 flex items-center justify-between hover:bg-white/5 text-left group transition-colors"
                                >
                                    <div className="flex items-center gap-3">
                                        <cmd.icon className="w-4 h-4 text-gray-400 group-hover:text-primary transition-colors" />
                                        <span className="text-sm text-gray-200 group-hover:text-white">{cmd.label}</span>
                                    </div>
                                    <ArrowRight className="w-4 h-4 text-white/0 group-hover:text-white/50 -translate-x-2 group-hover:translate-x-0 transition-all" />
                                </button>
                            ))}
                        </div>
                        <div className="p-2 border-t border-white/10 bg-white/5 flex justify-between items-center text-[10px] text-muted-foreground px-4">
                            <span>Aadhaar/OS Neural Interface</span>
                            <span>v2.4.0</span>
                        </div>
                    </div>
                    {/* Click outside to close */}
                    <div className="absolute inset-0 -z-10" onClick={() => setShowCmd(false)} />
                </div>
            )}

            {/* Footer - "System Status" */}
            <footer className="relative z-10 border-t border-white/5 bg-[#030712]/80 backdrop-blur-xl py-6 md:py-0">
                <div className="container flex flex-col items-center justify-between gap-4 md:h-14 md:flex-row max-w-screen-2xl px-4 md:px-8">
                    <p className="text-xs text-muted-foreground font-mono">
                        UIDAI // SECURE TERMINAL // <span className="text-green-500">CONNECTED</span>
                    </p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span className="hover:text-primary cursor-pointer transition-colors">System Health</span>
                        <span className="hover:text-primary cursor-pointer transition-colors">Privacy Policy</span>
                        <span className="hover:text-primary cursor-pointer transition-colors">v2.4.0-RC1</span>
                    </div>
                </div>
            </footer>
        </div>
    );
}
