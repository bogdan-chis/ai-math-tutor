import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import ChatRequest, ChatResponse
from .model import ChatModel

MODEL_DIR = os.getenv("MODEL_DIR", "./gpt2-mathdial-masked_loss")  # point to your saved checkpoint folder

app = FastAPI(title="MathDial Tutor Chat API")

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_model: ChatModel | None = None

@app.on_event("startup")
def _startup():
    global chat_model
    chat_model = ChatModel(MODEL_DIR)

@app.get("/health")
def health():
    return {"ok": True, "model_dir": MODEL_DIR}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    assert chat_model is not None
    reply = chat_model.generate(
        messages=[m.model_dump() for m in req.messages],
        max_new_tokens=req.max_new_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        repetition_penalty=req.repetition_penalty,
        seed=req.seed,
    )
    return ChatResponse(reply=reply)
