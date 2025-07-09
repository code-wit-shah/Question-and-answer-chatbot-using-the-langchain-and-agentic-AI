from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import httpx
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# FastAPI instance
app = FastAPI()

# Enable CORS (all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supported models mapping
SUPPORTED_MODELS = {
    "llama3-8b": "llama3-8b-8192",
    "llama3-70b": "llama3-70b-8192",
}

DEFAULT_MODEL = "llama3-8b"  # Set a fallback default

# Request schema
class QuestionRequest(BaseModel):
    question: str
    model: str = DEFAULT_MODEL

# Chat endpoint
@app.post("/chat")
async def chat(req: QuestionRequest):
    if not req.question.strip():
        return JSONResponse(content={"error": "❌ Question is empty."}, status_code=400)

    # Use provided model or default
    model_name = SUPPORTED_MODELS.get(req.model, SUPPORTED_MODELS[DEFAULT_MODEL])

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": req.question}],
        "max_tokens": 200,
        "temperature": 0.7
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if not content:
                return JSONResponse(content={"answer": "⚠️ No content returned."}, status_code=200)

            return {"answer": content}

        except httpx.HTTPStatusError as e:
            return JSONResponse(content={"error": f"HTTP error: {e.response.status_code} - {e.response.text}"}, status_code=e.response.status_code)

        except httpx.RequestError as e:
            return JSONResponse(content={"error": f"Request error: {str(e)}"}, status_code=500)
