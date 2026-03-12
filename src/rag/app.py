from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
