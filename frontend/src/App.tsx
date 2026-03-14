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
  const recentMatches = matches.slice(0, 2);
  
  return (
    <div className="space-y-10">
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          <h2 className="text-3xl font-outfit font-bold">Recommended for You</h2>
          <div className="grid grid-cols-2 gap-4">
            {recentMatches.map((m, i) => (
              <MatchCard key={m.id} id={m.id} teams={m.teams} status={i === 0 ? "Latest AI Insights" : "AI Analyzed"} onClick={() => onMatchClick(m.id)} />
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

const MatchCard = ({ id, teams, status, isLive, onClick }: any) => (
  <motion.div
    whileHover={{ y: -5 }}
    onClick={onClick}
    className="glass-card p-6 relative overflow-hidden group cursor-pointer font-inter"
  >
    {isLive && (
      <div className="absolute top-0 right-0 bg-accent text-background text-[10px] font-black px-4 py-1.5 uppercase skew-x-12 translate-x-3">
        Live
      </div>
    )}
    <div className="flex items-center justify-between mb-8">
      <div className="flex items-center gap-4">
        <div className="text-center">
          <div className="w-12 h-12 bg-white/5 rounded-full mb-2 flex items-center justify-center border border-white/10 group-hover:border-primary/50 transition-colors">
            <span className="text-xl font-black">{teams[0]}</span>
          </div>
        </div>
        <span className="text-xs font-bold text-text/30 italic">VS</span>
        <div className="text-center">
          <div className="w-12 h-12 bg-white/5 rounded-full mb-2 flex items-center justify-center border border-white/10 group-hover:border-primary/50 transition-colors">
            <span className="text-xl font-black">{teams[1]}</span>
          </div>
        </div>
      </div>
      <div className="text-right">
        <p className="text-[10px] font-bold tracking-widest text-text/40 uppercase mb-1">Match ID: {id}</p>
        <p className={`text-xs font-black uppercase ${isLive ? 'text-accent animate-pulse' : 'text-primary'}`}>{status}</p>
      </div>
    </div>

    <div className="flex items-center gap-2">
      <div className="flex-1 h-1 bg-white/5 rounded-full overflow-hidden">
        <motion.div initial={{ width: 0 }} animate={{ width: '66%' }} className="h-full bg-primary" />
      </div>
      <span className="text-[10px] font-bold text-text/40">AI Confidence: 88%</span>
    </div>
  </motion.div>
);

const MatchCenter = ({ onMatchClick, matches }: any) => (
  <div className="space-y-6">
    <h2 className="text-3xl font-outfit font-bold">Match Archive</h2>
    <div className="grid grid-cols-4 gap-4">
      {matches.map((m: any) => (
        <MatchCard key={m.id} id={m.id} teams={m.teams} status="Archived" onClick={() => onMatchClick(m.id)} />
      ))}
      {matches.length === 0 && <div className="col-span-4 text-white/40 p-4">Empty archive</div>}
    </div>
  </div>
);

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
