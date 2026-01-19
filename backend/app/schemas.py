from pydantic import BaseModel, Field
from typing import List, Literal, Optional


Role = Literal["user", "assistant", "system"]


class ChatMessage(BaseModel):
    role: Role
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(default_factory=list)
    max_new_tokens: int = 160
    temperature: float = 0.8
    top_p: float = 0.95
    repetition_penalty: float = 1.1
    seed: Optional[int] = None


class ChatResponse(BaseModel):
    reply: str
