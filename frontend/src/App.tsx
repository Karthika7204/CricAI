import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { MatchDetail } from './components/MatchDetail';
import { IPLIntelligence } from './components/IPLIntelligence';
import { TrainingAssistant } from './components/TrainingAssistant';
import { motion, AnimatePresence, useMotionValue, useTransform } from 'framer-motion';
import {
  Send, X, Bot, TrendingUp as TrendingUpIcon, Search,
  PlayCircle, Sparkles, Dumbbell, ChevronRight, Activity,
  Target, Zap, LayoutDashboard, Bell
} from 'lucide-react';
import { matchApi } from './api';

const TrendingUp = TrendingUpIcon;

const DynamicBackground = () => {
  return (
    <div className="mesh-gradient">
      {/* Continuous Data Particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: '110%' }}
            animate={{
              opacity: [0, 0.7, 0],
              y: '-10%',
              x: `${Math.random() * 100}%`
            }}
            transition={{
              duration: 8 + Math.random() * 12,
              repeat: Infinity,
              delay: Math.random() * 8,
              ease: "linear"
            }}
            className="absolute w-[1.5px] h-24 bg-gradient-to-t from-transparent via-primary/40 to-transparent shadow-[0_0_15px_rgba(0,245,196,0.3)]"
          />
        ))}
      </div>

      <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-[0.03] pointer-events-none" />
    </div>
  );
};

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedMatch, setSelectedMatch] = useState<string | null>(null);
  const [matches, setMatches] = useState<any[]>([]);

  useEffect(() => {
    matchApi.getMatches().then(res => setMatches(res.data.matches || [])).catch(console.error);
  }, []);

  return (
    <div className="min-h-screen text-text overflow-x-hidden font-inter selection:bg-primary selection:text-background relative">
      <DynamicBackground />
      <Navbar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
          setSelectedMatch(null); // Reset detail view when navigating
        }}
      />

      <main className="max-w-[1600px] mx-auto pt-24 px-8 pb-20 relative min-h-screen">
        {/* Dynamic Content Area */}
        <AnimatePresence mode="wait">
          <motion.div
            key={selectedMatch || activeTab}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -20, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {selectedMatch ? (
              <MatchDetail matchId={selectedMatch} onBack={() => setSelectedMatch(null)} />
            ) : (
              <>
                {activeTab === 'dashboard' && <Dashboard onMatchClick={setSelectedMatch} matches={matches} onNavigate={setActiveTab} />}
                {activeTab === 'match_center' && <MatchCenter onMatchClick={setSelectedMatch} matches={matches} />}
                {activeTab === 'ipl_intelligence' && <IPLIntelligence />}
                {activeTab === 'training_assistant' && <TrainingAssistant />}

                {!['dashboard', 'match_center', 'ipl_intelligence', 'training_assistant'].includes(activeTab) && (
                  <div className="flex flex-col items-center justify-center h-[60vh]">
                    <p className="text-2xl font-outfit opacity-30 italic">Module: {activeTab} coming soon...</p>
                  </div>
                )}
              </>
            )}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}

const Dashboard = ({ onMatchClick, matches, onNavigate }: { onMatchClick: (id: string) => void, matches: any[], onNavigate: (tab: string) => void }) => {
  const sortedByLatest = [...matches].sort((a, b) => parseInt(b.id) - parseInt(a.id));
  const recentMatches = sortedByLatest.slice(0, 4);

  const portals = [
    {
      id: 'match_center',
      title: 'Match Center',
      desc: 'Real-time tactical flow & AI-powered turning points.',
      icon: PlayCircle,
      stats: '49 Matches Online',
      color: 'blue'
    },
    {
      id: 'ipl_intelligence',
      title: 'IPL Intelligence',
      desc: 'Deep historical archive & predictive season modeling.',
      icon: Sparkles,
      stats: '18 Seasons Mapped',
      color: 'purple'
    },
    {
      id: 'training_assistant',
      title: 'Coach AI',
      desc: 'Holographic player drills & genetic weakness detection.',
      icon: Dumbbell,
      stats: '840 Players Profiled',
      color: 'emerald'
    }
  ];

  return (
    <div className="space-y-12 animate-in fade-in duration-700">
      {/* Global Intelligence Ticker */}
      <div className="glass-card bg-surface/20 border-white/5 py-4 px-8 flex items-center gap-8 overflow-hidden relative">
        <div className="flex items-center gap-3 shrink-0 border-r border-white/10 pr-8">
          <Activity className="text-primary w-4 h-4" />
          <span className="text-[10px] font-black uppercase tracking-widest text-primary/60">Global Intelligence Stream</span>
        </div>
        <div className="flex gap-16 animate-infinite-scroll whitespace-nowrap">
          {[
            "RASHID KHAN DETECTED AT HIGH RISK IN AHMEDABAD",
            "DEW PREDICTION: 84% PROBABILITY FOR CHENNAI EVENING FIXTURES",
            "VIRAT KOHLI FORM METRIC: +12% MOMENTUM GAIN IN LAST 4 INNINGS",
            "SYSTEM ANALYSIS: SPIN-FRIENDLY CONDITIONS EXPECTED AT EKANA STADIUM",
            "PAR SCORE PREDICTION (MUMBAI): 208 RUNS FOR FIRST INNINGS",
            "FIELD ROTATION ALERT: PBKS TENDING TOWARDS AGGRESSIVE SLIP POSITIONING"
          ].map((text, i) => (
            <div key={i} className="flex items-center gap-4">
              <div className="w-1.5 h-1.5 bg-primary/40 rounded-full shadow-neon" />
              <span className="text-[10px] font-bold text-text/40 tracking-wider font-outfit uppercase italic">{text}</span>
            </div>
          ))}
        </div>
        <div className="absolute inset-y-0 left-[220px] w-20 bg-gradient-to-r from-background to-transparent z-10" />
        <div className="absolute inset-y-0 right-0 w-20 bg-gradient-to-l from-background to-transparent z-10" />
      </div>

      {/* Hero Portals Section */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {portals.map((p) => (
          <motion.div
            key={p.id}
            whileHover={{ y: -5, scale: 1.02 }}
            onClick={() => onNavigate(p.id)}
            className={`glass-card p-6 cursor-pointer group relative overflow-hidden bg-${p.color}-500/[0.02] border-${p.color}-500/10 hover:border-${p.color}-500/40 transition-all`}
          >
            <div className="relative z-10 flex flex-col h-full">
              <div className={`w-12 h-12 rounded-xl bg-${p.color}-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                <p.icon className={`w-6 h-6 text-${p.color}-500`} />
              </div>
              <h3 className="text-xl font-outfit font-black uppercase tracking-tight mb-2 group-hover:text-primary transition-colors">{p.title}</h3>
              <p className="text-xs text-text/40 leading-relaxed mb-6 flex-1">{p.desc}</p>
              <div className="flex items-center justify-between mt-auto pt-4 border-t border-white/5">
                <span className="text-[9px] font-black uppercase tracking-widest text-text/20 group-hover:text-text/40">{p.stats}</span>
                <ChevronRight className={`w-4 h-4 text-${p.color}-500/40 group-hover:text-${p.color}-500 group-hover:translate-x-1 transition-all`} />
              </div>
            </div>
            <div className={`absolute -bottom-6 -right-6 w-24 h-24 bg-${p.color}-500/5 rounded-full blur-2xl group-hover:bg-${p.color}-500/10 transition-all`} />
          </motion.div>
        ))}
      </section>

      {/* Main Intelligence Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 border-t border-white/5 pt-12">
        <div className="lg:col-span-8 space-y-8">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-outfit font-bold flex items-center gap-3">
              <TrendingUp className="text-primary w-6 h-6" />
              Recommended for You
            </h2>
            <button onClick={() => onNavigate('match_center')} className="text-[10px] font-black uppercase tracking-widest text-primary/40 hover:text-primary transition-colors">
              Explore All Matches →
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recentMatches.map((m) => (
              <div key={m.id} className="min-w-[300px]">
                <MatchCard id={m.id} match={m} onClick={() => onMatchClick(m.id)} />
              </div>
            ))}
            {recentMatches.length === 0 && (
              <div className="col-span-2 glass-card p-12 text-center border-dashed border-white/5 opacity-30">
                <LayoutDashboard className="w-12 h-12 mx-auto mb-4" />
                <p>Initializing Intelligence Stream...</p>
              </div>
            )}
          </div>
        </div>

        {/* Intelligence Pulse Sidebar */}
        <div className="lg:col-span-4 space-y-6">
          <div className="glass-card bg-surface/40 border-primary/10 overflow-hidden">
            <div className="p-6 border-b border-white/5 bg-primary/[0.02] flex items-center justify-between">
              <h3 className="text-sm font-black uppercase tracking-widest italic flex items-center gap-3">
                <div className="relative">
                  <Bot className="text-primary w-5 h-5" />
                  <div className="absolute -top-1 -right-1 w-2 h-2 bg-primary rounded-full animate-ping" />
                </div>
                AI Insight Pulse
              </h3>
              <Bell className="w-4 h-4 text-text/20" />
            </div>

            <div className="p-4 space-y-4 max-h-[500px] overflow-y-auto custom-scrollbar">
              {[
                { type: 'Strategic Alert', content: 'Heavy dew detected in Mumbai - Impacting 2nd innings bowling effectiveness.', icon: Zap, color: 'text-orange-500' },
                { type: 'Milestone Watch', content: 'Virat Kohli: 14 runs away from 12,000 T20 runs.', icon: Target, color: 'text-blue-500' },
                { type: 'Player Trend', content: 'Rashid Khan: Economy spike (9.2) in last 3 death-over spells.', icon: Activity, color: 'text-red-500' },
                { type: 'Squad Update', content: 'Intelligence indicates a potential order rotation for RCB in upcoming match.', icon: Sparkles, color: 'text-purple-500' }
              ].map((insight, i) => (
                <div key={i} className="flex gap-4 p-4 rounded-xl hover:bg-white/5 transition-all border border-transparent hover:border-white/5 group cursor-pointer">
                  <div className={`mt-0.5 p-2 rounded-lg bg-white/5 ${insight.color} group-hover:scale-110 transition-transform`}>
                    <insight.icon className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <p className={`text-[10px] font-black uppercase tracking-tighter ${insight.color}`}>{insight.type}</p>
                      <span className="text-[9px] text-text/20">• 2m ago</span>
                    </div>
                    <p className="text-[12px] font-medium text-text/80 leading-relaxed">{insight.content}</p>
                  </div>
                </div>
              ))}
            </div>

            <button className="w-full py-4 border-t border-white/5 text-[9px] font-black uppercase tracking-[0.3em] text-text/20 hover:text-primary hover:bg-primary/5 transition-all">
              Load Archive Intelligence
            </button>
          </div>

          <div className="glass-card p-4 flex items-center justify-between bg-surface/20 border-white/5">
            <span className="text-[9px] font-black uppercase tracking-widest text-text/30">System Status</span>
            <div className="flex items-center gap-2">
              <span className="text-[9px] font-black text-primary uppercase">Active</span>
              <div className="w-1.5 h-1.5 rounded-full bg-primary shadow-neon shadow-primary/40 animate-pulse" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

import { getFlagUrl } from './utils/flags';

const MatchCard = ({ id, match, onClick }: any) => {
  const meta = match.metadata || {};
  const tsum = match.scores || (meta.team_summary ? meta.team_summary : {});
  const teams = match.full_teams || [];
  const team1 = teams[0] || '';
  const team2 = teams[1] || '';

  const clean = (s: string) => s?.replace(/['"]/g, '').trim() || '';

  const getTeamStats = (name: string) => {
    const cleaned = clean(name).toLowerCase();
    const key = Object.keys(tsum).find(k => clean(k).toLowerCase() === cleaned);
    return key ? tsum[key] : {};
  };

  const team1Stats = getTeamStats(team1);
  const team2Stats = getTeamStats(team2);

  const formatResult = () => {
    if (!meta.winner) return 'Pending Result';
    const winner = clean(meta.winner);
    const margin = meta.margin_runs ? `${meta.margin_runs} runs` : `${meta.margin_wickets} wickets`;
    return `${winner} won by ${margin}`;
  };

  return (
    <motion.div
      whileHover={{ y: -2, scale: 1.005 }}
      onClick={onClick}
      className="group relative cursor-pointer"
    >
      <div className="glass-card overflow-hidden border-white/5 bg-surface/20 backdrop-blur-md group-hover:border-primary/20 transition-all duration-300">
        <div className="p-4 relative z-10">
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-text/40">
              <div className="flex items-center gap-2">
                <span className="bg-white/5 px-2 py-0.5 rounded border border-white/5">{id}</span>
                {id === '1512773' && <span className="text-accent font-black animate-pulse">• FINAL</span>}
                {id === '1512772' && <span className="text-primary font-black">• 2ND SEMIFINAL</span>}
                {id === '1512771' && <span className="text-primary font-black">• 1ST SEMIFINAL</span>}
                {match.tournament && (
                  <>
                    <span className="opacity-50">•</span>
                    <span>{match.tournament}</span>
                  </>
                )}
              </div>
              {match.status && (
                <div className={`flex items-center gap-1.5 ${match.status === 'Finalized' ? 'text-primary' : 'text-accent'}`}>
                  <div className={`w-1 h-1 rounded-full ${match.status === 'Finalized' ? 'bg-primary shadow-neon' : 'bg-accent animate-pulse'}`} />
                  {match.status}
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4 items-center">
              <div className="flex items-center gap-3">
                <img src={getFlagUrl(team1)} alt="" className="w-8 h-5 object-cover rounded shadow-sm opacity-80 group-hover:opacity-100 transition-opacity" />
                <span className="text-lg font-outfit font-black tracking-tight uppercase group-hover:text-primary transition-colors">{clean(team1)}</span>
              </div>
              <div className="text-right">
                <span className="text-lg font-outfit font-black tracking-tight uppercase">{team1Stats.total_runs ?? 0}/{team1Stats.total_wickets ?? 0}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 items-center">
              <div className="flex items-center gap-3">
                <img src={getFlagUrl(team2)} alt="" className="w-8 h-5 object-cover rounded shadow-sm opacity-80 group-hover:opacity-100 transition-opacity" />
                <span className="text-lg font-outfit font-black tracking-tight uppercase group-hover:text-primary transition-colors">{clean(team2)}</span>
              </div>
              <div className="text-right">
                <span className="text-lg font-outfit font-black tracking-tight uppercase">{team2Stats.total_runs ?? 0}/{team2Stats.total_wickets ?? 0}</span>
              </div>
            </div>

            <div className="flex items-center gap-3 text-[10px] font-bold text-text/20 uppercase tracking-widest border-t border-white/5 pt-3">
              <span className="flex-1 truncate">{match.venue}</span>
              <span className="text-primary/50">Result : {formatResult()}</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

const MatchCenter = ({ onMatchClick, matches }: any) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredMatches = matches.filter((m: any) => {
    const teams = m.full_teams || [];
    return teams.some((t: string) => t.toLowerCase().includes(searchTerm.toLowerCase()));
  });

  const dates: string[] = [];
  const groupedMatches: Record<string, any[]> = {};

  filteredMatches.forEach((m: any) => {
    const date = m.date || 'Unknown Date';
    if (!groupedMatches[date]) {
      groupedMatches[date] = [];
      dates.push(date);
    }
    groupedMatches[date].push(m);
  });

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-20">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 relative">
        <div className="space-y-2">
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-2">
            <div className="w-6 h-px bg-primary/40" />
            <p className="text-primary font-black uppercase tracking-[0.4em] text-[9px]">Match Archive</p>
          </motion.div>
          <motion.h2 className="text-5xl font-outfit font-black tracking-tight text-white uppercase italic">
            Match <span className="text-primary">Center</span>
          </motion.h2>
        </div>

        <div className="relative group w-full md:w-auto">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-primary/40 w-4 h-4" />
          <input
            type="text"
            placeholder="Search Matchups..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-white/[0.03] border border-white/10 rounded-xl py-3 pl-12 pr-6 w-full md:w-[300px] text-sm focus:outline-none focus:border-primary transition-all backdrop-blur-md"
          />
        </div>
      </div>

      <div className="space-y-12">
        {dates.map((date) => (
          <div key={date} className="space-y-4">
            <div className="flex items-center gap-4">
              <span className="px-3 py-1 bg-primary/10 border border-primary/20 rounded-md font-outfit font-black text-primary text-[10px] uppercase">{date}</span>
              <div className="h-px flex-1 bg-white/5" />
            </div>

            <div className="grid grid-cols-1 gap-3">
              {groupedMatches[date].map((m: any, idx: number) => (
                <motion.div
                  key={m.id}
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.05 }}
                >
                  <MatchCard id={m.id} match={m} onClick={() => onMatchClick(m.id)} />
                </motion.div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};


export default App;
