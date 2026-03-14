import os
import pickle
import faiss
import json
from pathlib import Path
from embedding import EmbeddingEngine
from router import Router
from prompt_builder import PromptBuilder
from award_engine import calculate_awards
from pre_match_analysis import get_pre_match_analysis
from pressure_bot_engine import PressureBotEngine
from pvp_bot_engine import PvPBotEngine
from strategy_bot_engine import StrategyBotEngine

from llm_connector import GeminiConnector

class QueryEngine:
    """
    V5 Orchestrator:
    - Caches FAISS indices and metadata
    - Routes queries (Rule-Based -> RAG)
    - Grounded LLM reasoning via Gemini
    """
    def __init__(self, data_dir="d:/CricAI/data", gemini_api_key=None):
        self.data_dir = Path(data_dir)
        self.cache = {} 
        self.embedding_engine = EmbeddingEngine()
        # Initialize Gemini Connector
        try:
            self.llm = GeminiConnector(api_key=gemini_api_key)
                
        except Exception as e:
            print(f"Warning: Gemini initialization failed: {e}")
            self.llm = None
        
        # Initialize Specialized Bots
        self.pressure_bot = PressureBotEngine(data_dir=data_dir, gemini_api_key=gemini_api_key)
        self.pvp_bot = PvPBotEngine(data_dir=data_dir, gemini_api_key=gemini_api_key)
        self.strategy_bot = StrategyBotEngine(data_dir=data_dir, gemini_api_key=gemini_api_key)

    def _load_match(self, match_id):
        if match_id in self.cache:
            return self.cache[match_id]

        match_folder = self.data_dir / "processed" / "t20" / "matches" / match_id
        index_path = match_folder / "index.faiss"
        chunks_path = match_folder / "chunks.pkl"
        meta_path = match_folder / "metadata.pkl"

        if not (index_path.exists() and chunks_path.exists() and meta_path.exists()):
            raise FileNotFoundError(f"Match {match_id} indices not found. Run preprocess.py first.")

        index = faiss.read_index(str(index_path))
        with open(chunks_path, 'rb') as f:
            chunks = pickle.load(f)
        with open(meta_path, 'rb') as f:
            meta = pickle.load(f)

        match_data = {"index": index, "chunks": chunks, "meta": meta}
        self.cache[match_id] = match_data
        return match_data

    def _load_analysis_file(self, match_id, filename):
        """Loads specialized analysis JSON (flow or recommendations)."""
        path = self.data_dir / "processed" / "t20" / "matches" / str(match_id) / filename
        if not path.exists():
            return {"error": f"Analysis file {filename} not found. Generate it first."}
        with open(path, 'r') as f:
            return json.load(f)

    def query(self, match_id, user_query):
        """
        Main query entry point.
        """
        match_id = str(match_id)
        
        # Check if LLM is initialized
        if not self.llm:
            return {
                "answer": "I'm sorry, my AI reasoning engine (Gemini) is currently not configured or available. Please check your API key settings.",
                "source": "error_no_llm",
                "error": "GeminiConnector not initialized"
            }

        try:
            m_data = self._load_match(match_id)
        except Exception as e:
            return {"error": str(e)}

        # 1. Rule-Based Router (Fast Track)
        router = Router(m_data['meta'])
        fast_answer = router.route(user_query)
        
        if fast_answer == "ROUTE_TO_ANALYSIS_FLOW":
            analysis_data = self._load_analysis_file(match_id, "match_flow.json")
            if "error" in analysis_data: return analysis_data
            prompt = PromptBuilder.build_analysis_prompt(user_query, "Match Flow", analysis_data)
            answer = self.llm.generate_response(prompt)
            return {"answer": answer, "source": "specialized_analysis_flow"}
            
        if fast_answer == "ROUTE_TO_ANALYSIS_RECOMMEND":
            analysis_data = self._load_analysis_file(match_id, "match_recommendations.json")
            if "error" in analysis_data: return analysis_data
            prompt = PromptBuilder.build_analysis_prompt(user_query, "Recommendations", analysis_data)
            answer = self.llm.generate_response(prompt)
            return {"answer": answer, "source": "specialized_analysis_recommend"}

        if fast_answer == "ROUTE_TO_AWARDS":
            awards_data = self._load_analysis_file(match_id, "awards.json")
            # If awards.json doesn't exist yet, generate it on-the-fly
            if "error" in awards_data:
                try:
                    awards_data = calculate_awards(match_id, str(self.data_dir))
                except Exception as e:
                    return {"error": f"Could not generate awards: {e}"}
            if self.llm:
                prompt = PromptBuilder.build_awards_prompt(user_query, awards_data)
                answer = self.llm.generate_response(prompt)
                return {"answer": answer, "source": "awards_engine"}
            else:
                return {"awards": awards_data, "source": "awards_engine_raw"}

        if fast_answer == "ROUTE_TO_PRE_MATCH_INSIGHTS":
            insight_data = self._load_analysis_file(match_id, "pre_match_insights.json")
            if "error" in insight_data:
                try:
                    insight_data = calculate_pre_match_insights(match_id, str(self.data_dir))
                except Exception as e:
                    return {"error": f"Could not generate insights: {e}"}
            if self.llm:
                prompt = PromptBuilder.build_pre_match_prompt(user_query, insight_data)
                answer = self.llm.generate_response(prompt)
                return {"answer": answer, "source": "pre_match_insights"}
            else:
                return {"insights": insight_data, "source": "pre_match_insights_raw"}

        if fast_answer == "ROUTE_TO_PRESSURE_RECOMMENDATION":
            return self.pressure_bot.query(match_id, user_query)

        if fast_answer == "ROUTE_TO_PVP_RECOMMENDATION":
            return self.pvp_bot.query(match_id, user_query)

        if fast_answer == "ROUTE_TO_STRATEGY_RECOMMENDATION":
            return self.strategy_bot.query(match_id, user_query)

        if fast_answer:
            return {"answer": fast_answer, "source": "rule_based", "tokens_saved": True}

        # 2. RAG Flow
        query_vec = self.embedding_engine.encode(user_query).astype('float32')
        D, I = m_data['index'].search(query_vec.reshape(1, -1), k=5)
        retrieved_chunks = [m_data['chunks'][i] for i in I[0] if i < len(m_data['chunks'])]
        
        # 3. Build Grounded Prompt
        prompt = PromptBuilder.build_grounded_prompt(user_query, retrieved_chunks)
        
        # 4. Gemini Reasoning
        if self.llm:
            answer = self.llm.generate_response(prompt)
            return {
                "answer": answer,
                "source": "rag_grounded_gemini",
                "retrieved_chunks": retrieved_chunks
            }
        else:
            return {
                "prompt": prompt,
                "error": "Gemini not configured",
                "source": "rag_unreasoned"
            }

if __name__ == "__main__":

    current_key = os.getenv("GEMINI_API_KEY")
    print(f"DEBUG: Initializing with API Key ending in: {current_key[-4:] if current_key else 'NONE'}")

    # Test stub
    engine = QueryEngine()
    # Assuming match 1512721 is preprocessed
    # result = engine.query("1512721", "Who won the match?")
    # print(result)
