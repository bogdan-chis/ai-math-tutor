export type Role = "system" | "user" | "assistant";

export type ChatMessage = {
  role: Role;
  content: string;
};

export type ChatRequest = {
  messages: ChatMessage[];
  max_new_tokens?: number;
  temperature?: number;
  top_p?: number;
  repetition_penalty?: number;
  seed?: number | null;
};

export type ChatResponse = {
  reply: string;
};
