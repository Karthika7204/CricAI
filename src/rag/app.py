from fastapi import FastAPI, HTTPException, Request, Form, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import json
from pathlib import Path

# Add src and current dir to path to import local modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.dirname(__file__))

from rag.engine import QueryEngine
from rag.award_engine import calculate_awards
from rag.pre_match_analysis import get_pre_match_analysis
from rag.scorecard_engine import get_match_scorecard
from rag.pvp_analysis import get_pvp_comparison
from rag.pvp_bot_engine import PvPBotEngine
from rag.strategy_bot_engine import StrategyBotEngine
from rag.pressure_bot_engine import PressureBotEngine
from flow.match_flow_engine import MatchFlowEngine

# Training Assistant Imports
from training_assistant.data_loader import load_datasets
from training_assistant.player_analysis import analyze_player_performance
from training_assistant.weakness_detection import detect_weakness
from training_assistant.simulation_generator import generate_training_plan
from training_assistant.player_matchup import analyze_player_matchups
from training_assistant.field_strategy import predict_field_setup

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
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

query_engine = QueryEngine(data_dir=DATA_DIR, gemini_api_key=GEMINI_KEY)
pvp_bot = PvPBotEngine(data_dir=DATA_DIR, gemini_api_key=GEMINI_KEY)
strategy_bot = StrategyBotEngine(data_dir=DATA_DIR, gemini_api_key=GEMINI_KEY)
pressure_bot = PressureBotEngine(data_dir=DATA_DIR, gemini_api_key=GEMINI_KEY)
flow_engine = MatchFlowEngine(data_root=os.path.join(DATA_DIR, "processed/t20/matches"))

# Initialize Training Assistant Data
TRAINING_DATASETS = load_datasets()
TA_BALL_BY_BALL = TRAINING_DATASETS["ball_by_ball"]
TA_MATCHES = TRAINING_DATASETS["matches"]
TA_PLAYERS = TRAINING_DATASETS["players"]

# Templates for Training Assistant
templates = Jinja2Templates(directory="templates/training_assistant")

def get_ta_ipl_teams():
    teams = set()
    if "team1" in TA_MATCHES.columns and "team2" in TA_MATCHES.columns:
        teams.update(TA_MATCHES["team1"].dropna().unique())
        teams.update(TA_MATCHES["team2"].dropna().unique())
    return sorted([t for t in teams if t])

def get_ta_team_players(team_name):
    players = set()
    if "batting_team" in TA_BALL_BY_BALL.columns and "striker" in TA_BALL_BY_BALL.columns:
        players.update(
            TA_BALL_BY_BALL[TA_BALL_BY_BALL["batting_team"] == team_name]["striker"].dropna().unique()
        )
    if "batting_team" in TA_BALL_BY_BALL.columns and "non_striker" in TA_BALL_BY_BALL.columns:
        players.update(
            TA_BALL_BY_BALL[TA_BALL_BY_BALL["batting_team"] == team_name]["non_striker"].dropna().unique()
        )
    if not players:
        if "batsman" in TA_BALL_BY_BALL.columns:
            players.update(TA_BALL_BY_BALL["batsman"].dropna().unique())
        if "player_name" in TA_PLAYERS.columns:
            players.update(TA_PLAYERS["player_name"].dropna().unique())
        elif "player" in TA_PLAYERS.columns:
            players.update(TA_PLAYERS["player"].dropna().unique())
    return sorted(players)

class QueryRequest(BaseModel):
    match_id: str
    query: str

# ─────────────────────────────────────────────────────
# API Router (Prefix: /api)
# ─────────────────────────────────────────────────────
router = APIRouter(prefix="/api")

@router.get("/")
def read_root():
    return {"status": "CricAI Bridge Active", "version": "2.0"}

@router.post("/chat")
async def chat(request: QueryRequest):
    try:
        result = query_engine.query(request.match_id, request.query)
        return result
    except Exception as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg or "rate_limit" in err_msg:
            raise HTTPException(status_code=429, detail="AI Quota Reached or Rate Limited.")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/matches")
async def get_matches():
    try:
        matches_dir = os.path.join(DATA_DIR, "processed/t20/matches")
        if not os.path.exists(matches_dir):
            return {"matches": []}
            
        def clean_s(val):
            if not isinstance(val, str): return val
            return val.replace("'", "").replace('"', "").strip()

        match_list = []
        for match_id in os.listdir(matches_dir):
            match_path = os.path.join(matches_dir, match_id)
            if not os.path.isdir(match_path):
                continue
            match_info = None
            context_path = os.path.join(match_path, "context.json")
            if os.path.exists(context_path):
                try:
                    with open(context_path, 'r') as f:
                        cdata = json.load(f)
                        meta = cdata.get("metadata", {})
                        tsum = meta.get("team_summary", {})
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

            if match_info:
                match_list.append(match_info)
        match_list.sort(key=lambda x: int(x["id"]) if x["id"].isdigit() else x["id"])
        return {"matches": match_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/match/{match_id}/awards")
async def get_awards(match_id: str):
    return calculate_awards(match_id, DATA_DIR)

@router.get("/match/{match_id}/flow")
async def get_flow(match_id: str):
    try:
        return flow_engine.generate_match_flow(match_id)
    except Exception as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg or "rate_limit" in err_msg:
            raise HTTPException(status_code=429, detail="AI Flow Quota Reached.")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/match/{match_id}/insights")
async def get_insights(match_id: str):
    return get_pre_match_analysis(match_id, DATA_DIR)

@router.get("/match/{match_id}/scorecard")
async def get_scorecard(match_id: str):
    return get_match_scorecard(match_id, DATA_DIR)

@router.get("/match/{match_id}/pvp")
async def pvp_comparison(match_id: str, force_refresh: bool = False):
    return get_pvp_comparison(match_id, DATA_DIR, force_refresh=force_refresh)

@router.post("/match/{match_id}/recommend/pvp")
async def recommend_pvp(match_id: str, request: QueryRequest):
    try:
        return pvp_bot.query(match_id, request.query)
    except Exception as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg or "rate_limit" in err_msg:
            raise HTTPException(status_code=429, detail="AI Quota Reached or Rate Limited.")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match/{match_id}/recommend/strategy")
async def recommend_strategy(match_id: str, request: QueryRequest):
    try:
        return strategy_bot.query(match_id, request.query)
    except Exception as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg or "rate_limit" in err_msg:
            raise HTTPException(status_code=429, detail="AI Quota Reached or Rate Limited.")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match/{match_id}/recommend/pressure")
async def recommend_pressure(match_id: str, request: QueryRequest):
    try:
        return pressure_bot.query(match_id, request.query)
    except Exception as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg or "rate_limit" in err_msg:
            raise HTTPException(status_code=429, detail="AI Quota Reached or Rate Limited.")
        raise HTTPException(status_code=500, detail=str(e))

# Training Assistant API Routes
@router.get("/ta/teams")
async def ta_api_teams():
    return {"teams": get_ta_ipl_teams()}

@router.get("/ta/team_players")
async def ta_api_team_players(team: str = ""):
    return {"players": get_ta_team_players(team)}

@router.post("/ta/analyze")
async def ta_api_analyze(team: str = Form(...), player_name: str = Form(...)):
    try:
        player_name = player_name.strip()
        stats = analyze_player_performance(TA_BALL_BY_BALL, player_name)
        if stats is None:
            raise HTTPException(status_code=404, detail="Player not found in dataset.")
        
        weaknesses = detect_weakness(stats)
        field_strategy = predict_field_setup(weaknesses)
        simulation = generate_training_plan(player_name, stats, weaknesses)
        matchup = analyze_player_matchups(TA_BALL_BY_BALL, player_name)

        def convert_numpy(obj):
            if isinstance(obj, dict): return {k: convert_numpy(v) for k, v in obj.items()}
            if isinstance(obj, list): return [convert_numpy(i) for i in obj]
            if hasattr(obj, 'item'): return obj.item()
            return obj

        return convert_numpy({
            "team": team, "player_name": player_name, "stats": stats,
            "weaknesses": weaknesses, "field_strategy": field_strategy,
            "simulation": simulation, "matchup": matchup
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ta/ping")
async def ta_ping():
    return {"status": "TA API Active", "timestamp": str(os.path.getmtime(__file__))}

app.include_router(router)

# ─────────────────────────────────────────────────────
# Legacy/HTML Routes
# ─────────────────────────────────────────────────────
@app.get("/training-assistant", response_class=HTMLResponse)
async def ta_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "teams": get_ta_ipl_teams()})

@app.post("/training-assistant/analyze", response_class=HTMLResponse)
async def ta_analyze(request: Request, team: str = Form(...), player_name: str = Form(...)):
    player_name = player_name.strip()
    stats = analyze_player_performance(TA_BALL_BY_BALL, player_name)
    if stats is None:
        return templates.TemplateResponse("index.html", {"request": request, "teams": get_ta_ipl_teams(), "error": "Player not found."})
    
    weaknesses = detect_weakness(stats)
    field_strategy = predict_field_setup(weaknesses)
    simulation = generate_training_plan(player_name, stats, weaknesses)
    matchup = analyze_player_matchups(TA_BALL_BY_BALL, player_name)
    
    return templates.TemplateResponse("results.html", {
        "request": request, "team": team, "player_name": player_name,
        "stats": stats, "weaknesses": weaknesses, "field_strategy": field_strategy,
        "simulation": simulation, "matchup": matchup, "teams": get_ta_ipl_teams(),
        "team_players": get_ta_team_players(team) if team else []
    })

if __name__ == "__main__":
    print("-" * 50)
    print("CRIC-AI BACKEND STARTING...")
    print("Routes registered under /api/ prefix")
    print("-" * 50)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
