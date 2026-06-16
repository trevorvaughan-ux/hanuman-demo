// server.js — Hanuman backend service (Railway, brave-solace project)
// Real, runnable. Key lives ONLY in process.env.ANTHROPIC_API_KEY (Railway env var).
// Stateless: no conversation is stored server-side. Client sends history each turn.

const express = require("express");
const cors = require("cors");
const path = require("path");
const { HANUMAN_SYSTEM_PROMPT } = require("./hanuman-prompt");

const app = express();
app.use(express.json({ limit: "64kb" }));

// --- CORS: only the homepage may call this service ---
const ALLOWED_ORIGINS = [
  "https://www.hudsonseed.com",
  "https://hudsonseed.com",
];
app.use(cors({
  origin: (origin, cb) => {
    // allow same-origin / curl (no origin) and the homepage
    if (!origin || ALLOWED_ORIGINS.includes(origin)) return cb(null, true);
    return cb(new Error("Origin not allowed"));
  },
}));

// --- Config / caps ---
const MODEL = "claude-sonnet-4-6";
const MAX_TOKENS = 400;              // cost ceiling per reply (Hanuman speaks briefly)
const MAX_TURNS_PER_SESSION = 6;     // funnel + safety: a session is short
const DAILY_REQUEST_CAP = 2000;      // global circuit breaker (in-memory, see README)
const SESSION_IDLE_MS = 30 * 60 * 1000;

// --- In-memory state (resets on redeploy; README notes the production upgrade) ---
const sessions = new Map(); // sessionId -> { turns, last }
let dailyCount = 0;
let dailyStamp = new Date().toISOString().slice(0, 10);

function rollDaily() {
  const today = new Date().toISOString().slice(0, 10);
  if (today !== dailyStamp) { dailyStamp = today; dailyCount = 0; }
}

// --- PII scrub: strip obvious identifiers before anything reaches the API or logs.
// Regex catches the common cases. It is a reducer, not a guarantee (README is honest about this). ---
function scrubPII(text) {
  if (typeof text !== "string") return "";
  return text
    .replace(/[\w.+-]+@[\w-]+\.[\w.-]+/g, "[removed]")                         // emails
    .replace(/\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/g, "[removed]") // phones
    .replace(/\b\d{1,5}\s+[A-Za-z0-9.\s]{2,30}\s(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Lane|Ln|Dr|Drive)\b/gi, "[removed]"); // street addresses
}

// --- Gateway interceptor: kill clearly off-topic inputs at $0 (no API call). ---
// Honest design: this catches obvious cost-wasters cheaply. The SYSTEM PROMPT's hard
// walls are the real guardrail for anything subtle that gets through.
const OFF_TOPIC = [
  /\brecipe\b/i, /\bhomework\b/i, /\bmath\b/i, /\bessay\b/i,
  /\bwho won\b/i, /\bscore\b/i, /\bweather\b/i, /\bstock\b/i,
  /\bpresident\b/i, /\bcode\b/i, /\bpassword\b/i, /https?:\/\//i,
];
const REDIRECT = "Whoa, my monkey mind wants to chase that one! But you and I, we stay with the breath here. Let's take one slow breath in... and a long breath out. Feel that? That's your superpower. What would help your class right now: a calm-down breath, or a wake-up stretch?";

function isOffTopic(text) {
  return OFF_TOPIC.some((re) => re.test(text));
}

app.get("/healthz", (_req, res) => res.json({ ok: true }));

app.post("/api/hanuman", async (req, res) => {
  rollDaily();
  if (dailyCount >= DAILY_REQUEST_CAP) {
    return res.status(429).json({ error: "Hanuman is resting. Please try again tomorrow." });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;

  const { sessionId, messages } = req.body || {};
  if (!sessionId || !Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({ error: "Bad request." });
  }

  // Session turn cap (stateless: we only count, we don't store transcripts)
  const now = Date.now();
  let s = sessions.get(sessionId);
  if (!s || now - s.last > SESSION_IDLE_MS) s = { turns: 0, last: now };
  if (s.turns >= MAX_TURNS_PER_SESSION) {
    return res.json({ reply: "What a beautiful practice we just shared. Let's close together: I am happy. I am safe. I am brave. I am strong. I am love. Come find me again whenever your class needs a reset.", capped: true });
  }

  // Scrub + take only the latest user message text for the gate
  const last = messages[messages.length - 1];
  const lastText = scrubPII(last && last.content ? String(last.content) : "");
  if (isOffTopic(lastText)) {
    return res.json({ reply: REDIRECT, gated: true }); // $0 — no API call
  }

  // Build scrubbed, role-clean history (stateless: nothing persisted)
  const cleanMessages = messages
    .filter((m) => m && (m.role === "user" || m.role === "assistant"))
    .map((m) => ({ role: m.role, content: scrubPII(String(m.content)).slice(0, 1000) }));

  if (!apiKey) return res.status(503).json({ error: "Service not configured." });

  try {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: MAX_TOKENS,
        system: HANUMAN_SYSTEM_PROMPT,
        messages: cleanMessages,
      }),
    });

    if (!r.ok) {
      const detail = await r.text();
      console.error("Anthropic error", r.status, detail.slice(0, 200));
      return res.status(502).json({ error: "Hanuman couldn't catch his breath. Try once more." });
    }

    const data = await r.json();
    const reply = (data.content || [])
      .filter((b) => b.type === "text")
      .map((b) => b.text)
      .join("\n")
      .trim();

    s.turns += 1; s.last = now; sessions.set(sessionId, s);
    dailyCount += 1;

    return res.json({ reply, turn: s.turns, turnsLeft: MAX_TURNS_PER_SESSION - s.turns });
  } catch (err) {
    console.error("Handler error", err.message);
    return res.status(500).json({ error: "Something went sideways. Take a breath, try again." });
  }
});

// Serve the widget
app.use(express.static(path.join(__dirname, "public")));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Hanuman service on :${PORT}`));
