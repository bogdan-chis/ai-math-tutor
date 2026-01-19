import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed
from typing import List, Dict, Optional

from .safety import build_bad_words_list, has_final_answer_cue

SPECIAL_TOKENS = ["<STUDENT>", "<TUTOR>", "<PROBLEM>", "</PROBLEM>", "<FINAL_ANSWER_REDACTED>"]

def _device():
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"

class ChatModel:
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.device = _device()

        self.tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
        self.tokenizer.add_special_tokens({"additional_special_tokens": SPECIAL_TOKENS})
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(model_dir)
        self.model.resize_token_embeddings(len(self.tokenizer))
        self.model.to(self.device)
        self.model.eval()

        # Precompute bad_words_ids for decoding-time suppression
        bad_phrases = build_bad_words_list()
        self.bad_words_ids = [self.tokenizer.encode(p, add_special_tokens=False) for p in bad_phrases]

    def format_prompt(self, messages: List[Dict[str, str]], max_turns: int = 10) -> str:
        """
        Converts OpenAI-style {role, content} into the MathDial-style tags.
        Keeps last max_turns user/assistant turns.
        """
        # Keep only user/assistant; system becomes an instruction header.
        system = ""
        filtered = []
        for m in messages:
            if m["role"] == "system":
                system += m["content"].strip() + "\n"
            elif m["role"] in ("user", "assistant"):
                filtered.append(m)

        filtered = filtered[-max_turns:]

        prompt = ""
        if system:
            prompt += f"<PROBLEM>\n{system.strip()}\n</PROBLEM>\n"

        for m in filtered:
            if m["role"] == "user":
                prompt += f"<STUDENT> {m['content'].strip()}\n"
            else:
                prompt += f"<TUTOR> {m['content'].strip()}\n"

        # Model should generate the next tutor turn
        prompt += "<TUTOR> "
        return prompt

    @torch.no_grad()
    def generate(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 160,
        temperature: float = 0.8,
        top_p: float = 0.95,
        repetition_penalty: float = 1.1,
        seed: Optional[int] = None,
    ) -> str:
        if seed is not None:
            set_seed(seed)

        prompt = self.format_prompt(messages)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Prefer deterministic behavior at temp=0
        do_sample = temperature is not None and temperature > 0

        gen = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=max(temperature, 1e-6) if do_sample else None,
            top_p=top_p if do_sample else None,
            repetition_penalty=repetition_penalty,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            bad_words_ids=self.bad_words_ids,
        )

        full = self.tokenizer.decode(gen[0], skip_special_tokens=False)

        # Extract only what comes after the last "<TUTOR> "
        idx = full.rfind("<TUTOR>")
        reply = full[idx + len("<TUTOR>"):].strip() if idx != -1 else full.strip()

        # Hard safety: if it still starts with a final cue, refuse and reframe
        if has_final_answer_cue(reply):
            return "I can guide you step by step, but I won’t give the final answer directly. What have you tried so far, and where do you get stuck?"

        # Clean up any special tokens that might leak
        reply = reply.replace("<FINAL_ANSWER_REDACTED>", "").strip()
        return reply
