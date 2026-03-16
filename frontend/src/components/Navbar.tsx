import { motion } from 'framer-motion';
import { Search, Bell, User, LayoutDashboard, Trophy, Cpu, Dumbbell } from 'lucide-react';

interface NavbarProps {
    activeTab: string;
    setActiveTab: (tab: string) => void;
}

export const Navbar = ({ activeTab, setActiveTab }: NavbarProps) => {
    const navItems = [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'match_center', label: 'Match Center', icon: Trophy },
        { id: 'ipl_intelligence', label: 'IPL Intelligence', icon: Cpu },
        { id: 'training_assistant', label: 'Training Assistant', icon: Dumbbell },
    ];

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-xl border-b border-white/10 px-8 h-20">
            <div className="max-w-[1600px] mx-auto h-full flex items-center justify-between gap-8">
                {/* Logo Section */}
                <div className="flex items-center gap-2 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
                    <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-neon">
                        <span className="text-background font-black text-xl italic">C</span>
                    </div>
                    <span className="text-2xl font-outfit font-black uppercase tracking-tighter italic">Cric<span className="text-primary">AI</span></span>
                </div>

                {/* Nav Links */}
                <div className="flex items-center gap-2 flex-1 max-w-2xl">
                    {navItems.map((item) => (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id)}
                            className={`flex items-center gap-2 px-6 py-2 rounded-xl text-sm font-bold uppercase transition-all relative ${activeTab === item.id ? 'text-primary' : 'text-text/50 hover:text-white'
                                }`}
                        >
                            <item.icon className="w-4 h-4" />
                            {item.label}
                            {activeTab === item.id && (
                                <motion.div
                                    layoutId="nav-active"
                                    className="absolute inset-0 bg-primary/10 rounded-xl -z-10"
                                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                                />
                            )}
                        </button>
                    ))}
                </div>

                {/* Search & Profile */}
                <div className="flex items-center gap-6">
                    <div className="relative w-64">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text/40 w-4 h-4" />
                        <input
                            type="text"
                            placeholder="Quick Search..."
                            className="w-full bg-white/5 border border-white/10 rounded-lg py-1.5 pl-10 pr-4 text-xs focus:outline-none focus:border-primary/50 transition-all font-outfit"
                        />
                    </div>

                    <div className="h-8 w-px bg-white/10" />

                    <div className="flex items-center gap-4">
                        <button className="relative text-text/70 hover:text-white transition-colors">
                            <Bell className="w-5 h-5" />
                            <span className="absolute -top-1 -right-1 w-2 h-2 bg-accent rounded-full border-2 border-background"></span>
                        </button>
                        <div className="w-10 h-10 bg-surface rounded-full border border-white/10 flex items-center justify-center overflow-hidden cursor-pointer hover:border-primary/50 transition-colors">
                            <User className="text-text/70 w-5 h-5" />
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
};
