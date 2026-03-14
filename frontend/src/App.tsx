import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { MatchDetail } from './components/MatchDetail';
import { AnalyticsHub } from './components/AnalyticsHub';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, X, Bot, TrendingUp as TrendingUpIcon } from 'lucide-react';
import { matchApi } from './api';

const TrendingUp = TrendingUpIcon;

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedMatch, setSelectedMatch] = useState<string | null>(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [matches, setMatches] = useState<any[]>([]);

  useEffect(() => {
    matchApi.getMatches().then(res => setMatches(res.data.matches || [])).catch(console.error);
  }, []);

  return (
    <div className="bg-background min-h-screen text-text overflow-x-hidden font-inter selection:bg-primary selection:text-background relative">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

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
                {activeTab === 'dashboard' && <Dashboard onMatchClick={setSelectedMatch} matches={matches} />}
                {activeTab === 'match_center' && <MatchCenter onMatchClick={setSelectedMatch} matches={matches} />}
                {activeTab === 'stats' && <AnalyticsHub />}
                {activeTab === 'learning' && <AnalyticsHub />}

                {!['dashboard', 'match_center', 'stats', 'learning'].includes(activeTab) && (
                  <div className="flex flex-col items-center justify-center h-[60vh]">
                    <p className="text-2xl font-outfit opacity-30 italic">Module: {activeTab} coming soon...</p>
                  </div>
                )}
              </>
            )}
          </motion.div>
        </AnimatePresence>

        {/* AI Chat Slide-over */}
        <ChatPanel isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} matchId={selectedMatch || 'GENERIC'} />

        {/* Floating Chat Trigger */}
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setIsChatOpen(true)}
          className="fixed bottom-8 right-8 w-16 h-16 bg-primary text-background rounded-2xl flex items-center justify-center shadow-neon z-40"
        >
          <Bot className="w-8 h-8" />
        </motion.button>
      </main>
    </div>
  );
}

const Dashboard = ({ onMatchClick, matches }: { onMatchClick: (id: string) => void, matches: any[] }) => {
  // Sort matches by ID descending to get the latest matches for the dashboard
  const sortedByLatest = [...matches].sort((a, b) => parseInt(b.id) - parseInt(a.id));
  const recentMatches = sortedByLatest.slice(0, 2);
  
  return (
    <div className="space-y-10">
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          <h2 className="text-3xl font-outfit font-bold">Recommended for You</h2>
          <div className="flex flex-col gap-4">
            {recentMatches.map((m) => (
              <MatchCard key={m.id} id={m.id} match={m} onClick={() => onMatchClick(m.id)} />
            ))}
            {recentMatches.length === 0 && <div className="text-white/40 italic p-4">Loading matches...</div>}
          </div>
        </div>
      <div className="glass-card p-6 bg-primary/5 border-primary/20">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
          <TrendingUp className="text-primary w-5 h-5" /> AI Insight Pulse
        </h3>
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="flex gap-4 p-3 rounded-lg hover:bg-white/5 transition-colors cursor-pointer border border-transparent hover:border-white/5">
              <div className="w-2 h-10 bg-primary/20 rounded-full" />
              <div>
                <p className="text-xs text-text/50 font-bold uppercase">Milestone Alert</p>
                <p className="text-sm font-medium">Player needs 42 runs to reach 15,000 runs...</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
  );
};

const getFlagUrl = (name: string) => {
  const cleanStr = (s: string) => s?.replace(/['"]/g, '').trim().toLowerCase() || '';
  const n = cleanStr(name);
  const mapping: Record<string, string> = {
    'india': 'in',
    'pakistan': 'pk',
    'sri lanka': 'lk',
    'u.s.a.': 'us',
    'usa': 'us',
    'england': 'gb',
    'australia': 'au',
    'south africa': 'za',
    'new zealand': 'nz',
    'west indies': 'vg',
    'netherlands': 'nl',
    'afghanistan': 'af',
    'scotland': 'gb-sct',
    'bangladesh': 'bd'
  };
  const code = mapping[n] || 'un';
  return `https://flagcdn.com/w40/${code}.png`;
};

const MatchCard = ({ id, match, onClick }: any) => {
  const meta = match.metadata || {};
  const tsum = match.scores || tsum_from_meta(meta) || {};
  const teams = match.full_teams || [];
  const team1 = teams[0] || '';
  const team2 = teams[1] || '';
  
  function tsum_from_meta(m: any) {
    if (m.team_summary) return m.team_summary;
    return null;
  }

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
      whileHover={{ scale: 1.005, backgroundColor: 'rgba(255,255,255,0.05)' }}
      onClick={onClick}
      className="bg-surface/10 hover:bg-surface/20 border border-white/5 p-8 rounded-2xl cursor-pointer transition-all group flex flex-col md:flex-row items-center gap-8"
    >
      <div className="flex-1 w-full space-y-6">
        <div className="flex items-center justify-between text-[10px] font-black uppercase text-text/30 tracking-[0.2em]">
          <div className="flex items-center gap-3">
            <span className="text-primary/60">ID: {id}</span>
            <span className="opacity-20">|</span>
            <span>{clean(match.stage || 'League')}</span>
            <span className="opacity-20">|</span>
            <span>{match.venue}</span>
          </div>
          <span className="bg-primary/5 px-2 py-0.5 rounded text-primary/80">Result</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div className="space-y-4">
            <div className="flex items-center justify-between group-hover:translate-x-1 transition-transform">
              <div className="flex items-center gap-4">
                <img src={getFlagUrl(team1)} alt="" className="w-6 h-4 object-cover rounded shadow-sm" />
                <span className="font-outfit font-bold text-xl text-text/90 tracking-tight">{clean(team1)}</span>
              </div>
              <span className="font-outfit font-black text-xl tabular-nums">
                {team1Stats.total_runs ?? 0}/{team1Stats.total_wickets ?? 0}
              </span>
            </div>
            <div className="flex items-center justify-between group-hover:translate-x-1 transition-transform">
              <div className="flex items-center gap-4">
                <img src={getFlagUrl(team2)} alt="" className="w-6 h-4 object-cover rounded shadow-sm" />
                <span className="font-outfit font-bold text-xl text-text/90 tracking-tight">{clean(team2)}</span>
              </div>
              <div className="flex items-center gap-3">
                {team2Stats.run_rate && <span className="text-[10px] font-bold text-text/30">({team2Stats.run_rate} ov)</span>}
                <span className="font-outfit font-black text-xl tabular-nums">
                  {team2Stats.total_runs ?? 0}/{team2Stats.total_wickets ?? 0}
                </span>
              </div>
            </div>
          </div>
          
          <div className="md:border-l md:border-white/5 md:pl-12">
            <p className="text-base font-medium text-primary/70 italic leading-relaxed font-outfit">
              {formatResult()}
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

const MatchCenter = ({ onMatchClick, matches }: any) => {
  // Group matches by date while preserving order
  const dates: string[] = [];
  const groupedMatches: Record<string, any[]> = {};
  
  matches.forEach((m: any) => {
    const date = m.date || 'Unknown Date';
    if (!groupedMatches[date]) {
      groupedMatches[date] = [];
      dates.push(date);
    }
    groupedMatches[date].push(m);
  });

  return (
    <div className="max-w-6xl mx-auto space-y-16 pb-20">
      <div className="space-y-3 text-center md:text-left border-b border-white/5 pb-8">
        <h2 className="text-5xl font-outfit font-black tracking-tight text-white uppercase">ICC Men's T20 World Cup 2026</h2>
        <div className="flex items-center justify-center md:justify-start gap-4">
          <div className="h-px w-12 bg-primary/40" />
          <p className="text-primary font-bold uppercase tracking-[0.4em] text-xs">Schedule & Results</p>
        </div>
      </div>

      <div className="space-y-12">
        {dates.map((date) => (
          <div key={date} className="grid lg:grid-cols-[200px_1fr] gap-8">
            <div className="pt-4">
              <div className="sticky top-28 bg-surface/5 p-4 rounded-xl border border-white/5 backdrop-blur-sm">
                <p className="font-outfit font-black text-primary/60 uppercase tracking-widest text-xs mb-1">Match Day</p>
                <p className="font-outfit font-black text-text/90 text-lg tabular-nums">{date}</p>
              </div>
            </div>
            <div className="space-y-6">
              {groupedMatches[date].map((m: any) => (
                <MatchCard key={m.id} id={m.id} match={m} onClick={() => onMatchClick(m.id)} />
              ))}
            </div>
          </div>
        ))}
        {matches.length === 0 && (
          <div className="glass-card p-16 text-center border-dashed border-white/10 bg-white/[0.02]">
            <p className="text-white/30 font-medium italic text-lg">No matches found in the archive yet.</p>
          </div>
        )}
      </div>
    </div>
  );
};

const ChatPanel = ({ isOpen, onClose, matchId }: any) => {
  const [msgs, setMsgs] = useState([{ role: 'bot', text: 'Ask me anything about the analytics!' }]);
  const [input, setInput] = useState('');

  const send = async () => {
    if (!input) return;
    const newMsgs = [...msgs, { role: 'user', text: input }];
    setMsgs(newMsgs);
    setInput('');

    try {
      const res = await (matchApi as any).chat(matchId, input);
      setMsgs([...newMsgs, { role: 'bot', text: res.data.answer || 'Analysis complete.' }]);
    } catch {
      setMsgs([...newMsgs, { role: 'bot', text: 'Service unavailable.' }]);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          className="fixed right-0 top-0 h-screen w-[400px] bg-surface border-l border-white/10 z-[60] shadow-2xl flex flex-col font-inter"
        >
          <div className="p-6 border-b border-white/10 flex items-center justify-between bg-white/5">
            <div className="flex items-center gap-3">
              <Bot className="text-primary" />
              <h3 className="font-outfit font-bold">CricAI Assistant</h3>
            </div>
            <button onClick={onClose} className="p-1 hover:bg-white/10 rounded-lg"><X /></button>
          </div>
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {msgs.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-4 rounded-2xl text-sm ${m.role === 'user' ? 'bg-primary text-background font-medium' : 'bg-white/5 border border-white/10'}`}>
                  {m.text}
                </div>
              </div>
            ))}
          </div>
          <div className="p-6 border-t border-white/10 flex gap-2">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && send()}
              placeholder="Ask about strategy, player impact..."
              className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-primary"
            />
            <button onClick={send} className="bg-primary text-background p-2 rounded-xl active:scale-95 transition-all">
              <Send className="w-5 h-5" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default App;
