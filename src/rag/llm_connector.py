import os
from google import genai
from dotenv import load_dotenv

# Load env variables from .env
load_dotenv()

class GeminiConnector:
    """
    Modular connector for Gemini LLM.
    Updated for the modern Google GenAI SDK (google-genai).
    """
    def __init__(self, api_key=None, model_name="gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment or .env file.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def generate_response(self, prompt):
        """Sends the grounded prompt to Gemini using the new SDK."""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error connecting to Gemini (V5 SDK): {str(e)}"
