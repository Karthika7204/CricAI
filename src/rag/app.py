from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import json
from pathlib import Path

# Add src to path to import local modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from rag.engine import QueryEngine
from rag.award_engine import calculate_awards
from rag.pre_match_analysis import get_pre_match_analysis
from rag.scorecard_engine import get_match_scorecard
from rag.pvp_analysis import get_pvp_comparison
from rag.pvp_bot_engine import PvPBotEngine
from rag.strategy_bot_engine import StrategyBotEngine
from rag.pressure_bot_engine import PressureBotEngine
from flow.match_flow_engine import MatchFlowEngine

app = FastAPI(title="CricAI Backend Bridge")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engines
DATA_DIR = "d:/CricAI/data"
query_engine = QueryEngine(data_dir=DATA_DIR)
pvp_bot = PvPBotEngine(data_dir=DATA_DIR)
strategy_bot = StrategyBotEngine(data_dir=DATA_DIR)
pressure_bot = PressureBotEngine(data_dir=DATA_DIR)
flow_engine = MatchFlowEngine(data_root=os.path.join(DATA_DIR, "processed/t20/matches"))

class QueryRequest(BaseModel):
    match_id: str
    query: str

@app.get("/")
def read_root():
    return {"status": "CricAI Bridge Active"}

@app.post("/api/chat")
async def chat(request: QueryRequest):
    try:
        result = query_engine.query(request.match_id, request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/matches")
async def get_matches():
    try:
        matches_dir = os.path.join(DATA_DIR, "processed/t20/matches")
        if not os.path.exists(matches_dir):
            return {"matches": []}
            
        def clean_s(val):
            if not isinstance(val, str): return val
            return val.replace("'", "").replace('"', "").strip()

        match_list = []
        # Get all subdirectories in the matches folder
        for match_id in os.listdir(matches_dir):
            match_path = os.path.join(matches_dir, match_id)
            if not os.path.isdir(match_path):
                continue

            match_info = None
            
            # 1. Primary Source: context.json
            context_path = os.path.join(match_path, "context.json")
            if os.path.exists(context_path):
                try:
                    with open(context_path, 'r') as f:
                        cdata = json.load(f)
                        meta = cdata.get("metadata", {})
                        tsum = meta.get("team_summary", {})
                        
                        # Clean and transform
                        clean_tsum = {clean_s(k): v for k, v in tsum.items()}
                        clean_meta = {k: clean_s(v) if isinstance(v, str) else v for k, v in meta.items()}
                        teams = list(clean_tsum.keys())
                        
                        if len(teams) >= 2:
                            match_info = {
                                "id": match_id,
                                "date": clean_meta.get("date", ""),
                                "venue": clean_meta.get("venue", ""),
                                "stage": clean_meta.get("stage", ""),
                                "teams": [teams[0][:3].upper(), teams[1][:3].upper()],
                                "full_teams": teams,
                                "metadata": clean_meta,
                                "scores": clean_tsum
                            }
                except Exception: pass

            # 2. Secondary Fallback: structured_summary.json
            if not match_info:
                summary_path = os.path.join(match_path, "structured_summary.json")
                if os.path.exists(summary_path):
                    try:
                        with open(summary_path, 'r') as f:
                            data = json.load(f)
                            ctx = data.get("match_context", {})
                            teams_raw = list(ctx.get("Teams", {}).keys())
                            teams = [clean_s(t) for t in teams_raw]
                            if len(teams) >= 2:
                                match_info = {
                                    "id": match_id,
                                    "date": clean_s(ctx.get("date", "")),
                                    "teams": [teams[0][:3].upper(), teams[1][:3].upper()],
                                    "full_teams": teams,
                                    "venue": clean_s(ctx.get("venue", "")),
                                    "stage": clean_s(ctx.get("event", "League")),
                                    "metadata": {"winner": clean_s(ctx.get("winner", ""))}
                                }
                    except Exception: pass

            # 3. Final Fallback: batting.csv (basic)
            if not match_info:
                batting_path = os.path.join(match_path, "batting.csv")
                if os.path.exists(batting_path):
                    try:
                        import pandas as pd
                        df = pd.read_csv(batting_path)
                        teams = [clean_s(t) for t in df['team'].unique()]
                        if len(teams) >= 2:
                            match_info = {
                                "id": match_id,
                                "date": clean_s(df['date'].iloc[0]) if 'date' in df.columns else "",
                                "teams": [teams[0][:3].upper(), teams[1][:3].upper()],
                                "full_teams": teams
                            }
                    except Exception: pass

            # IMPORTANT: Append to the list if found
            if match_info:
                match_list.append(match_info)
        
        # Sort strictly by match ID ascending (to follow sequence 1512719 -> 1512773)
        match_list.sort(key=lambda x: int(x["id"]) if x["id"].isdigit() else x["id"])
        return {"matches": match_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/match/{match_id}/awards")
async def get_awards(match_id: str):
    try:
        return calculate_awards(match_id, DATA_DIR)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/match/{match_id}/flow")
async def get_flow(match_id: str):
    try:
        return flow_engine.generate_match_flow(match_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/match/{match_id}/insights")
async def get_insights(match_id: str):
    try:
        return get_pre_match_analysis(match_id, DATA_DIR)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/match/{match_id}/scorecard")
async def get_scorecard(match_id: str):
    try:
        return get_match_scorecard(match_id, DATA_DIR)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/match/{match_id}/pvp")
async def pvp_comparison(match_id: str, force_refresh: bool = False):
    try:
        return get_pvp_comparison(match_id, DATA_DIR, force_refresh=force_refresh)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match/{match_id}/recommend/pvp")
async def recommend_pvp(match_id: str, request: QueryRequest):
    try:
        return pvp_bot.query(match_id, request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match/{match_id}/recommend/strategy")
async def recommend_strategy(match_id: str, request: QueryRequest):
    try:
        return strategy_bot.query(match_id, request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match/{match_id}/recommend/pressure")
async def recommend_pressure(match_id: str, request: QueryRequest):
    try:
        return pressure_bot.query(match_id, request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
