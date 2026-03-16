import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowLeft,
  Loader2,
  Cpu
} from 'lucide-react';
import { matchApi } from '../api';

export const TrainingAssistant = () => {
  const [teams, setTeams] = useState<string[]>([]);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [players, setPlayers] = useState<string[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState('');
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    matchApi.getTATeams().then(res => setTeams(res.data.teams)).catch(console.error);
  }, []);

  const handleTeamChange = async (team: string) => {
    setSelectedTeam(team);
    setSelectedPlayer('');
    setPlayers([]);
    if (team) {
      setLoading(true);
      try {
        const res = await matchApi.getTAPlayers(team);
        setPlayers(res.data.players);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleAnalyze = async () => {
    if (!selectedTeam || !selectedPlayer) return;
    setAnalyzing(true);
    setError('');
    try {
      const res = await matchApi.analyzePlayer(selectedTeam, selectedPlayer);
      // Artificial delay for scanning effect
      setTimeout(() => {
        setResult(res.data);
        setAnalyzing(false);
      }, 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.');
      setAnalyzing(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-12 px-4 relative z-10 min-h-screen">
      <AnimatePresence mode="wait">
        {!result && !analyzing ? (
          <motion.div 
            key="input"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05, filter: 'blur(10px)' }}
            className="max-w-2xl mx-auto"
          >
            <div className="glass-card p-12 border-primary/20 bg-surface/40 backdrop-blur-3xl relative overflow-hidden group">
              <div className="scanning-bar opacity-10 group-hover:opacity-30 transition-opacity" />
              
              <div className="text-center mb-12 relative z-10">
                <motion.div 
                  animate={{ rotate: [0, 10, -10, 0] }}
                  transition={{ duration: 5, repeat: Infinity }}
                  className="w-20 h-20 bg-primary/10 rounded-3xl flex items-center justify-center mx-auto mb-8 border border-primary/30 shadow-neon text-4xl"
                >
                  🏋️
                </motion.div>
                <h1 className="text-5xl font-outfit font-black uppercase tracking-tighter italic mb-3">
                  AI <span className="text-primary italic">Tactical</span> Coach
                </h1>
                <p className="text-text/40 text-sm font-medium tracking-wide">Syncing with real-time IPL database for holographic breakdown.</p>
              </div>

              {error && (
                <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="mb-8 p-4 bg-accent/10 border border-accent/30 rounded-2xl flex items-center gap-4 text-accent text-sm">
                  <span className="text-lg">⚠️</span>
                  {error}
                </motion.div>
              )}

              <div className="space-y-8 relative z-10">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <label className="text-[10px] font-black uppercase tracking-[0.3em] text-primary/60 flex items-center gap-2 px-1">
                      <span className="text-xs">🛡️</span> Target Entity
                    </label>
                    <div className="relative group/input">
                      <select 
                        value={selectedTeam}
                        onChange={(e) => handleTeamChange(e.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-2xl p-4 text-sm focus:outline-none focus:border-primary transition-all appearance-none cursor-pointer group-hover/input:border-white/20"
                      >
                        <option value="" className="bg-surface">Select Team</option>
                        {teams.map(t => <option key={t} value={t} className="bg-surface">{t}</option>)}
                      </select>
                      <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none opacity-20">▼</div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <label className="text-[10px] font-black uppercase tracking-[0.3em] text-primary/60 flex items-center gap-2 px-1">
                      <span className="text-xs">👤</span> Profile Identifier
                      {loading && <Loader2 className="w-3 h-3 animate-spin ml-auto" />}
                    </label>
                    <div className="relative group/input">
                      <select 
                        value={selectedPlayer}
                        onChange={(e) => setSelectedPlayer(e.target.value)}
                        disabled={!selectedTeam || loading}
                        className="w-full bg-white/5 border border-white/10 rounded-2xl p-4 text-sm focus:outline-none focus:border-primary transition-all appearance-none cursor-pointer disabled:opacity-30 group-hover/input:border-white/20"
                      >
                        <option value="" className="bg-surface">{!selectedTeam ? 'Awaiting Team...' : 'Select Player'}</option>
                        {players.map(p => <option key={p} value={p} className="bg-surface">{p}</option>)}
                      </select>
                      <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none opacity-20">▼</div>
                    </div>
                  </div>
                </div>

                <motion.button
                  whileHover={{ scale: 1.02, letterSpacing: '0.4em' }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleAnalyze}
                  disabled={!selectedTeam || !selectedPlayer || analyzing}
                  className="w-full bg-primary text-background font-black uppercase tracking-[0.3em] py-5 rounded-2xl shadow-neon flex items-center justify-center gap-3 disabled:opacity-30 transition-all relative overflow-hidden"
                >
                  <span className="text-xl">⚡</span>
                  Initialize Scanning
                </motion.button>
              </div>

              <div className="mt-16 flex items-center gap-8 opacity-20 group-hover:opacity-40 transition-opacity">
                 <div className="flex-1 h-px bg-gradient-to-r from-transparent to-white/20" />
                 <Cpu className="w-6 h-6" />
                 <div className="flex-1 h-px bg-gradient-to-l from-transparent to-white/20" />
              </div>
            </div>
          </motion.div>
        ) : analyzing ? (
          <ScanningPhase player={selectedPlayer} />
        ) : (
          <AnalysisResults key="results" result={result} onBack={() => setResult(null)} />
        )}
      </AnimatePresence>
    </div>
  );
};

const ScanningPhase = ({ player }: { player: string }) => (
  <motion.div 
    key="scanning"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    className="flex flex-col items-center justify-center h-[70vh] relative"
  >
    <div className="relative">
      <div className="w-64 h-64 border-2 border-primary/20 rounded-full animate-ping opacity-20" />
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.div 
          animate={{ scale: [1, 1.2, 1], rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity }}
          className="w-32 h-32 border-4 border-l-primary border-transparent rounded-full"
        />
      </div>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-5xl animate-pulse">📡</span>
      </div>
    </div>
    
    <div className="mt-12 text-center space-y-4">
      <h2 className="text-3xl font-outfit font-black uppercase tracking-widest italic animate-pulse">
        Scanning <span className="text-primary">{player}</span>
      </h2>
      <div className="w-64 h-2 bg-white/5 rounded-full overflow-hidden mx-auto">
        <motion.div 
          initial={{ x: '-100%' }}
          animate={{ x: '100%' }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
          className="w-full h-full bg-primary shadow-neon"
        />
      </div>
      <p className="text-[10px] font-black uppercase tracking-[0.5em] text-primary/40">Synchronizing Data Particles...</p>
    </div>

    <div className="absolute left-0 right-0 top-0 bottom-0 pointer-events-none">
       {[...Array(20)].map((_, i) => (
         <motion.div
           key={i}
           initial={{ opacity: 0, y: 100 }}
           animate={{ opacity: [0, 1, 0], y: -200, x: Math.random() * 400 - 200 }}
           transition={{ duration: 2, repeat: Infinity, delay: i * 0.1 }}
           className="absolute left-1/2 bottom-1/2 w-1 h-4 bg-primary/20 blur-[1px]"
         />
       ))}
    </div>
  </motion.div>
);

const AnalysisResults = ({ result, onBack }: { result: any, onBack: () => void }) => {
  const { player_name, team, stats, weaknesses, simulation, matchup } = result;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-10 animate-in fade-in duration-700 pb-20"
    >
      {/* 1. Header Card - Matching Image 1 */}
      <div className="glass-card p-10 border-white/5 bg-surface/90 backdrop-blur-xl relative overflow-hidden ring-1 ring-white/10 rounded-[2.5rem]">
        <div className="flex flex-col md:flex-row items-start gap-10">
          <div className="w-32 h-32 bg-slate-900/40 rounded-3xl border border-white/10 flex items-center justify-center shadow-2xl shrink-0">
             <div className="w-20 h-20 bg-primary/20 rounded-2xl flex items-center justify-center border border-primary/30 text-3xl">
                🏏
             </div>
          </div>
          <div className="flex-1 space-y-4">
            <h2 className="text-6xl font-outfit font-black uppercase tracking-tight italic text-white leading-none">{player_name}</h2>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-primary/10 border border-primary/20 rounded-full">
              <span className="text-xs">🛡️</span>
              <span className="text-[11px] font-black uppercase tracking-[0.2em] text-primary">{team}</span>
            </div>
            <p className="text-sm text-text/40 font-medium max-w-3xl leading-relaxed">
              Full AI analysis complete — weaknesses identified, training plan generated, matchup analyzed, and field setup recommended.
            </p>
          </div>
        </div>

        {/* 2. Stats Grid - Exactly 5 columns */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-6 mt-12">
          <StatBox label="Total Runs" value={stats.runs?.toFixed(1) || '0.0'} icon="🏃" />
          <StatBox label="Strike Rate" value={stats.strike_rate?.toFixed(1) || '0.0'} icon="⚡" />
          <StatBox label="Balls Faced" value={stats.balls || '0'} icon="🏏" />
          <StatBox label="Dot Ball %" value={(stats.dot_ball_pct || 0).toFixed(1) + '%'} icon="🔴" />
          <StatBox label="Weaknesses" value={weaknesses?.length || 0} icon="⚠️" />
        </div>
      </div>

      {/* 3. Mid Section: Weaknesses & Training - Matching Image 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Detected Weaknesses Card */}
        <div className="glass-card p-10 border-white/5 bg-surface rounded-[2.5rem] relative">
          <h3 className="text-sm font-black uppercase tracking-[0.3em] text-[#ff4a6e] flex items-center gap-4 mb-10">
            <div className="bg-[#ff4a6e]/20 p-2 rounded-lg">
              ⚠️
            </div>
            <div>
              <p className="leading-tight">Detected Weaknesses</p>
              <p className="text-[10px] opacity-40 lowercase tracking-normal font-medium">Areas needing improvement</p>
            </div>
          </h3>
          <div className="space-y-4">
            {weaknesses?.map((w: string, i: number) => (
              <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                key={i} 
                className="flex items-center gap-4 p-5 bg-white/[0.03] border border-white/5 rounded-2xl group hover:border-[#ff4a6e]/30 transition-all"
              >
                <div className="w-6 h-6 rounded-full bg-[#ff4a6e]/10 flex items-center justify-center border border-[#ff4a6e]/20 text-[10px]">
                  ❌
                </div>
                <p className="text-sm font-bold text-text/80">{w}</p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Training Techniques Card */}
        <div className="glass-card p-10 border-white/5 bg-surface rounded-[2.5rem] relative">
          <h3 className="text-sm font-black uppercase tracking-[0.3em] text-primary flex items-center gap-4 mb-10">
            <div className="bg-primary/20 p-2 rounded-lg text-lg">
              🏋️
            </div>
            <div>
              <p className="leading-tight">Training Techniques</p>
              <p className="text-[10px] opacity-40 lowercase tracking-normal font-medium">Personalized drills & exercises</p>
            </div>
          </h3>
          <div className="space-y-8 pl-2">
            {simulation?.training_plan?.map((plan: string, i: number) => (
              <div key={i} className="flex gap-6 group">
                <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-background font-black shadow-[0_0_20px_rgba(0,245,196,0.4)] shrink-0">
                  {i + 1}
                </div>
                <p className="text-sm font-bold text-text/90 pt-2 border-b border-white/5 pb-4 flex-1">{plan}</p>
              </div>
            ))}
          </div>
          <div className="mt-12 space-y-4">
             <p className="text-[10px] font-black uppercase tracking-widest text-text/40">Coach Tips</p>
             <div className="flex gap-4 items-center p-4">
                <span className="text-xl">💡</span>
                <p className="text-sm text-text/60 font-medium">
                  {simulation?.training_tips?.[0] || 'Maintain back-foot balance'}
                </p>
             </div>
          </div>
        </div>
      </div>

      {/* 4. Bottom Section: Matchup & Field Setup - Matching Image 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {matchup && (
          <div className="glass-card p-10 border-white/5 bg-surface rounded-[2.5rem]">
            <h3 className="text-sm font-black uppercase tracking-[0.3em] text-primary flex items-center gap-4 mb-10">
              <div className="bg-primary/20 p-2 rounded-lg text-lg">
                ⚡
              </div>
              <div>
                <p className="leading-tight">Matchup vs Bowler</p>
                <p className="text-[10px] opacity-40 lowercase tracking-normal font-medium">Danger bowler analysis</p>
              </div>
            </h3>
            <div className="bg-surface/80 rounded-[2.5rem] p-12 border border-white/5 relative mb-10">
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-accent/20 border border-accent/40 px-4 py-1.5 rounded-xl text-xs font-black text-accent tracking-widest z-10">VS</div>
              <div className="flex items-center justify-between gap-12 relative z-0">
                <div className="text-center flex-1">
                  <div className="w-20 h-20 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/10 relative text-2xl">
                    🏏
                  </div>
                  <p className="text-[10px] font-black uppercase text-text/30 tracking-widest mb-1">Batter</p>
                  <p className="text-xl font-black text-white">{player_name.split(' ').map((n:any) => n[0]).join('')}</p>
                </div>
                <div className="text-center flex-1">
                  <div className="w-20 h-20 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/10 relative text-2xl">
                    🎯
                  </div>
                  <p className="text-[10px] font-black uppercase text-text/30 tracking-widest mb-1">Bowler</p>
                  <p className="text-xl font-black text-accent truncate">{matchup.danger_bowler}</p>
                </div>
              </div>
            </div>
            <div className="space-y-4">
              <StatRow label="Dismissals" value={matchup.dismissals} icon="☠️" color="text-accent" />
              <StatRow label="SR vs Bowler" value={matchup.strike_rate?.toFixed(2) || '0.00'} icon="⏲️" color="text-primary" />
              <StatRow label="Vulnerability" value={matchup.dismissals > 3 ? "High Risk" : "Moderate Risk"} icon="⚠️" color="text-[#ff9f43]" />
            </div>
          </div>
        )}

        <div className="glass-card p-10 border-white/5 bg-surface rounded-[2.5rem]">
          <h3 className="text-sm font-black uppercase tracking-[0.3em] text-[#facc15] flex items-center gap-4 mb-10">
            <div className="bg-[#facc15]/20 p-2 rounded-lg text-lg">
              📍
            </div>
            <div>
              <p className="leading-tight">AI Field Setup</p>
              <p className="text-[10px] opacity-40 lowercase tracking-normal font-medium">Optimal fielding positions</p>
            </div>
          </h3>
          <div className="space-y-10">
             <div className="scale-110 py-6">
                <FieldDiagram />
             </div>
             <div className="space-y-3">
               {['Slip', 'Gully', 'Point', 'Deep Cover', 'Long Off'].map((pos) => (
                 <div key={pos} className="flex items-center gap-4 p-4 bg-white/[0.03] rounded-2xl border border-white/5 group hover:bg-white/5 transition-all">
                   <div className="w-2.5 h-2.5 rounded-full bg-[#facc15] shadow-[0_0_10px_#facc15]" />
                   <span className="text-xs font-bold text-text/70">{pos}</span>
                 </div>
               ))}
             </div>
          </div>
        </div>
      </div>

      {/* 5. Back Button at bottom center */}
      <div className="pt-20 flex justify-center">
         <motion.button
           whileHover={{ scale: 1.05 }}
           whileTap={{ scale: 0.95 }}
           onClick={onBack}
           className="px-10 py-4 bg-primary/10 border border-primary/20 rounded-2xl text-primary font-black uppercase text-xs tracking-[0.3em] flex items-center gap-3 hover:bg-primary/20 transition-all"
         >
           <ArrowLeft className="w-4 h-4" /> Analyze Another Player
         </motion.button>
      </div>
    </motion.div>
  );
};

const StatBox = ({ label, value, icon }: any) => (
  <div className="p-8 bg-surface/50 border border-white/5 rounded-3xl hover:border-primary/30 transition-all group relative overflow-hidden">
    <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
    <div className="flex flex-col items-center gap-6">
      <div className="text-2xl">{icon}</div>
      <div className="text-center">
        <p className="text-4xl font-outfit font-black text-primary tracking-tight mb-2">{value}</p>
        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-text/40">{label}</p>
      </div>
    </div>
  </div>
);

const StatRow = ({ label, value, icon, color }: any) => (
  <div className="flex items-center justify-between p-5 bg-white/[0.02] border border-white/5 rounded-2xl group hover:bg-white/[0.05] transition-all">
    <div className="flex items-center gap-4">
      <span className="text-lg opacity-40 group-hover:opacity-100 transition-opacity">{icon}</span>
      <span className="text-[10px] font-black uppercase tracking-widest text-text/40">{label}</span>
    </div>
    <span className={`text-sm font-black italic ${color}`}>{value}</span>
  </div>
);

const FieldDiagram = () => (
  <div className="relative aspect-square w-full max-w-[320px] mx-auto p-4 scale-110">
    <svg viewBox="0 0 280 280" className="w-full h-full drop-shadow-[0_0_40px_rgba(0,0,0,0.5)]">
      {/* Outer Boundary */}
      <circle cx="140" cy="140" r="130" fill="#04080c" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
      <circle cx="140" cy="140" r="100" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" strokeDasharray="4 4" />
      
      {/* Pitch Area */}
      <rect x="128" y="96" width="24" height="88" rx="2" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
      <text x="140" y="142" fill="rgba(0,245,196,0.2)" fontSize="10" fontWeight="900" transform="rotate(-90 140 140)" textAnchor="middle" className="uppercase tracking-[0.3em]">Pitch</text>
      
      {/* Wickets */}
      <g stroke="#facc15" strokeWidth="2.5" strokeLinecap="round">
        <line x1="132" y1="102" x2="148" y2="102" />
        <line x1="132" y1="178" x2="148" y2="178" />
        <g strokeWidth="1.5">
          <line x1="135" y1="98" x2="135" y2="102" />
          <line x1="140" y1="98" x2="140" y2="102" />
          <line x1="145" y1="98" x2="145" y2="102" />
          <line x1="135" y1="178" x2="135" y2="182" />
          <line x1="140" y1="178" x2="140" y2="182" />
          <line x1="145" y1="178" x2="145" y2="182" />
        </g>
      </g>
      
      {/* Fielding Positions - Matching img1 exactly */}
      {[
        {x: 155, y: 115, c: "#ff4a6e", l: "Slip", pos: 'right'},
        {x: 168, y: 138, c: "#ff9f43", l: "Gully", pos: 'right'},
        {x: 182, y: 172, c: "#7b61ff", l: "Cover", pos: 'right'},
        {x: 162, y: 198, c: "#54a0ff", l: "Mid-off", pos: 'right'},
        {x: 118, y: 198, c: "#54a0ff", l: "Mid-on", pos: 'left'},
        {x: 92, y: 148, c: "#facc15", l: "Sq. Leg", pos: 'left'},
        {x: 122, y: 242, c: "#00f5c4", l: "Fine Leg", pos: 'left'}
      ].map((dot, i) => (
        <g key={i}>
          <circle cx={dot.x} cy={dot.y} r="6" fill={dot.c} className="animate-pulse" />
          <text 
            x={dot.pos === 'right' ? dot.x + 12 : dot.x - 12} 
            y={dot.y + 4} 
            fill={dot.c} 
            fontSize="9" 
            fontWeight="bold" 
            textAnchor={dot.pos === 'right' ? "start" : "end"}
            className="uppercase font-outfit opacity-80"
          >
            {dot.l}
          </text>
        </g>
      ))}
    </svg>
  </div>
);
