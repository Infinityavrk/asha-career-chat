from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from pdf_loader import load_pdf_embeddings
from llm_engine import LLMResponder

load_dotenv()
vector_store = load_pdf_embeddings()
responder = LLMResponder(vector_store)

app = FastAPI()

# Allow React frontend to talk to API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    message: str
    history: list[str] = []

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ask")
def ask_question(data: ChatInput):
    print("🚨 *******************:")
    print("🚨 Received data:", data)
    history_text = ""
    for i, msg in enumerate(data.history):
        role = "Human" if i % 2 == 0 else "Career Expert"
        #history_text += f"{role}: {msg}\n"
        history_text += f"{msg}\n"

    answer = responder.generate_response(data.message, history_text)
    return {"response": answer}

@app.get("/suggestions")
def get_suggestions():
    return {
        "suggestions": [
            "What are high-paying careers in India?",
            "How to switch from commerce to tech?",
            "Will AI replace software engineers?"
        ]
    }