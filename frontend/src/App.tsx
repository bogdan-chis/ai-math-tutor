import React, { useMemo, useRef, useState } from "react";
import { sendChat } from "./api";
import type { ChatMessage } from "./types";
import "./styles.css";

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "system",
      content:
        "You are a Socratic math tutor. Ask guiding questions, give hints, and avoid giving the final answer directly.",
    },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  const [temperature, setTemperature] = useState(0.8);
  const [maxNewTokens, setMaxNewTokens] = useState(180);

  const chatRef = useRef<HTMLDivElement | null>(null);

  const viewMessages = useMemo(
    () => messages.filter((m) => m.role !== "system"),
    [messages]
  );

  async function onSend() {
    const text = input.trim();
    if (!text || busy) return;

    const next: ChatMessage[] = [...messages, { role: "user", content: text }];
    setMessages(next);
    setInput("");
    setBusy(true);

    try {
      const res = await sendChat({
        messages: next,
        temperature,
        max_new_tokens: maxNewTokens,
        top_p: 0.95,
        repetition_penalty: 1.1,
        seed: null,
      });

      setMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);

      // scroll to bottom
      setTimeout(() => {
        chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" });
      }, 50);
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${e?.message ?? String(e)}` },
      ]);
    } finally {
      setBusy(false);
    }
  }

  function onClear() {
    setMessages(messages.slice(0, 1)); // keep system
    setInput("");
  }

  return (
    <div className="container">
      <div className="card">
        <div className="header">
          <div className="title">MathDial Tutor Chat</div>
          <div className="row">
            <button className="smallbtn" onClick={onClear} disabled={busy}>
              Clear
            </button>
          </div>
        </div>

        <div className="controls">
          <label>
            Temperature{" "}
            <input
              type="number"
              step="0.1"
              min="0"
              max="2"
              value={temperature}
              onChange={(e) => setTemperature(Number(e.target.value))}
            />
          </label>
          <label>
            Max new tokens{" "}
            <input
              type="number"
              step="10"
              min="50"
              max="500"
              value={maxNewTokens}
              onChange={(e) => setMaxNewTokens(Number(e.target.value))}
            />
          </label>
        </div>

        <div className="chat" ref={chatRef}>
          {viewMessages.map((m, i) => (
            <div
              key={i}
              className={[
                "msg",
                m.role === "user" ? "user" : m.role === "assistant" ? "assistant" : "system",
              ].join(" ")}
            >
              {m.content}
            </div>
          ))}
          {busy && <div className="msg assistant">Thinking…</div>}
        </div>

        <div className="footer">
          <input
            className="input"
            value={input}
            placeholder="Ask a question (e.g., 'How do I solve 3x+5=20?')"
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                onSend();
              }
            }}
            disabled={busy}
          />
          <button className="btn" onClick={onSend} disabled={busy || !input.trim()}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
