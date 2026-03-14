import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Award, Zap, ChevronRight, MessageCircle, ChevronLeft, Share2, MoreVertical, PlayCircle, BarChart3, TrendingUp, Info, Bot } from 'lucide-react';
import { matchApi } from '../api';

export const MatchDetail = ({ matchId, onBack }: { matchId: string, onBack: () => void }) => {
    const [data, setData] = useState<any>(null);
    const [activeTab, setActiveTab] = useState('Post-match Talk');

    const tabs = [
        { id: 'Post-match Talk', label: 'Post-match Talk', icon: MessageCircle },
        { id: 'Scorecard', label: 'Scorecard', icon: Info },
        { id: 'Match Flow', label: 'AI Match Flow', icon: PlayCircle },
        { id: 'Pre-match Insights', label: 'Pre-match Insights', icon: Zap },
        { id: 'AI Stats & Awards', label: 'AI Stats & Awards', icon: Award },
        { id: 'Recommendation Bot', label: 'Recommendation Bot', icon: TrendingUp },
        { id: 'Overs', label: 'Overs', icon: BarChart3 },
        { id: 'Table', label: 'Table', icon: BarChart3 }
    ];

    useEffect(() => {
        Promise.all([
            matchApi.getFlow(matchId),
            matchApi.getAwards(matchId),
            matchApi.getInsights(matchId),
            matchApi.getScorecard(matchId)
        ]).then(([flow, awards, insights, scorecard]) => {
            setData({
                flow: flow.data,
                awards: awards.data,
                insights: insights.data,
                scorecard: scorecard.data
            });
        });
    }, [matchId]);

    if (!data) return (
        <div className="flex items-center justify-center h-96">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
    );

    return (
        <div className="space-y-6 max-w-[1200px] mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Breadcrumb / Navigation */}
            <div className="flex items-center justify-between text-text/50 text-[11px] font-medium uppercase tracking-wider border-b border-white/5 pb-4">
                <div className="flex items-center gap-4">
                    <button onClick={onBack} className="hover:text-primary flex items-center gap-1 bg-white/5 px-2 py-1 rounded transition-colors">
                        <ChevronLeft className="w-3 h-3" /> Result
                    </button>
                    <span>3rd Match, Group A (N), Wankhede, February 07, 2026, ICC Men's T20 World Cup</span>
                </div>
                <div className="flex items-center gap-6">
                    <Share2 className="w-4 h-4 cursor-pointer hover:text-white" />
                    <MoreVertical className="w-4 h-4 cursor-pointer hover:text-white" />
                </div>
            </div>

            {/* Score Header Section */}
            <div className="grid grid-cols-4 gap-8">
                <div className="col-span-3 glass-card p-8 bg-surface/40">
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-8 bg-white/5 rounded flex items-center justify-center border border-white/10 overflow-hidden">
                                    <span className="text-xl font-black italic">IND</span>
                                </div>
                                <h2 className="text-4xl font-outfit font-black uppercase tracking-tighter">India</h2>
                            </div>
                            <div className="text-4xl font-outfit font-black tracking-tight">161/9</div>
                        </div>
                        <div className="flex items-center justify-between opacity-40">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-8 bg-white/5 rounded flex items-center justify-center border border-white/10 overflow-hidden">
                                    <span className="text-xl font-black italic">USA</span>
                                </div>
                                <h2 className="text-4xl font-outfit font-black uppercase tracking-tighter">U.S.A.</h2>
                            </div>
                            <div className="text-right">
                                <span className="text-sm font-bold mr-4">(20 ov, T:162)</span>
                                <span className="text-4xl font-outfit font-black tracking-tight">132/8</span>
                            </div>
                        </div>
                        <div className="text-primary font-black text-xl pt-2 italic drop-shadow-neon uppercase tracking-widest">India won by 29 runs</div>
                    </div>
                </div>

                {/* POTM / MVP Section */}
                <div className="space-y-4">
                    {data.awards?.awards?.player_of_the_match && (
                        <>
                            <div className="glass-card p-4 flex items-center gap-4 border-accent/20 bg-accent/5">
                                <div className="w-12 h-12 bg-accent/20 rounded-full flex items-center justify-center border border-accent/20 ring-4 ring-accent/5">
                                    <Award className="text-accent w-6 h-6" />
                                </div>
                                <div className="flex-1">
                                    <p className="text-[10px] font-black uppercase text-accent/60 tracking-widest leading-none mb-1">PotM</p>
                                    <p className="font-bold text-white leading-tight truncate">{data.awards.awards.player_of_the_match.name}</p>
                                    <p className="text-[10px] font-bold text-text/50 uppercase">{data.awards.awards.player_of_the_match.team}</p>
                                </div>
                            </div>
                            <div className="glass-card p-4 flex items-center gap-4 border-primary/20 bg-primary/5">
                                <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center border border-primary/20 ring-4 ring-primary/5">
                                    <TrendingUp className="text-primary w-6 h-6" />
                                </div>
                                <div className="flex-1">
                                    <p className="text-[10px] font-black uppercase text-primary/60 tracking-widest leading-none mb-1">CricAI MVP</p>
                                    <p className="font-bold text-white leading-tight truncate">Suryakumar Yadav</p>
                                    <div className="flex items-center justify-between mt-1">
                                        <p className="text-xs font-black">149.6 <span className="opacity-40 font-normal">pts</span></p>
                                        <ChevronRight className="w-3 h-3 text-primary" />
                                    </div>
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* Unified Tab Bar */}
            <div className="flex border-b border-white/10 overflow-x-auto scrollbar-hide bg-surface/20 rounded-t-xl px-2">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-8 py-5 text-xs font-black uppercase tracking-widest whitespace-nowrap transition-all border-b-2 relative group ${activeTab === tab.id ? 'text-primary border-primary' : 'text-text/40 border-transparent hover:text-text'
                            }`}
                    >
                        <tab.icon className={`w-4 h-4 transition-transform group-hover:scale-110 ${activeTab === tab.id ? 'text-primary' : 'text-text/30'}`} />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Content Area */}
            <div className="glass-card overflow-hidden bg-surface/20">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.2 }}
                        className="min-h-[500px]"
                    >
                        {activeTab === 'Post-match Talk' && <PostMatchChat matchId={matchId} />}

                        {activeTab === 'Scorecard' && (
                            <div className="divide-y divide-white/10">
                                {data.scorecard?.innings ? Object.values(data.scorecard.innings).map((inn: any, idx: number) => (
                                    <div key={idx} className="p-1">
                                        <div className="bg-primary/10 px-6 py-4 border-b border-white/5 flex items-center justify-between">
                                            <h3 className="font-outfit font-black uppercase text-primary tracking-widest flex items-center gap-2">
                                                {inn.team} <span className="text-[10px] font-bold opacity-60">({inn.total_runs}/{inn.wickets})</span>
                                            </h3>
                                            <span className="text-[10px] font-black text-primary/40 uppercase">{idx === 0 ? '1st' : '2nd'} Innings</span>
                                        </div>
                                        {/* Batting Table */}
                                        <ScorecardTable batters={inn.batting} />

                                        {/* Bowling Table */}
                                        <div className="bg-surface/40 px-6 py-2 border-y border-white/5">
                                            <span className="text-[10px] font-black uppercase tracking-widest text-text/40">Bowling Analysis</span>
                                        </div>
                                        <BowlingTable bowlers={inn.bowling} />
                                    </div>
                                )) : (
                                    <div className="p-20 text-center opacity-30 italic">No detailed scorecard available for this match.</div>
                                )}
                            </div>
                        )}

                        {activeTab === 'Match Flow' && (
                            <div className="p-10 space-y-8">
                                <div className="flex items-center gap-4 mb-6">
                                    <div className="p-3 bg-primary/10 rounded-2xl"><PlayCircle className="text-primary w-8 h-8" /></div>
                                    <div>
                                        <h3 className="font-outfit font-black uppercase text-2xl tracking-tighter">Tactical Match Flow</h3>
                                        <p className="text-xs font-bold text-text/40 tracking-widest uppercase">AI Summarized Turning Points</p>
                                    </div>
                                </div>
                                <div className="space-y-4">
                                    {data.flow.flow_points?.map((p: string, i: number) => (
                                        <div key={i} className="flex gap-6">
                                            <div className="flex flex-col items-center">
                                                <div className="w-3 h-3 rounded-full bg-primary shadow-neon" />
                                                <div className="w-px flex-1 bg-gradient-to-b from-primary/30 to-transparent my-1" />
                                            </div>
                                            <div className="pb-8">
                                                <p className="text-base text-text/80 leading-relaxed font-medium">{p}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {activeTab === 'Pre-match Insights' && (
                            <div className="p-10">
                                <div className="flex items-center gap-4 mb-8">
                                    <div className="p-3 bg-accent/10 rounded-2xl"><Zap className="text-accent w-8 h-8" /></div>
                                    <div>
                                        <h3 className="font-outfit font-black uppercase text-2xl tracking-tighter">Pre-match Intelligence</h3>
                                    </div>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {data.insights?.textual_insights?.map((insight: string, idx: number) => (
                                        <div key={idx} className="p-6 bg-white/5 border border-white/10 rounded-2xl border-l-4 border-l-accent hover:bg-white/10 transition-colors">
                                            <p className="text-sm italic text-text/70">"{insight}"</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {activeTab === 'AI Stats & Awards' && (
                            <div className="p-10">
                                <div className="flex items-center gap-4 mb-10">
                                    <div className="p-3 bg-primary/10 rounded-2xl"><Award className="text-primary w-8 h-8" /></div>
                                    <h3 className="font-outfit font-black uppercase text-2xl tracking-tighter">AI Post-Match Recognition</h3>
                                </div>
                                <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                                    {Object.entries(data.awards?.awards || {}).map(([key, award]: [string, any], i: number) => (
                                        <div key={i} className="glass-card p-6 flex flex-col items-center text-center hover:border-primary/30 transition-all cursor-default group">
                                            <div className="w-12 h-12 bg-white/5 rounded-xl flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                                                <Award className="w-6 h-6 text-primary/40 group-hover:text-primary" />
                                            </div>
                                            <p className="text-[10px] font-black uppercase text-text/40 tracking-widest mb-1">{key.replace(/_/g, ' ')}</p>
                                            <p className="text-sm font-bold text-white mb-2">{award.name}</p>
                                            <p className="text-[10px] font-black uppercase px-3 py-1 bg-white/5 rounded-full text-primary border border-primary/10">{award.team}</p>
                                            <p className="mt-4 text-[11px] opacity-40 italic leading-snug">"{award.reason || 'Outstanding match contribution'}"</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {activeTab === 'Recommendation Bot' && <RecommendationBot matchId={matchId} />}
                    </motion.div>
                </AnimatePresence>
            </div>
        </div>
    );
};

const RecommendationBot = ({ matchId }: { matchId: string }) => {
    const [messages, setMessages] = useState([
        { role: 'bot', text: 'Hello! I am the CricAI Recommendation Bot. Ask me about PvP matchups, strategic rotations (batting/bowling), or tactical pressure avoidance for this match!' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;
        const newMsgs = [...messages, { role: 'user', text: input }];
        setMessages(newMsgs);
        setInput('');
        setIsLoading(true);
        try {
            const res = await matchApi.chat(matchId, input);
            setMessages([...newMsgs, { role: 'bot', text: res.data.answer }]);
        } catch {
            setMessages([...newMsgs, { role: 'bot', text: 'Strategy engine busy. Please try again.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => { scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight); }, [messages]);

    return (
        <div className="flex flex-col h-[600px] max-w-[1000px] mx-auto">
            <div className="p-8 pb-0 flex items-center gap-4">
                <div className="p-3 bg-primary/10 rounded-2xl"><TrendingUp className="text-primary w-8 h-8" /></div>
                <div>
                    <h3 className="font-outfit font-black uppercase text-2xl tracking-tighter">Tactical Recommendation Bot</h3>
                    <p className="text-[10px] font-bold text-text/40 tracking-widest uppercase mb-1">PvP · Strategy · Pressure Avoidance</p>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-8 space-y-6" ref={scrollRef}>
                {messages.map((m, i) => (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        key={i}
                        className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div className={`flex gap-3 max-w-[85%] ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center border shrink-0 ${m.role === 'user' ? 'bg-primary border-primary' : 'bg-surface border-white/10'}`}>
                                {m.role === 'user' ? <TrendingUp className="w-4 h-4 text-background" /> : <Bot className="w-4 h-4 text-primary" />}
                            </div>
                            <div className={`p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-line ${m.role === 'user' ? 'bg-primary text-background font-medium shadow-neon' : 'bg-surface/80 border border-white/5 shadow-xl'}`}>
                                {m.text}
                            </div>
                        </div>
                    </motion.div>
                ))}
                {isLoading && (
                    <div className="flex items-center gap-2 ml-11">
                        <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                        <span className="text-[10px] font-black uppercase tracking-widest text-primary/60 ml-2">Analyzing Tactics...</span>
                    </div>
                )}
            </div>

            <div className="p-6 bg-surface/40 border-t border-white/5 rounded-b-2xl mb-6 mx-8">
                <div className="flex gap-4">
                    <input
                        value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()}
                        placeholder="Ask about matchups, order rotation, or what to avoid..."
                        className="flex-1 bg-background border border-white/10 rounded-xl px-4 py-3 text-sm font-medium focus:border-primary/50 outline-none transition-all placeholder:text-text/20"
                    />
                    <button
                        onClick={sendMessage}
                        disabled={isLoading}
                        className="bg-primary text-background px-8 rounded-xl font-black uppercase text-xs shadow-neon hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:scale-100"
                    >
                        Ask AI
                    </button>
                </div>
            </div>
        </div>
    );
};

const PostMatchChat = ({ matchId }: { matchId: string }) => {
    const [messages, setMessages] = useState([{ role: 'bot', text: 'Hello! I am CricAI. Ask me anything about the strategy, player impact, or turning points in this match!' }]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;
        const newMsgs = [...messages, { role: 'user', text: input }];
        setMessages(newMsgs);
        setInput('');
        setIsLoading(true);
        try {
            const res = await matchApi.chat(matchId, input);
            setMessages([...newMsgs, { role: 'bot', text: res.data.answer }]);
        } catch {
            setMessages([...newMsgs, { role: 'bot', text: 'Connection lost. Please try again later.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => { scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight); }, [messages]);

    return (
        <div className="flex flex-col h-[600px]">
            <div className="flex-1 overflow-y-auto p-8 space-y-6" ref={scrollRef}>
                {messages.map((m, i) => (
                    <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`flex gap-3 max-w-[85%] ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center border shrink-0 ${m.role === 'user' ? 'bg-primary border-primary' : 'bg-surface border-white/10'}`}>
                                {m.role === 'user' ? <TrendingUp className="w-4 h-4 text-background" /> : <Bot className="w-4 h-4 text-primary" />}
                            </div>
                            <div className={`p-4 rounded-2xl text-sm ${m.role === 'user' ? 'bg-primary text-background font-medium' : 'bg-surface/80 border border-white/5'}`}>
                                {m.text}
                            </div>
                        </div>
                    </div>
                ))}
                {isLoading && <div className="text-[10px] font-black uppercase tracking-widest text-primary animate-pulse ml-11">Analyzing Match Data...</div>}
            </div>
            <div className="p-6 bg-surface/40 border-t border-white/5">
                <div className="flex gap-4">
                    <input
                        value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()}
                        placeholder="Ask about strategy, impact, or specific players..."
                        className="flex-1 bg-background border border-white/10 rounded-xl px-4 py-3 text-sm focus:border-primary/50 outline-none transition-all"
                    />
                    <button onClick={sendMessage} className="bg-primary text-background px-6 rounded-xl font-black uppercase text-xs shadow-neon hover:scale-105 transition-transform">Ask</button>
                </div>
            </div>
        </div>
    );
};

const ScorecardTable = ({ batters }: { batters: any[] }) => (
    <table className="w-full text-left text-xs border-collapse">
        <thead>
            <tr className="text-[10px] font-black uppercase text-text/40 border-b border-white/5">
                <th className="px-6 py-4">Batting</th>
                <th className="px-3 py-4 text-center">R</th>
                <th className="px-3 py-4 text-center">B</th>
                <th className="px-3 py-4 text-center">4s</th>
                <th className="px-3 py-4 text-center">6s</th>
                <th className="px-3 py-4 text-center">SR</th>
            </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
            {batters?.map((p, i) => (
                <tr key={i} className="hover:bg-white/5 transition-colors">
                    <td className="px-6 py-4">
                        <div className="flex flex-col">
                            <span className="font-bold text-white">{p.name}</span>
                            <span className="text-[10px] opacity-40 italic">{p.out}</span>
                        </div>
                    </td>
                    <td className="px-3 py-4 text-center font-black">{p.runs}</td>
                    <td className="px-3 py-4 text-center opacity-70">{p.balls}</td>
                    <td className="px-3 py-4 text-center opacity-70">{p.fours}</td>
                    <td className="px-3 py-4 text-center opacity-70">{p.sixes}</td>
                    <td className="px-3 py-4 text-center font-bold text-accent">{p.sr.toFixed(1)}</td>
                </tr>
            ))}
        </tbody>
    </table>
);

const BowlingTable = ({ bowlers }: { bowlers: any[] }) => (
    <table className="w-full text-left text-xs border-collapse">
        <thead>
            <tr className="text-[10px] font-black uppercase text-text/40 border-b border-white/5">
                <th className="px-6 py-4">Bowling</th>
                <th className="px-3 py-4 text-center">O</th>
                <th className="px-3 py-4 text-center">M</th>
                <th className="px-3 py-4 text-center">R</th>
                <th className="px-3 py-4 text-center">W</th>
                <th className="px-3 py-4 text-center">ECON</th>
            </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
            {bowlers?.map((p, i) => (
                <tr key={i} className="hover:bg-white/5 transition-colors">
                    <td className="px-6 py-4 font-bold text-white">{p.name}</td>
                    <td className="px-3 py-4 text-center font-black">{p.overs}</td>
                    <td className="px-3 py-4 text-center opacity-70">{p.maidens}</td>
                    <td className="px-3 py-4 text-center font-black">{p.runs}</td>
                    <td className="px-3 py-4 text-center font-bold text-primary">{p.wickets}</td>
                    <td className="px-3 py-4 text-center font-bold text-accent">{p.econ.toFixed(2)}</td>
                </tr>
            ))}
        </tbody>
    </table>
);
