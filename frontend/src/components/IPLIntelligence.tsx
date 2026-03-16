import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Cpu, Sparkles, Trophy, Users, User as UserIcon, 
  MapPin, Gavel, History, ChevronRight, Zap, 
  RotateCcw, Globe, Shield, Star
} from 'lucide-react';
import { SQUADS, H2H, PLAYERS, VENUES, CHAMPIONS, BAT_RECORDS, BOWL_RECORDS, TEAM_RECORDS } from '../data/iplData';

// --- Utility Functions ---

const getVenue = (sel: string) => {
  const keys = Object.keys(VENUES);
  for (let k of keys) {
    if (sel.includes(k.split(' ')[0]) || sel.includes(k.split(',')[0])) return { name: k, ...VENUES[k] };
  }
  return { name: sel, ...VENUES['Wankhede Stadium'] };
};

const fmt = (t: string) => {
  return t
    .replace(/### (.*)/g, '<h3 class="text-primary font-bebas text-2xl mt-4 mb-2">$1</h3>')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-bold">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="text-text/60 not-italic">$1</em>')
    .replace(/---/g, '<hr class="border-white/10 my-4 text-primary">')
    .replace(/^\|(.+)\|$/gm, (row) => {
      const cells = row.split('|').filter(c => c.trim());
      if (cells.every(c => /^[-: ]+$/.test(c.trim()))) return '';
      return '<div class="flex border-b border-white/5 last:border-0 py-2">' + 
        cells.map((c, i) => `<div class="flex-1 px-2 text-[11px] font-mono ${c.includes('★') || c.includes('%') || i === cells.length - 1 ? 'text-primary' : 'text-text/60'}">${c.trim()}</div>`).join('') + 
        '</div>';
    })
    .replace(/\n/g, '<br>');
};

// --- Demo Data Generators ---

const genFantasy = (t1: string, t2: string, venue: string, strat: string, cont: string) => {
  const sq1 = SQUADS[t1] || SQUADS['Mumbai Indians'];
  const sq2 = SQUADS[t2] || SQUADS['Chennai Super Kings'];
  const v = getVenue(venue);
  const isDiff = strat.includes('Differential');
  const isGL = cont.includes('Grand');

  const batters = [...sq1.bat.slice(0, 3), ...sq2.bat.slice(0, 3)];
  const ars = [...sq1.ar.slice(0, 2), ...sq2.ar.slice(0, 2)];
  const wks1 = sq1.wk[0], wks2 = sq2.wk[0];
  const cap = sq1.ar[0] || sq1.bat[0];
  const vc = sq2.bat[0];
  const diffCap = isDiff ? (sq1.bowl[0] || sq2.bowl[0]) : sq1.bat[1];

  return `### ⭐ FANTASY XI: ${t1} vs ${t2}\n**Venue:** ${v.name}, ${v.city} | **Strategy:** ${strat} | **${cont}**\n\n---\n\n### 🥊 WICKET-KEEPER\n**1. ${wks1} (${t1}) ★ SAFE PICK**\n${PLAYERS[wks1]?.note?.split('.')[0] || 'Consistent WK-batter, reliable floor pick'}. Avg ${PLAYERS[wks1]?.avg || 35}+.\n\n**2. ${wks2} (${t2}) ${isDiff ? '— DIFFERENTIAL OPTION' : ''}**\n${PLAYERS[wks2]?.note?.split('.')[0] || 'Wicket-keeper option from Team B'}. ${PLAYERS[wks2]?.s25 || 'In form this season'}.\n\n---\n\n### 🏏 BATTERS\n**3. ${batters[0]} (${t1}) ★★ TOP BATTER PICK**\n${PLAYERS[batters[0]]?.note?.split('.')[0] || 'In-form top-order batter'}. phase: ${PLAYERS[batters[0]]?.phase?.mid || 'Middle overs specialist'}.\n\n**4. ${batters[3] || batters[1]} (${t2})**\n${PLAYERS[batters[3]]?.note?.split('.')[0] || PLAYERS[batters[1]]?.note?.split('.')[0] || 'Consistent'}.\n\n---\n\n### 🏏 ALL-ROUNDERS\n**6. ${ars[0]} (${t1}) ★★ CAPTAIN PICK (${isGL ? 'GL' : 'Standard'})**\n${PLAYERS[ars[0]]?.note?.split('.')[0] || 'Key all-rounder'}. Bat + bowl double value.\n\n**7. ${ars[2] || ars[1]} (${t2})**\n${PLAYERS[ars[2]]?.note?.split('.')[0] || PLAYERS[ars[1]]?.note?.split('.')[0] || 'All-rounder value pick'}.\n\n---\n\n### 📊 CAPTAIN / VC STRATEGY\n| Role | Player | Team | Reason |\n|---|---|---|---|\n| **Captain** | ${cap} | ${t1} | Bat+bowl, highest pts ceiling |\n| **Vice-Captain** | ${vc} | ${t2} | In-form, safe floor |\n| **Diff Captain** | ${diffCap} | ${t1} | Low ownership high upside for GL |\n\n*CrickAI Fantasy Engine · IPL 2026*`;
};

const genMatch = (t1: string, t2: string, venue: string, mtype: string) => {
  const v = getVenue(venue);
  const k1 = `${t1}_${t2}`, k2 = `${t2}_${t1}`;
  const h2h = H2H[k1] || H2H[k2] || { t1w: 5, t2w: 5, total: 10, notable: 'New fixture' };
  const w1pct = Math.round((h2h.t1w / h2h.total) * 100) || 50;
  const w2pct = 100 - w1pct;

  return `### 🎯 MATCH PREDICTION: ${t1} vs ${t2}\n**${v.name} | ${mtype} | IPL 2026**\n\n---\n\n### 📊 WIN PROBABILITY\n**${t1}: ${w1pct}%**\n**${t2}: ${w2pct}%**\n\n### 🤝 HEAD-TO-HEAD\n| Metric | Value |\n|---|---|\n| Total Matches | ${h2h.total} |\n| Notable | ${h2h.notable} |\n\n### 🔑 KEY FACTORS\n**Venue:** ${v.name} — ${v.rec}\n**Pitch:** ${v.pitch} — Best for ${v.best.split(',')[0]}.\n\n**Predicted Score:** ${v.avg1 - 5} - ${v.avg1 + 10}\n\n*CrickAI Match Engine*`;
};

const genPlayer = (pName: string, cmpName: string, season: string) => {
  const pData = PLAYERS[pName];
  if (!pData) return `### 👤 ${pName} Analysis\nData not found. Try Live AI mode.`;
  const cmpData = cmpName ? PLAYERS[cmpName] : null;

  return `### 👤 ${pName} — IPL ANALYSIS\n**Team: ${pData.team}** | ${pData.role} | ${season}\n\n---\n\n### 📊 STATS\n| Metric | Value |\n|---|---|\n| Runs | ${pData.runs} |\n| Avg | ${pData.avg} |\n| SR | ${pData.sr} |\n| Wkts | ${pData.wkts} |\n\n**IPL 2025:** ${pData.s25}\n\n**Strength:** ${pData.note}\n\n${cmpData ? `### ⚖️ VS ${cmpName}\n${pName} (${pData.fant}/10) vs ${cmpName} (${cmpData.fant}/10)\n**Verdict:** ${pData.fant >= cmpData.fant ? pName : cmpName} edges it.` : ''}\n\n*CrickAI Player Engine*`;
};

const genTeam = (myTeam: string, opp: string, vtype: string, toss: string) => {
    const mySq = SQUADS[myTeam];
    const oppSq = SQUADS[opp];
    return `### 🛡️ STRATEGY: ${myTeam} vs ${opp}\n**IPL 2026 | ${vtype} | ${toss}**\n\n---\n\n### 🏏 BATTING ORDER\n1. ${mySq.bat[0]}\n2. ${mySq.wk[0]}\n3. ${mySq.bat[1]}\n4. ${mySq.ar[0]}\n\n### 🎳 BOWLING PLAN\n**Early:** ${mySq.bowl[0]} (2 ov)\n**Middle:** ${mySq.bowl[1]} + ${mySq.bowl[2]}\n**Death:** ${mySq.bowl[0]} (19, 21)\n\n**Threat:** ${oppSq.bat[0]} — Plan: ${PLAYERS[oppSq.bat[0]]?.weakV || 'varied'}\n\n*CrickAI Team Engine*`;
};

const genVenue = (venue: string, time: string) => {
    const v = getVenue(venue);
    return `### 🏟️ VENUE: ${v.name}\n**${v.city} | ${time}**\n\n---\n\n| Metric | Value |\n|---|---|\n| Avg 1st | ${v.avg1} |\n| Chase Win% | ${v.chase}% |\n| Dew | ${v.dew} |\n| Toss | ${v.toss} First |\n\n**Advice:** ${v.rec}\n\n*CrickAI Venue Engine*`;
};

const genAuction = (team: string, atype: string, role: string) => {
    return `### 💰 AUCTION INTEL: ${team}\n**Analysis: ${atype} | Role: ${role}**\n\n---\n\n### 💥 KEY BUYS\n**1. Rishabh Pant** — LSG — ₹27Cr (Record)\n**2. Cameron Green** — KKR — ₹25.2Cr\n**3. Prashant Veer** — CSK — ₹14.2Cr\n\n### 🏆 SQUAD STRENGTHS\n1. GT (9.3/10)\n2. MI (9.0/10)\n3. KKR (8.7/10)\n\n*CrickAI Auction Scout*`;
};

const genIPL26 = (ptype: string, depth: string) => {
    return `### 🔮 2026 PREDICTIONS: ${ptype}\n**Depth: ${depth}**\n\n---\n\n### 🏆 TITLE ODDS\n1. **Gujarat Titans** (26%)\n2. **Mumbai Indians** (21%)\n3. **KKR** (17%)\n\n**Winner Pick:** Gujarat Titans — Most balanced squad with Rashid + Gill.\n\n**Orange Cap:** Sai Sudharsan / Travis Head\n**Purple Cap:** Jasprit Bumrah\n\n*CrickAI Predictive Engine*`;
};

// --- Component ---

export const IPLIntelligence = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [apiKey, setApiKey] = useState(sessionStorage.getItem('cai_k') || '');
  const [isDemo, setIsDemo] = useState(!sessionStorage.getItem('cai_k'));
  const [showModal, setShowModal] = useState(!sessionStorage.getItem('cai_k'));
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<Record<string, { text: string; time: string; type: string }>>({});
  
  // Form States
  const [fantasyForm, setFantasyForm] = useState({ t1: 'Chennai Super Kings', t2: 'Mumbai Indians', venue: 'MA Chidambaram Stadium, Chennai', strat: 'Balanced (Safe)', cont: 'Grand League' });
  const [matchForm, setMatchForm] = useState({ t1: 'Chennai Super Kings', t2: 'Mumbai Indians', venue: 'MA Chidambaram Stadium, Chennai', type: 'League Stage' });
  const [playerForm, setPlayerForm] = useState({ player: 'Virat Kohli (RCB)', cmp: '', vs: 'All Teams', season: 'All Time (2008–2025)' });
  const [teamForm, setTeamForm] = useState({ team: 'Chennai Super Kings', opp: 'Mumbai Indians', vtype: 'Home Ground', toss: 'Not Decided' });
  const [venueForm, setVenueForm] = useState({ venue: 'MA Chidambaram Stadium, Chennai', teams: 'Any / General Analysis', time: 'Evening (7:30 PM)' });
  const [auctionForm, setAuctionForm] = useState({ team: 'All Teams', type: 'Value Picks & Hidden Gems', role: 'All Roles' });
  const [ipl26Form, setIpl26Form] = useState({ type: 'Season Champion', depth: 'Top 5 with full reasoning' });
  const [activeSquad, setActiveSquad] = useState(Object.keys(SQUADS)[0]);
  const [activeRec, setActiveRec] = useState('bat');
  
  const [queries, setQueries] = useState<Record<string, string>>({});

  const handleLaunch = (demo: boolean, key?: string) => {
    if (demo) {
      setIsDemo(true);
    } else if (key) {
      setApiKey(key);
      sessionStorage.setItem('cai_k', key);
      setIsDemo(false);
    }
    setShowModal(false);
  };

  const handleReset = () => {
    sessionStorage.removeItem('cai_k');
    setApiKey('');
    setIsDemo(true);
    setShowModal(true);
  };

  const analyze = async (page: string) => {
    const q = queries[page]?.trim();
    if (!q) return;

    setIsLoading(true);
    const t0 = Date.now();

    if (isDemo) {
      await new Promise(r => setTimeout(r, 1500 + Math.random() * 500));
      
      let response = '';
      if (page === 'fantasy') response = genFantasy(fantasyForm.t1, fantasyForm.t2, fantasyForm.venue, fantasyForm.strat, fantasyForm.cont);
      else if (page === 'match') response = genMatch(matchForm.t1, matchForm.t2, matchForm.venue, matchForm.type);
      else if (page === 'player') response = genPlayer(playerForm.player.split(' (')[0], playerForm.cmp.split(' (')[0], playerForm.season);
      else if (page === 'team') response = genTeam(teamForm.team, teamForm.opp, teamForm.vtype, teamForm.toss);
      else if (page === 'venue') response = genVenue(venueForm.venue, venueForm.time);
      else if (page === 'auction') response = genAuction(auctionForm.team, auctionForm.type, auctionForm.role);
      else if (page === 'ipl26') response = genIPL26(ipl26Form.type, ipl26Form.depth);
      else response = `### DEMO ANALYSIS: ${page.toUpperCase()}\n\n*Using Static Data Engine*\n\nThis is a data-driven simulation of the ${page} analysis. In Live AI mode, this is processed by Claude-3.5-Sonnet.`;
      
      setResults(prev => ({ ...prev, [page]: { text: response, time: `${((Date.now() - t0) / 1000).toFixed(1)}s`, type: 'DEMO' } }));
      setIsLoading(false);
      return;
    }

    // Live API Logic
    try {
        const ctx = buildCtx(page);
        const resp = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': apiKey,
                'anthropic-version': '2023-06-01',
                'anthropic-dangerous-direct-browser-access': 'true'
            },
            body: JSON.stringify({
                model: 'claude-3-5-sonnet-20240620',
                max_tokens: 2000,
                system: buildSys(),
                messages: [{ role: 'user', content: `CONTEXT:\n${ctx}\n\nQUERY: ${q}` }]
            })
        });

        if (!resp.ok) {
            const e = await resp.json();
            throw new Error(e.error?.message || 'API error ' + resp.status);
        }
        
        const data = await resp.json();
        setResults(prev => ({ 
            ...prev, 
            [page]: { 
                text: data.content?.[0]?.text || 'No response.', 
                time: `${((Date.now() - t0) / 1000).toFixed(1)}s`, 
                type: 'Live AI' 
            } 
        }));
    } catch (e: any) {
        setResults(prev => ({ ...prev, [page]: { text: `⚠️ Error: ${e.message}`, time: '0s', type: 'ERROR' } }));
    } finally {
        setIsLoading(false);
    }
  };

  const buildCtx = (page: string) => {
    switch(page) {
        case 'fantasy': return `Match: ${fantasyForm.t1} vs ${fantasyForm.t2} | Venue: ${fantasyForm.venue} | Strategy: ${fantasyForm.strat} | Contest: ${fantasyForm.cont}`;
        case 'match': return `${matchForm.t1} vs ${matchForm.t2} | Venue: ${matchForm.venue} | Type: ${matchForm.type}`;
        case 'player': return `Player: ${playerForm.player} | Compare: ${playerForm.cmp || 'None'} | vs: ${playerForm.vs} | Season: ${playerForm.season}`;
        case 'team': return `${teamForm.team} vs ${teamForm.opp} | ${teamForm.vtype} | Toss: ${teamForm.toss}`;
        case 'venue': return `Venue: ${venueForm.venue} | Teams: ${venueForm.teams} | Time: ${venueForm.time}`;
        case 'auction': return `Team: ${auctionForm.team} | Type: ${auctionForm.type} | Role: ${auctionForm.role}`;
        case 'ipl26': return `Type: ${ipl26Form.type} | Depth: ${ipl26Form.depth}`;
        default: return '';
    }
  };

  const buildSys = () => {
    return `You are CrickAI, the world's most advanced IPL intelligence system. 18 seasons (2008–2025) plus full IPL 2026 squads. 
            IPL 2025 Champ: RCB. Orange Cap: Sai Sudharsan. Purple: Prasidh Krishna. 
            Pant ₹27Cr to LSG. Green ₹25.2Cr to KKR. 
            Provide deep, data-driven analysis for the user query.`;
  };

  const renderModuleHeader = (title: string, engine: string, icon: React.ReactNode) => (
    <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-white/5 pb-6 mb-8 gap-4">
        <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center text-primary border border-primary/20 shadow-neon">
                {icon}
            </div>
            <div>
                <h2 className="font-outfit font-black text-3xl tracking-tighter text-white italic uppercase leading-none">{title}</h2>
                <div className="flex items-center gap-3 mt-1.5">
                    <div className="flex items-center gap-1.5 px-2 py-0.5 bg-green-500/10 rounded text-[9px] font-black uppercase tracking-widest text-green-500">
                      <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                      Protocol Active
                    </div>
                    <span className="text-[10px] text-text/30 font-mono tracking-widest uppercase">Engine: {engine}</span>
                </div>
            </div>
        </div>
        <div className="flex items-center gap-2">
            <div className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-[10px] text-text/40 font-mono tracking-wider uppercase font-black">Cluster: 03-Nexus</div>
            <div className="px-3 py-1.5 bg-primary/5 border border-primary/20 rounded-lg text-[10px] text-primary/60 font-mono tracking-wider uppercase font-black">Safe Protocol</div>
        </div>
    </div>
  );

  const renderModuleShell = (id: string, title: string, engine: string, icon: React.ReactNode, form: React.ReactNode, buttons: string[]) => (
    <div className="space-y-8">
        {renderModuleHeader(title, engine, icon)}
        
        <div className="glass-card border-white/5 bg-white/5 p-6 md:p-8 rounded-3xl">
          <div className="text-[10px] font-black text-text/20 uppercase tracking-[0.3em] mb-6 flex items-center justify-between">
            <span>Input Parameters</span>
            <span className="font-mono">SYS.REQ_INTEL</span>
          </div>
          {form}
          
          <div className="space-y-4">
            <p className="text-[10px] font-black uppercase tracking-[0.3em] text-text/20">Query Presets</p>
            <div className="flex flex-wrap gap-2">
                {buttons.map(q => (
                    <button 
                        key={q}
                        onClick={() => setQueries({...queries, [id]: q})}
                        className="px-4 py-2 bg-white/5 border border-white/5 hover:border-primary/30 rounded-xl text-[10px] font-black uppercase tracking-widest text-text/40 hover:text-primary transition-all"
                    >
                        {q}
                    </button>
                ))}
            </div>
          </div>
        </div>

        <div className="relative group">
          <div className="absolute -inset-1 bg-primary/20 rounded-3xl blur opacity-0 group-focus-within:opacity-100 transition-opacity" />
          <textarea 
              placeholder="Inject custom query or use preset protocols above..."
              value={queries[id] || ''}
              onChange={e => setQueries({...queries, [id]: e.target.value})}
              className="relative w-full h-32 bg-surface border border-white/10 rounded-3xl px-8 py-6 text-sm focus:border-primary/50 outline-none resize-none font-medium text-text placeholder:text-text/20 tracking-wide"
          />
        </div>

        <div className="flex items-center justify-between pt-2">
            <button 
                onClick={() => analyze(id)}
                disabled={isLoading}
                className="bg-primary text-background font-black uppercase tracking-[0.2em] px-10 py-4 rounded-2xl flex items-center gap-3 hover:scale-[1.02] active:scale-[0.98] transition-all shadow-neon disabled:opacity-50 disabled:scale-100"
            >
                {isLoading ? <RotateCcw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4 fill-current" />}
                {isLoading ? 'Processing Signal...' : `Initialize Analysis`}
            </button>
            <div className="hidden md:flex flex-col items-end gap-1">
              <div className="text-[10px] text-text/20 font-black tracking-widest uppercase">Neural Link Established</div>
              <div className="text-[9px] text-primary/40 font-mono uppercase">Node: Sonnet-3-5.v2</div>
            </div>
        </div>

        {results[id] && (
            <div className="mt-12 group animate-in slide-in-from-bottom-8 duration-700">
                <div className="glass-card border-primary/20 bg-surface/40 rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(102,252,241,0.05)]">
                    <div className="px-8 py-4 border-b border-white/5 bg-white/5 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <span className="px-3 py-1 bg-primary/10 text-primary rounded-lg text-[10px] font-black uppercase tracking-[0.3em] border border-primary/20">Stream Output</span>
                            <span className="text-[11px] text-text/40 font-mono tracking-widest">TIME_SYNC: {results[id].time}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                          <span className="text-[10px] text-text/20 font-black tracking-widest uppercase">{results[id].type} MODE</span>
                        </div>
                    </div>
                    <div className="p-10 prose prose-invert prose-sm max-w-none result-content selection:bg-primary/30" dangerouslySetInnerHTML={{ __html: fmt(results[id].text) }} />
                </div>
            </div>
        )}
    </div>
  );

  const renderHome = () => (
    <div className="space-y-6 pb-12 h-full flex flex-col">
      <div className="relative overflow-hidden glass-card border-white/10 bg-surface/40 p-10 lg:p-16 flex-1 rounded-[2.5rem] flex flex-col justify-center">
        <div className="absolute top-0 right-0 w-full h-full bg-[radial-gradient(circle_at_top_right,rgba(102,252,241,0.05),transparent)] pointer-events-none" />
        <div className="relative z-10 max-w-4xl">
          <div className="flex items-center gap-3 text-primary font-mono text-[10px] font-black uppercase tracking-[0.5em] mb-6">
            <Sparkles className="w-4 h-4" />
            <span>Multi-Model AI Synchronization Protocol</span>
          </div>
          <h1 className="font-outfit font-black text-6xl lg:text-8xl uppercase tracking-tighter italic leading-[0.85] mb-8 terminal-glow">
            IPL <span className="text-primary">2026</span><br />INTELLIGENCE
          </h1>
          <p className="text-text/50 text-xl leading-relaxed mb-12 max-w-2xl font-medium">
            Unified command interface for deep IPL forensics. 18 seasons of match telemetry powering 8 specialized intelligence modules. 
            Initiate protocol below to start analysis.
          </p>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-12">
            {[
              { val: '1,100+', label: 'DATA NODES' },
              { val: '300+', label: 'ENTITIES' },
              { val: '10', label: 'UNITS 2026' },
              { val: '8', label: 'AI CORES' }
            ].map((stat, i) => (
              <div key={i} className="space-y-1">
                <div className="text-4xl font-outfit font-black text-white italic tracking-tighter leading-none">{stat.val}</div>
                <div className="text-[9px] text-primary/40 uppercase font-black tracking-[0.3em]">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          { id: 'fantasy', title: 'Optimizer', desc: 'Squad probability matching.', icon: <Star />, color: 'shadow-[0_0_30px_rgba(255,184,0,0.1)] border-yellow-500/20' },
          { id: 'match', title: 'Predictor', desc: 'Predictive win modelling.', icon: <Zap />, color: 'shadow-[0_0_30px_rgba(102,252,241,0.1)] border-primary/20' },
          { id: 'player', title: 'Forensics', desc: 'Entity capability mapping.', icon: <UserIcon />, color: 'shadow-[0_0_30px_rgba(168,85,247,0.1)] border-purple-500/20' },
          { id: 'team', title: 'Tactics', desc: 'Unit deployment planning.', icon: <Shield />, color: 'shadow-[0_0_30px_rgba(34,197,94,0.1)] border-green-500/20' },
          { id: 'venue', title: 'Sectors', desc: 'Geospatial sector analysis.', icon: <MapPin />, color: 'shadow-[0_0_30px_rgba(249,115,22,0.1)] border-orange-500/20' },
          { id: 'ipl26', title: 'Forecast', desc: 'Deep horizon projections.', icon: <Globe />, color: 'shadow-[0_0_30px_rgba(6,182,212,0.1)] border-cyan-500/20' }
        ].map((mod) => (
          <button
            key={mod.id}
            onClick={() => setActiveTab(mod.id)}
            className={`group relative bg-surface/30 border border-white/5 hover:border-primary/40 rounded-3xl p-8 text-left transition-all hover:-translate-y-2 ${mod.color}`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center group-hover:bg-primary/10 transition-colors text-text/40 group-hover:text-primary border border-white/5 group-hover:border-primary/20">
                {React.isValidElement(mod.icon) ? React.cloneElement(mod.icon as any, { className: 'w-6 h-6' }) : mod.icon}
              </div>
              <ChevronRight className="w-5 h-5 text-text/10 group-hover:text-primary transition-all translate-x-0 group-hover:translate-x-1" />
            </div>
            <h3 className="font-black text-xl mb-1 uppercase tracking-tighter text-white italic">{mod.title}</h3>
            <p className="text-text/30 text-[11px] font-black uppercase tracking-widest">{mod.desc}</p>
          </button>
        ))}
      </div>
    </div>
  );

    const renderSquads = () => {
        const codes = Object.keys(SQUADS);

        return (
            <div className="space-y-10 animate-in fade-in duration-700">
                <div className="flex items-center gap-4 mb-10">
                    <div className="w-1.5 h-10 bg-primary" />
                    <div>
                        <h2 className="text-4xl font-outfit font-black uppercase italic tracking-tighter">ROSTER MANIFEST</h2>
                        <p className="text-text/30 text-[10px] font-black uppercase tracking-[0.3em]">Operational units for the 2026 cycle</p>
                    </div>
                </div>

                <div className="flex flex-wrap gap-2 mb-8 p-1.5 bg-white/5 rounded-2xl border border-white/5">
                    {codes.map(team => (
                        <button
                            key={team}
                            onClick={() => setActiveSquad(team)}
                            className={`px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${
                                activeSquad === team ? 'bg-primary text-background shadow-neon' : 'text-text/40 hover:text-white hover:bg-white/5'
                            }`}
                        >
                            {team.split(' ').map(w => w[0]).join('')}
                        </button>
                    ))}
                </div>

                <AnimatePresence mode="wait">
                    <motion.div
                        key={activeSquad}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="glass-card border-white/5 bg-white/5 rounded-3xl p-10 relative overflow-hidden"
                    >
                        <div className="absolute top-0 right-0 p-8">
                          <span className="text-[9px] font-mono text-text/10 uppercase tracking-[0.5em]">AUTH.STAMP_SECURE</span>
                        </div>
                        
                        <div className="flex items-center gap-6 mb-12">
                            <div className="w-2 h-16 rounded-full shadow-[0_0_20px_currentColor]" style={{ backgroundColor: SQUADS[activeSquad].color, color: SQUADS[activeSquad].color }} />
                            <div>
                                <h3 className="text-4xl font-black uppercase italic tracking-tighter text-white">{activeSquad}</h3>
                                <div className="flex items-center gap-4 mt-2">
                                  <div className="px-3 py-1 bg-white/5 rounded text-[10px] font-black uppercase tracking-widest text-text/40">
                                    Commander: <span className="text-primary font-black ml-1 text-xs">{SQUADS[activeSquad].cap}</span>
                                  </div>
                                  <div className="px-3 py-1 bg-white/5 rounded text-[10px] font-black uppercase tracking-widest text-text/40">
                                    Foreign Assets: <span className="text-white ml-1">{SQUADS[activeSquad].overseas.length}</span>
                                  </div>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                            {[
                                { label: 'Heavy Batters', data: SQUADS[activeSquad].bat },
                                { label: 'Keepers', data: SQUADS[activeSquad].wk },
                                { label: 'Tactical Hybrids', data: SQUADS[activeSquad].ar },
                                { label: 'Strike Units', data: SQUADS[activeSquad].bowl }
                            ].map(group => group.data.length > 0 && (
                                <div key={group.label} className="space-y-6">
                                    <h4 className="text-[10px] font-black text-primary/40 uppercase tracking-[0.4em] px-1">{group.label}</h4>
                                    <div className="space-y-2">
                                        {group.data.map((player: string) => (
                                            <div key={player} className="group flex items-center justify-between p-3 bg-white/5 hover:bg-white/10 rounded-xl transition-all border border-transparent hover:border-white/10">
                                                <span className="text-xs font-bold text-text/70 group-hover:text-white transition-colors uppercase tracking-tight">{player}</span>
                                                {SQUADS[activeSquad].overseas.includes(player) ? (
                                                  <Globe className="w-3 h-3 text-primary animate-pulse" />
                                                ) : (
                                                  <div className="w-1 h-1 rounded-full bg-white/10" />
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </motion.div>
                </AnimatePresence>
            </div>
        );
    };

    const renderChampionsView = () => (
        <div className="space-y-10">
            <div className="flex items-center gap-4 mb-10">
                <div className="w-1.5 h-10 bg-yellow-500" />
                <div>
                    <h2 className="text-4xl font-outfit font-black uppercase italic tracking-tighter">HALL OF HONOR</h2>
                    <p className="text-text/30 text-[10px] font-black uppercase tracking-[0.3em]">Historical Archive (2008–2025)</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {CHAMPIONS.map((c, i) => (
                    <motion.div
                        key={c.y}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.03 }}
                        className="glass-card border-white/5 bg-white/5 p-8 hover:border-yellow-500/30 transition-all group relative overflow-hidden"
                    >
                        <div className="absolute top-0 right-0 w-24 h-24 bg-yellow-500/5 blur-2xl rounded-full translate-x-12 -translate-y-12" />
                        <div className="flex items-center justify-between mb-6">
                            <span className="text-3xl font-black text-yellow-500 italic tracking-tighter">{c.y}</span>
                            <Trophy className="w-6 h-6 text-yellow-500/20 group-hover:text-yellow-500 transition-all group-hover:scale-110" />
                        </div>
                        <div className="space-y-4">
                            <div className="flex items-center gap-4">
                                <span className="text-[10px] font-black uppercase tracking-widest text-text/20">Victor</span>
                                <span className="text-xl font-black uppercase italic text-white">{c.w}</span>
                            </div>
                            <div className="flex items-center gap-4">
                                <span className="text-[10px] font-black uppercase tracking-widest text-text/20">Runner</span>
                                <span className="text-sm font-bold text-text/40">{c.r}</span>
                            </div>
                            <div className="mt-6 pt-6 border-t border-white/5">
                                <span className="text-[11px] italic font-medium text-yellow-500/50 leading-relaxed block">{c.n}</span>
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );

    const renderRecordsView = () => {

        return (
            <div className="space-y-10">
                <div className="flex items-center gap-4 mb-10">
                    <div className="w-1.5 h-10 bg-primary" />
                    <div>
                        <h2 className="text-4xl font-outfit font-black uppercase italic tracking-tighter">DATA ARCHIVES</h2>
                        <p className="text-text/30 text-[10px] font-black uppercase tracking-[0.3em]">Universal baseline metrics (2008–2025)</p>
                    </div>
                </div>

                <div className="flex gap-2 p-1.5 bg-white/5 rounded-2xl border border-white/5 w-fit">
                    {[
                        { id: 'bat', label: 'Offensive' },
                        { id: 'bowl', label: 'Defensive' },
                        { id: 'team', label: 'Unit Group' }
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveRec(tab.id)}
                            className={`px-8 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${
                                activeRec === tab.id ? 'bg-primary text-background shadow-neon' : 'text-text/40 hover:text-white'
                            }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                <div className="glass-card border-white/5 bg-white/2 rounded-3xl overflow-hidden shadow-2xl">
                    {activeRec === 'bat' && (
                        <table className="w-full text-left">
                            <thead>
                                <tr className="text-primary/40 text-[9px] font-black uppercase tracking-[0.3em] border-b border-white/5 bg-white/5">
                                    <th className="py-5 px-8">Entity</th>
                                    <th className="py-5 px-6">Affiliation</th>
                                    <th className="py-5 px-6">Score</th>
                                    <th className="py-5 px-6">Factor</th>
                                    <th className="py-5 px-6">Velocity</th>
                                    <th className="py-5 px-8">Thresholds</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {BAT_RECORDS.map((r, i) => (
                                    <tr key={i} className="hover:bg-primary/5 transition-colors group">
                                        <td className="py-5 px-8">
                                            <div className="font-black text-white group-hover:text-primary transition-colors uppercase italic tracking-tighter">{r.p}</div>
                                        </td>
                                        <td className="py-5 px-6 text-[10px] font-black text-text/30 uppercase tracking-widest">{r.t}</td>
                                        <td className="py-5 px-6 font-outfit font-black text-2xl italic tracking-tighter text-white">{r.r}</td>
                                        <td className="py-5 px-6 text-[11px] font-mono font-bold text-text/40">{r.a}</td>
                                        <td className="py-5 px-6 text-[11px] font-mono font-bold text-primary/60">{r.s}</td>
                                        <td className="py-5 px-8">
                                            <span className="text-[10px] font-black bg-white/5 px-3 py-1 rounded-lg border border-white/10 uppercase tracking-widest">
                                                {r.h}H / {r.f}F
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}

                    {activeRec === 'bowl' && (
                        <table className="w-full text-left">
                            <thead>
                                <tr className="text-primary/40 text-[9px] font-black uppercase tracking-[0.3em] border-b border-white/5 bg-white/5">
                                    <th className="py-5 px-8">Entity</th>
                                    <th className="py-5 px-6">Affiliation</th>
                                    <th className="py-5 px-6">Neutralized</th>
                                    <th className="py-5 px-6">Efficiency</th>
                                    <th className="py-5 px-6">Factor</th>
                                    <th className="py-5 px-8">Peak Output</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {BOWL_RECORDS.map((r, i) => (
                                    <tr key={i} className="hover:bg-primary/5 transition-colors group">
                                        <td className="py-5 px-8 font-black text-white group-hover:text-primary transition-colors uppercase italic tracking-tighter">{r.p}</td>
                                        <td className="py-5 px-6 text-[10px] font-black text-text/30 uppercase tracking-widest">{r.t}</td>
                                        <td className="py-5 px-6 font-outfit font-black text-2xl italic tracking-tighter text-white">{r.w}</td>
                                        <td className="py-5 px-6 text-[11px] font-mono font-bold text-text/40">{r.e}</td>
                                        <td className="py-5 px-6 text-[11px] font-mono font-bold text-text/40">{r.a}</td>
                                        <td className="py-5 px-8 text-[11px] font-mono font-black text-primary/60">{r.b}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}

                    {activeRec === 'team' && (
                        <table className="w-full text-left">
                            <thead>
                                <tr className="text-primary/40 text-[9px] font-black uppercase tracking-[0.3em] border-b border-white/5 bg-white/5">
                                    <th className="py-5 px-8">Protocol</th>
                                    <th className="py-5 px-8">Subject</th>
                                    <th className="py-5 px-6">Metric</th>
                                    <th className="py-5 px-8">Cycle</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {TEAM_RECORDS.map((r, i) => (
                                    <tr key={i} className="hover:bg-primary/5 transition-colors group">
                                        <td className="py-5 px-8 text-[11px] font-black text-text/30 uppercase tracking-widest">{r.r}</td>
                                        <td className="py-5 px-8 font-black text-white group-hover:text-primary transition-colors uppercase italic tracking-tighter">{r.t}</td>
                                        <td className="py-5 px-6 font-outfit font-black text-2xl italic tracking-tighter text-primary shadow-neon-text">{r.v}</td>
                                        <td className="py-5 px-8 text-[10px] font-black text-text/40 uppercase tracking-widest">{r.s}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        );
    };

  return (
    <div className="min-h-screen pt-12 px-4 md:px-8 max-w-[1600px] mx-auto text-text font-inter selection:bg-primary/30 relative">
        <style dangerouslySetInnerHTML={{ __html: `
            .result-content h3 { font-family: 'Outfit', sans-serif; font-weight: 900; text-transform: uppercase; letter-spacing: -0.02em; font-style: italic; font-size: 1.5rem; }
            .result-content hr { border-color: rgba(102, 252, 241, 0.1); margin: 2rem 0; }
            .result-content table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; }
            .result-content tr { border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
            .result-content td { padding: 0.75rem 1rem; font-size: 0.875rem; color: rgba(255, 255, 255, 0.6); }
            .terminal-glow { text-shadow: 0 0 10px rgba(102,252,241,0.3); }
        `}} />

        <div className="flex flex-col lg:flex-row gap-6 min-h-[calc(100vh-140px)]">
            {/* Command Sidebar */}
            <div className="w-full lg:w-72 flex-shrink-0">
              <div className="glass-card p-6 border-white/5 bg-surface/20 h-full flex flex-col gap-1 sticky top-24">
                <div className="text-[9px] font-black text-primary/40 uppercase tracking-[0.4em] mb-4 px-3 flex items-center justify-between">
                  <span>Directory</span>
                  <div className="w-1 h-1 rounded-full bg-primary animate-pulse" />
                </div>
                {[
                    { id: 'home', label: 'System Overview', icon: <History /> },
                    { id: 'fantasy', label: 'Fantasy Optimizer', icon: <Star /> },
                    { id: 'match', label: 'Predictor Engine', icon: <Zap /> },
                    { id: 'player', label: 'Entity Profile', icon: <UserIcon /> },
                    { id: 'team', label: 'Tactical Unit', icon: <Shield /> },
                    { id: 'venue', label: 'Sector Analysis', icon: <MapPin /> },
                    { id: 'auction', label: 'Market Scout', icon: <Gavel /> },
                    { id: 'ipl26', label: 'Season Forecast', icon: <Globe /> },
                    { id: 'squads', label: 'Roster Manifest', icon: <Users /> },
                    { id: 'champions', label: 'Hall of Honor', icon: <Trophy /> },
                    { id: 'records', label: 'Data Archives', icon: <Sparkles /> },
                ].map(item => (
                    <button
                        key={item.id}
                        onClick={() => setActiveTab(item.id)}
                        className={`group flex items-center gap-3 px-4 py-3 rounded-xl text-[11px] font-black uppercase tracking-widest transition-all ${
                            activeTab === item.id 
                            ? 'bg-primary text-background shadow-neon scale-[1.02]' 
                            : 'text-text/40 hover:text-primary hover:bg-white/5'
                        }`}
                    >
                        {React.isValidElement(item.icon) ? React.cloneElement(item.icon as any, { className: `w-4 h-4 ${activeTab === item.id ? '' : 'group-hover:scale-110'} transition-transform` }) : item.icon}
                        {item.label}
                    </button>
                ))}
                
                <div className="mt-8 pt-8 border-t border-white/5">
                  <button 
                    onClick={handleReset}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest text-text/20 hover:text-red-400 hover:bg-red-400/5 transition-all"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    Reset Buffer
                  </button>
                </div>
              </div>
            </div>

            {/* Main Console */}
            <div className="flex-1 min-w-0">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.3 }}
                        className="h-full"
                    >
                        {activeTab === 'home' ? renderHome() : (
                            <div className="glass-card border-white/10 bg-surface/30 backdrop-blur-3xl overflow-hidden flex flex-col h-full min-h-[70vh]">
                                <div className="p-8 md:p-10 flex-1">
                                    {activeTab === 'fantasy' && renderModuleShell(
                                        'fantasy', 'Fantasy XI Optimizer', 'Optimization Protocol', <Star />,
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                                            <div className="space-y-2">
                                              <p className="text-[9px] font-black uppercase tracking-widest text-primary/40 px-1">Host Team</p>
                                              <select value={fantasyForm.t1} onChange={e => setFantasyForm({...fantasyForm, t1: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-primary transition-all">
                                                  {Object.keys(SQUADS).map(t => <option key={t} value={t} className="bg-surface">{t}</option>)}
                                              </select>
                                            </div>
                                            <div className="space-y-2">
                                              <p className="text-[9px] font-black uppercase tracking-widest text-primary/40 px-1">Visitor Team</p>
                                              <select value={fantasyForm.t2} onChange={e => setFantasyForm({...fantasyForm, t2: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-primary transition-all">
                                                  {Object.keys(SQUADS).map(t => <option key={t} value={t} className="bg-surface">{t}</option>)}
                                              </select>
                                            </div>
                                            <div className="space-y-2">
                                              <p className="text-[9px] font-black uppercase tracking-widest text-primary/40 px-1">Sector</p>
                                              <select value={fantasyForm.venue} onChange={e => setFantasyForm({...fantasyForm, venue: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-primary transition-all">
                                                  {Object.keys(VENUES).map(v => <option key={v} value={v} className="bg-surface">{v}</option>)}
                                              </select>
                                            </div>
                                        </div>,
                                        ['Generate Best XI', 'Differential Analysis', 'Risk-Averse Pool']
                                    )}
                                    
                                    {activeTab === 'match' && renderModuleShell(
                                        'match', 'Match Predictor', 'Win-Probability Engine', <Zap />,
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                                            <select value={matchForm.t1} onChange={e => setMatchForm({...matchForm, t1: e.target.value})} className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-primary">
                                                {Object.keys(SQUADS).map(t => <option key={t} value={t} className="bg-surface">{t}</option>)}
                                            </select>
                                            <select value={matchForm.t2} onChange={e => setMatchForm({...matchForm, t2: e.target.value})} className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-primary">
                                                {Object.keys(SQUADS).map(t => <option key={t} value={t} className="bg-surface">{t}</option>)}
                                            </select>
                                        </div>,
                                        ['Full Forecast', 'H2H Matrix', 'Pressure Scenarios']
                                    )}

                                    {activeTab === 'player' && renderModuleShell(
                                        'player', 'Entity Analysis', 'Player Profile Engine', <UserIcon />,
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                                            <select value={playerForm.player} onChange={e => setPlayerForm({...playerForm, player: e.target.value})} className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-primary font-mono italic">
                                                {Object.keys(PLAYERS).map(p => <option key={p} value={p} className="bg-surface">{p}</option>)}
                                            </select>
                                            <select value={playerForm.vs} onChange={e => setPlayerForm({...playerForm, vs: e.target.value})} className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-primary">
                                                <option value="All Teams">vs Universal Dataset</option>
                                                {Object.keys(SQUADS).map(t => <option key={t} value={t} className="bg-surface">vs {t}</option>)}
                                            </select>
                                        </div>,
                                        ['Full Capability Map', 'Combat History', 'Fantasy Performance']
                                    )}

                                    {activeTab === 'team' && renderModuleShell(
                                        'team', 'Tactical Strategy', 'Unit Coordinator', <Shield />,
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                                            <select value={teamForm.team} onChange={e => setTeamForm({...teamForm, team: e.target.value})} className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-primary">
                                                {Object.keys(SQUADS).map(t => <option key={t} value={t} className="bg-surface">{t}</option>)}
                                            </select>
                                            <select value={teamForm.opp} onChange={e => setTeamForm({...teamForm, opp: e.target.value})} className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-primary">
                                                {Object.keys(SQUADS).map(t => <option key={t} value={t} className="bg-surface">vs {t}</option>)}
                                            </select>
                                        </div>,
                                        ['Deployment Plan', 'Rival Suppression', 'Best Tactical XI']
                                    )}

                                    {activeTab === 'venue' && renderModuleShell(
                                        'venue', 'Sector Intelligence', 'Venue Environmental Engine', <MapPin />,
                                        <div className="grid grid-cols-1 md:grid-cols-1 gap-4 mb-8">
                                            <select value={venueForm.venue} onChange={e => setVenueForm({...venueForm, venue: e.target.value})} className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-primary">
                                                {Object.keys(VENUES).map(v => <option key={v} value={v} className="bg-surface">{v}</option>)}
                                            </select>
                                        </div>,
                                        ['Environmental Scan', 'Ground Records', 'Toss Impact']
                                    )}

                                    {activeTab === 'auction' && renderModuleShell(
                                        'auction', 'Market Scout', 'Financial Predictive Intel', <Gavel />,
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                                            <select value={auctionForm.team} onChange={e => setAuctionForm({...auctionForm, team: e.target.value})} className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-primary font-mono italic">
                                                <option value="All Teams">Universal Market</option>
                                                {Object.keys(SQUADS).map(t => <option key={t} value={t} className="bg-surface">{t}</option>)}
                                            </select>
                                            <select value={auctionForm.role} onChange={e => setAuctionForm({...auctionForm, role: e.target.value})} className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-primary">
                                                <option value="All Roles">All Specializations</option>
                                                <option value="Batter">Batter</option>
                                                <option value="Bowler">Bowler</option>
                                                <option value="All-Rounder">All-Rounder</option>
                                                <option value="WK">Wicket Keeper</option>
                                            </select>
                                        </div>,
                                        ['Asset Valuation', 'Growth Assets', 'Tactical Buys']
                                    )}

                                    {activeTab === 'ipl26' && renderModuleShell(
                                        'ipl26', 'Season Forecast', 'Deep Predictive Engine', <Globe />,
                                        <div className="grid grid-cols-1 md:grid-cols-1 gap-4 mb-8">
                                            <select value={ipl26Form.type} onChange={e => setIpl26Form({...ipl26Form, type: e.target.value})} className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-primary font-black uppercase italic tracking-widest">
                                                <option value="Season Champion">Championship Probability</option>
                                                <option value="Orange Cap">Scoring Dominance</option>
                                                <option value="Purple Cap">Strike Capability</option>
                                                <option value="Breakout Star">Breakout Potential</option>
                                            </select>
                                        </div>,
                                        ['Probabilistic Model', 'Full Forecast', 'Key Divergences']
                                    )}

                                    {activeTab === 'squads' && renderSquads()}
                                    {activeTab === 'champions' && renderChampionsView()}
                                    {activeTab === 'records' && renderRecordsView()}
                                </div>
                            </div>
                        )}
                    </motion.div>
                </AnimatePresence>
            </div>
        </div>

        {/* Auth Interface */}
        {showModal && (
            <div className="fixed inset-0 z-[200] flex items-center justify-center bg-black/90 backdrop-blur-xl p-6">
                <motion.div 
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="glass-card border-primary/30 p-12 max-w-lg w-full shadow-[0_0_100px_rgba(102,252,241,0.1)] relative overflow-hidden"
                >
                    <div className="scanning-bar opacity-20" />
                    <div className="text-center relative z-10">
                        <div className="w-20 h-20 bg-primary/10 rounded-3xl flex items-center justify-center mx-auto mb-8 border border-primary/30 shadow-neon">
                          <Cpu className="text-primary w-10 h-10 animate-pulse" />
                        </div>
                        <h2 className="text-4xl font-outfit font-black tracking-tighter text-white mb-3 italic">SYSTEM <span className="text-primary">ACCESS</span></h2>
                        <p className="text-text/40 text-sm mb-10 leading-relaxed font-medium">
                            Multi-model Intelligence Platform initialized. Synchronized with 18,000+ match data nodes. 
                            Select access protocol to continue.
                        </p>
                        <div className="space-y-6">
                            <div className="space-y-2">
                              <p className="text-[9px] font-black uppercase tracking-[0.4em] text-primary/40">Credential Input</p>
                              <input 
                                  type="password"
                                  placeholder="Enter Decryption Key..."
                                  className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-sm focus:border-primary outline-none font-mono text-center tracking-widest"
                                  onChange={(e) => setApiKey(e.target.value)}
                              />
                            </div>
                            <div className="flex flex-col gap-3">
                                <button 
                                    onClick={() => handleLaunch(false, apiKey)}
                                    className="w-full bg-primary text-background font-black uppercase tracking-[0.3em] py-5 rounded-2xl hover:scale-[1.02] active:scale-[0.98] transition-all shadow-neon"
                                >
                                    Login (Live AI)
                                </button>
                                <button 
                                    onClick={() => handleLaunch(true)}
                                    className="w-full bg-white/5 border border-white/10 text-text/60 font-black uppercase tracking-[0.3em] py-4 rounded-2xl hover:bg-white/10 transition-colors"
                                >
                                    Guest Access
                                </button>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        )}
    </div>
  );
};
