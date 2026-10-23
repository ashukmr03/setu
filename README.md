# Setu — Government Scheme Voice Agent

A WhatsApp voice agent that helps Indian citizens discover and apply for government welfare schemes.

**User sends voice note → Agent transcribes → Retrieves verified scheme info → Replies with text + voice note in the user's language (Hindi / Kannada / English)**

---

## Stack (zero API cost)

| Component | Tool | Cost |
|---|---|---|
| Backend | FastAPI on Render | Free |
| LLM | Gemini 1.5 Flash | Free (1500 req/day) |
| STT + TTS | ElevenLabs (1 month free) | Free |
| Vector store | ChromaDB local | Free |
| Embeddings | sentence-transformers | Free (local) |
| WhatsApp | Meta Cloud API (test number) | Free |

---

## Local Setup

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env file and fill in values
copy .env.example .env

# 4. Run the server
uvicorn app.main:app --reload --port 8000
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | From https://aistudio.google.com |
| `ELEVENLABS_API_KEY` | From https://elevenlabs.io |
| `WHATSAPP_TOKEN` | Meta app permanent access token |
| `WHATSAPP_PHONE_NUMBER_ID` | From Meta WhatsApp API setup page |
| `WHATSAPP_APP_SECRET` | From Meta App Settings → Basic |
| `WHATSAPP_VERIFY_TOKEN` | Any string you choose (paste same in Meta webhook config) |

---

## Meta WhatsApp Setup (after deploying to Render)

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create App → Business → Add WhatsApp product
3. Go to WhatsApp → Configuration → Edit Webhook
4. Webhook URL: `https://your-render-url.onrender.com/webhook`
5. Verify Token: `setu_verify_2024` (or whatever you set in `.env`)
6. Subscribe to: `messages`
7. Copy Phone Number ID and generate Token from the API Setup page

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Project Structure

```
setu/
├── app/
│   ├── main.py              # FastAPI app, webhook routes
│   ├── config.py            # Environment config
│   ├── agent/
│   │   ├── orchestrator.py  # Main pipeline coordinator
│   │   ├── llm.py           # Gemini 1.5 Flash integration
│   │   └── session.py       # Per-user conversation state
│   ├── knowledge/
│   │   ├── schemes.py       # Verified scheme records
│   │   └── vector_store.py  # ChromaDB RAG store
│   ├── voice/
│   │   └── pipeline.py      # STT + TTS + OGG conversion
│   ├── whatsapp/
│   │   ├── client.py        # WhatsApp Cloud API client
│   │   └── handler.py       # Webhook event handler
│   └── security/
│       ├── guardrails.py    # Input/output safety checks
│       ├── rate_limiter.py  # Per-user rate limiting
│       └── webhook_auth.py  # HMAC signature verification
└── tests/
    └── test_security.py     # All security tests
```
