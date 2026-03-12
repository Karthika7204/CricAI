import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { BookMarked, GraduationCap, Target, Cpu } from 'lucide-react';

const seasonData = [
    { name: 'Match 1', impact: 45, runs: 28 },
    { name: 'Match 2', impact: 82, runs: 74 },
    { name: 'Match 3', impact: 35, runs: 12 },
    { name: 'Match 4', impact: 95, runs: 102 },
    { name: 'Match 5', impact: 60, runs: 45 },
    { name: 'Match 6', impact: 78, runs: 68 },
];

export const AnalyticsHub = () => {
    return (
        <div className="space-y-10 pb-20">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-outfit font-black uppercase italic">Analytics <span className="text-primary">Hub</span></h1>
                    <p className="text-text/50 font-medium">Deep-dive into seasonal trends and tactical intelligence.</p>
                </div>
                <div className="flex gap-4">
                    <div className="glass-card px-6 py-2 bg-primary/10 border-primary/30">
                        <p className="text-[10px] font-black uppercase tracking-widest text-primary">Season AI Score</p>
                        <p className="text-2xl font-black">8.4<span className="text-xs opacity-50 ml-1">/10</span></p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-8">
                {/* Season Trends Chart */}
                <div className="col-span-2 glass-card p-8">
                    <h3 className="text-xl font-bold mb-8 flex items-center gap-2">
                        <Target className="text-primary" /> Performance Momentum
                    </h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={seasonData}>
                                <defs>
                                    <linearGradient id="colorImpact" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#66FCF1" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#66FCF1" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#2D3748" vertical={false} />
                                <XAxis dataKey="name" stroke="#718096" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#718096" fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1F2833', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                                    itemStyle={{ color: '#66FCF1' }}
                                />
                                <Area type="monotone" dataKey="impact" stroke="#66FCF1" strokeWidth={3} fillOpacity={1} fill="url(#colorImpact)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Learning Corner */}
                <div className="glass-card p-8 bg-surface border-white/5 flex flex-col">
                    <div className="mb-6">
                        <GraduationCap className="text-accent w-10 h-10 mb-4" />
                        <h3 className="text-xl font-bold mb-2">Tactical Academy</h3>
                        <p className="text-sm text-text/60 leading-relaxed">
                            AI-driven lessons based on real match scenarios from this season.
                        </p>
                    </div>

                    <div className="space-y-4 flex-1">
                        {[
                            { title: 'The Anchor Role', level: 'Beginner', xp: '120' },
                            { title: 'Death Over Geometry', level: 'Advanced', xp: '450' },
                            { title: 'Spin vs. Powerplay', level: 'Intermediate', xp: '280' },
                        ].map((lesson, idx) => (
                            <div key={idx} className="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-primary/30 transition-all cursor-pointer group">
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-[10px] font-black uppercase tracking-tighter text-accent bg-accent/10 px-2 py-0.5 rounded">{lesson.level}</span>
                                    <span className="text-[10px] font-bold text-text/40">+{lesson.xp} XP</span>
                                </div>
                                <p className="font-bold group-hover:text-primary transition-colors">{lesson.title}</p>
                            </div>
                        ))}
                    </div>

                    <button className="w-full mt-6 py-3 rounded-xl bg-accent text-background font-black uppercase tracking-widest text-xs hover:shadow-neon transition-all">
                        Continue Learning
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-4 gap-6">
                {[
                    { icon: BookMarked, label: 'Tactical Playbook', count: '14' },
                    { icon: Cpu, label: 'AI Strategy Logs', count: '256' },
                    { icon: Target, label: 'Success Rate', count: '68%' },
                    { icon: GraduationCap, label: 'Course Progress', count: '42%' },
                ].map((stat, i) => (
                    <div key={i} className="glass-card p-6 flex flex-col items-center justify-center text-center">
                        <stat.icon className="text-primary/50 w-6 h-6 mb-4" />
                        <p className="text-2xl font-black mb-1">{stat.count}</p>
                        <p className="text-xs font-bold text-text/40 uppercase tracking-widest">{stat.label}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};
