'use client'

import { useState, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

const INITIAL_MESSAGE = "Hi! I'm Adriana, your social intelligence analyst. I monitor Instagram, Reddit, Facebook, and the news in real time. Ask me what's trending, how sentiment looks on a topic, or anything about what people are saying."

const SUGGESTIONS = [
  "What's trending right now?",
  "What's happening on Reddit about AI?",
  "Search news for climate change",
  "What are people saying on Instagram?",
]

type Role = 'adriana' | 'user'
interface Msg { id: string; role: Role; text: string }

function Avatar() {
  return (
    <div className="w-7 h-7 rounded-full bg-zinc-800 flex items-center justify-center text-white text-xs font-semibold shrink-0">
      A
    </div>
  )
}

function Bubble({ msg }: { msg: Msg }) {
  const isAdriana = msg.role === 'adriana'
  return (
    <div className={`flex gap-2.5 fade-up ${isAdriana ? '' : 'flex-row-reverse'}`}>
      {isAdriana && <Avatar />}
      <div
        className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap
          ${isAdriana
            ? 'bg-white text-zinc-800 rounded-tl-sm border border-zinc-200'
            : 'bg-zinc-800 text-white rounded-tr-sm'
          }`}
      >
        {msg.text}
      </div>
    </div>
  )
}

function TypingBubble() {
  return (
    <div className="flex gap-2.5 fade-up">
      <Avatar />
      <div className="bg-white border border-zinc-200 rounded-2xl rounded-tl-sm px-4 py-3">
        <div className="flex gap-1 items-center h-4">
          <span className="typing-dot" style={{ animationDelay: '0ms' }} />
          <span className="typing-dot" style={{ animationDelay: '160ms' }} />
          <span className="typing-dot" style={{ animationDelay: '320ms' }} />
        </div>
      </div>
    </div>
  )
}

export default function Chat() {
  const [messages, setMessages] = useState<Msg[]>([
    { id: '0', role: 'adriana', text: INITIAL_MESSAGE },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function send(text: string) {
    if (!text.trim() || loading) return
    const trimmed = text.trim()
    setMessages(p => [...p, { id: Date.now().toString(), role: 'user', text: trimmed }])
    setInput('')
    setLoading(true)
    try {
      const res = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed }),
      })
      const data = await res.json()
      setMessages(p => [...p, { id: (Date.now() + 1).toString(), role: 'adriana', text: data.reply }])
    } catch {
      setMessages(p => [...p, {
        id: (Date.now() + 1).toString(),
        role: 'adriana',
        text: 'Could not reach the API. Make sure the backend is running on port 8000.',
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 px-5 py-4 border-b border-zinc-200 bg-white shrink-0">
        <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center text-white text-sm font-semibold">
          A
        </div>
        <div>
          <p className="text-sm font-semibold text-zinc-900">Adriana</p>
          <p className="text-xs text-zinc-400">Social Intelligence Analyst</p>
        </div>
        <div className="ml-auto flex items-center gap-1.5">
          <span className="live-dot" />
          <span className="text-xs text-zinc-400">Live</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-5 space-y-4 min-h-0">
        {messages.map(m => <Bubble key={m.id} msg={m} />)}
        {loading && <TypingBubble />}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions — only shown when no user messages yet */}
      {messages.length === 1 && (
        <div className="px-5 pb-3 flex flex-wrap gap-2 shrink-0">
          {SUGGESTIONS.map(s => (
            <button
              key={s}
              onClick={() => send(s)}
              className="text-xs text-zinc-600 bg-white border border-zinc-200 rounded-full px-3 py-1.5 hover:bg-zinc-50 hover:border-zinc-300 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="px-5 pb-5 shrink-0">
        <div className="flex gap-2 bg-white border border-zinc-200 rounded-xl px-4 py-3 focus-within:border-zinc-400 transition-colors">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send(input)}
            placeholder="Ask Adriana anything…"
            className="flex-1 bg-transparent text-sm text-zinc-900 placeholder-zinc-400 outline-none"
          />
          <button
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            className="w-7 h-7 rounded-lg bg-zinc-800 hover:bg-zinc-700 disabled:opacity-30 flex items-center justify-center transition-colors shrink-0"
          >
            <Send className="w-3.5 h-3.5 text-white" />
          </button>
        </div>
      </div>
    </div>
  )
}
