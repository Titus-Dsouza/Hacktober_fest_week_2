# 🌿 TouchGrass

> **Go outside. We'll handle the plan.**

TouchGrass is an outdoor activity companion built around the idea of **spending less time on screens and more time outside**. Its static HTML/CSS/JavaScript frontend uses Supabase Auth and sends authenticated chat requests to a Django REST API. The chatbot asks a local open-weight AI model (via Ollama) for missions and falls back to deterministic Python rules when the model is unavailable.

Tell TouchGrass how you're feeling, how much time you have, and what kind of activity you want. The Django chatbot service turns that request into a structured outdoor mission using an open-weight model when available.

---

## 🎯 Why TouchGrass?

AI is becoming a bigger part of our daily lives, but not every problem needs more screen time.
People who want to go outside may still need a low-pressure idea that fits the
time, energy, activity, and access needs they choose to share. TouchGrass is
intended for anyone looking for a short, practical starting point; it does not
require precise location access or paid services.

TouchGrass takes the opposite approach:

**Get a plan → Leave the screen.**

The goal is to make the screen the **shortest part of the experience**.

---

## ✨ Features

- 🌿 Personalized outdoor missions from a local AI model or deterministic fallback
- 🗺️ Missions adapt to available time, mood, activity, setting, energy, and supported constraints
- 🏕️ Walking, nature observation, mindfulness, light movement, gardening, and social categories
- ✅ Clear instructions, estimated difficulty, suggested setting, items, and safety notes
- 📍 Client-side start and optional self-reported completion check-ins; no activity history is saved
- 📵 Challenges designed to reduce screen time
- 💬 Simple conversational chatbot
- 📱 Responsive design for mobile and desktop
- 🔓 Open-weight AI with automatic rule-based fallback
- 🔐 Supabase sign-in for personalized chat requests

---

## 📷 Screenshots and demo

Screenshots and a recording have **not** been captured yet. Add genuine,
redacted browser screenshots here after configuring Supabase and verifying the
flows:

- `[Desktop landing page — capture pending]`
- `[Mobile landing page — capture pending]`
- `[Personalized mission card — capture pending]`
- `[Started mission and rule-based fallback — capture pending]`

The repository-controlled demo script, capture checklist, and submission
checklist are in [`SUBMISSION.md`](SUBMISSION.md). No live service or submission
is implied by these placeholders.

---

## 💡 Example

**You:**

> I have one hour and want something relaxing.

**Example rule-based mission:**

> 🌿 **Your Outdoor Mission**
>
> Take a gentle walk somewhere with trees, fresh air, and room to breathe. Let the pace stay easy.
>
> **About 40 minutes · Relaxation & mindfulness · Easy**
>
> Choose a familiar nearby route with a comfortable place to pause. Walk at an easy pace, then notice one sound you usually miss.
>
> **Where:** A nearby park, garden, campus, or familiar outdoor space.
>
> **Bring:** Comfortable shoes; no special gear is needed.
>
> **Keep in mind:** Choose a familiar place and stop or head home if you feel uncomfortable.

The idea is simple:

```text
Ask TouchGrass
   ↓
Get a mission
   ↓
Close the website
   ↓
🌿 Go outside
```

---

## 🧠 Open AI at the Core

TouchGrass uses an **open-weight/open-source AI model** rather than making a closed AI service the core of the project. The Django chatbot first asks a **local Ollama server** running an open-weight model (`qwen2.5:3b` by default) for a structured outdoor mission. If the model is unavailable, times out, or returns anything invalid, the chatbot automatically falls back to its built-in rule-based mission generator, so the app keeps working without AI. Messages are validated and processed for one request only; the server does not store conversation history.

This approach provides:

- More control over the AI
- Ability to experiment with different models
- Running inference locally
- Greater control over user data
- Lower dependency on a single AI provider
- Freedom to modify how the assistant behaves

The model powers the outdoor mission generator behind the unchanged `POST /api/chat/` API.

---

## 🛠️ Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript

### AI

- Open-weight/open-source language model (`qwen2.5:3b`, Apache-2.0)
- Local inference through [Ollama](https://ollama.com)
- Automatic rule-based fallback when the model is unavailable

### Backend

A Django REST API connects the frontend to the Python chatbot service. The chatbot
service contains a model adapter (`backend/chatbot/ai.py`); the frontend API is
unchanged.

The MVP is intentionally kept simple.

---

## 📁 Project Structure

```text
TouchGrass/
│
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   ├── js/ (app, config, mission state/response)
│   └── assets/
├── backend/
│   ├── manage.py
│   ├── config/
│   ├── chatbot/
│   ├── missions/
│   └── users/
├── requirements.txt
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
├── Design.md
├── architecture.md
├── PHASE.md
├── PRD.md
├── README.md
├── SUBMISSION.md
└── scripts/api_smoke_load.py
```

There is currently no `LICENSE` file. The project owner must choose and add a
license before describing the repository as licensed for reuse.

The frontend uses Supabase Auth for account sessions and calls the Django API for
chat-generated missions. The mission generator asks a local open-weight model first
and falls back to built-in rules when the model is unavailable (see
[Local open-weight AI (Ollama)](#local-open-weight-ai-ollama)).

---

## 🚀 Getting Started

### Requirements

- Python 3.12 or newer
- A Supabase project for signup, login, and email confirmation
- A modern browser with JavaScript module and native `<dialog>` support
- Node.js only for client-state tests; the frontend has no npm build step
- Optional: [Ollama](https://ollama.com) for local open-weight AI missions
  (the app works without it via the rule-based fallback)

### 1. Configure the project

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Edit `.env` and set a unique `DJANGO_SECRET_KEY` before using Django outside local
development. Set `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and the frontend origin in
`.env`; these configure the Django API.

In `frontend/js/config.js`, set the same Supabase project URL and its **publishable
(anon) key**, along with the Django API URL. The publishable key is intended for browser
use; never put a service-role key in frontend files. In Supabase Authentication settings,
enable email/password sign-in and add your frontend origin (for example,
`http://localhost:8080`) to the allowed Site URL / redirect URLs. Configure email
confirmation as desired in Supabase.

`SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env` are used by Django to verify
access tokens. The browser configuration in `frontend/js/config.js` is separate
and must point to the same Supabase project. The frontend loads Supabase JS
from `esm.sh`, so authentication setup requires a network connection. Never put
a service-role key in either file.

### 2. Run the website

In a second terminal, from the project root:

```bash
npm run dev
```

This runs the static frontend using Python's built-in HTTP server; no npm
packages need to be installed. Alternatively, run
`python3 -m http.server 8080 --directory frontend`. Open
<http://localhost:8080>. Supabase's browser client is loaded from esm.sh; use a
network connection. Sign up or sign in to get missions from the Django API.

### 3. Start the Django API

With the virtual environment active, from the project root:

```bash
.venv/bin/python backend/manage.py check
.venv/bin/python backend/manage.py migrate
.venv/bin/python backend/manage.py runserver
```

The frontend and API run separately during local development. Django exposes:

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/api/auth/verify/` | Supabase bearer token | Verify the current session |
| GET | `/api/auth/user/` | Supabase bearer token | Get the verified user's email and ID |
| POST | `/api/chat/` | Supabase bearer token | Validate a message and return a structured outdoor mission |
| GET | `/api/missions/` | Public | List sample missions |

`POST /api/chat/` accepts `{"message":"I have 20 minutes and want something relaxing"}`
and returns `{"reply":"…","mission":{…}}`. The mission object includes `title`,
`duration`, `duration_minutes`, `activity`, exactly three `instructions`,
`description`, `challenge`, `bring`, `setting`, `energy_level`, `category`,
`difficulty`, `safety_considerations`, and `type`. The legacy response fields
remain present for the existing frontend. Client-supplied `history` is rejected;
the service does not store conversation history.

Protected endpoints accept `Authorization: Bearer your_access_token`. Django
verifies tokens with Supabase Auth; it does not trust user IDs supplied by the browser.
The chat endpoint asks the local open-weight model for a mission first and falls back to
deterministic server-side rules when the model is unavailable or returns invalid output.
It extracts available time, mood/energy,
activity, setting preference, energy, and recognized constraints. The structured
mission includes `title`, `duration`, `duration_minutes`, `activity`, three
`instructions`, `category`, `difficulty`, `setting`, `bring`, and
`safety_considerations`, plus the existing `description`, `challenge`, `energy_level`,
and `type` fields. The original response fields remain available; the newer metadata
is additive. Categories are walking/exploring, nature observation,
relaxation/mindfulness, light movement, gardening/nature care, and social outdoors.
Difficulty is Easy, Moderate, or Challenging; the application applies conservative
limits based on stated energy. API errors use an
`{ "error": { "code", "message", "details" } }` response envelope.

The mission card's start action updates browser-only state. Users may mark a started
mission complete as a self-check-in; TouchGrass does not save, verify, or award
rewards for real-world activity. Failed requests show an inline error with a retry path.

Run backend and frontend checks with:

```bash
.venv/bin/python backend/manage.py check
.venv/bin/python backend/manage.py makemigrations --check --dry-run
.venv/bin/python backend/manage.py showmigrations --plan
.venv/bin/python backend/manage.py test users chatbot missions
node --test frontend/tests/mission-state.test.mjs
node --check frontend/js/app.js
node --check frontend/js/config.js
node --check frontend/js/mission-state.mjs
node --check frontend/js/mission-response.mjs
.venv/bin/python backend/manage.py check --deploy
```

The backend suite uses mocked Supabase and Ollama/network calls, so it does not
require live credentials or a running model. Client tests use Node's built-in
test runner and require no additional package. On 2026-10-12,
`test users chatbot missions` passed all 61 tests, the 4 client-state/API-shape tests
passed, Django's system check passed, and no model migrations were pending.

**QA limitations:** No local `.env`/configured Supabase project, Ollama
executable, or browser automation tool was available during verification.
Real sign-in, authenticated browser flow, model inference, and rendered mobile,
tablet, desktop, and cross-browser layouts remain unverified and require manual
setup/testing. `.venv/bin/python backend/manage.py check --deploy` reports
production configuration warnings for HSTS/SSL redirect, secure cookies, the
local fallback secret key, and `DEBUG=True`; configure TLS-aware production
settings before deployment. These warnings are not expected to be resolved by
enabling HTTPS-only flags in local development.
No production load, deployed HTTPS, or rate-limiting/abuse-control behavior has
been tested.

### Lightweight local API smoke/load check

This optional standard-library check makes 20 requests to the **public sample
missions endpoint only**, using four workers. It is not a test of authenticated
chat, Ollama, a production server, or deployment capacity:

1. Start Django with `.venv/bin/python backend/manage.py runserver`.
2. In another terminal run `.venv/bin/python scripts/api_smoke_load.py`.

The script is restricted to local loopback HTTP and has no third-party
dependencies. Its timing output is observational; no performance target is
implied.

### Local open-weight AI (Ollama)

The chatbot's default model is **`qwen2.5:3b`**, run locally with
[Ollama](https://ollama.com):

| | |
|---|---|
| **Model** | `qwen2.5:3b` (Qwen2.5 3B Instruct) |
| **License** | Apache-2.0 — weights are downloadable, so it qualifies as open-weight **and** open-source AI |
| **Why selected** | 3B parameters is small enough for a normal laptop, Apache-2.0 avoids license ambiguity, and it follows the structured-JSON instruction well |
| **Approx. requirements** | ~2 GB download, ~3–4 GB free RAM, CPU-only is fine (GPU optional) |
| **How it runs** | Local Ollama server on `http://127.0.0.1:11434`; when configured locally, mission inference is sent to that server. Supabase authentication still uses its configured service. |

Setup:

```bash
# 1. Install Ollama (macOS/Linux): https://ollama.com/download
# 2. Pull the model (~2 GB)
ollama pull qwen2.5:3b
# 3. Start the server if it is not already running (the macOS/Windows app does this)
ollama serve
# 4. Sanity check
ollama run qwen2.5:3b "Reply with JSON: {\"ok\": true}"
```

Then configure Django in `.env` (defaults shown; no secrets involved):

```env
AI_PROVIDER=ollama            # set to rule_based to disable the model entirely
AI_MODEL=qwen2.5:3b
AI_BASE_URL=http://127.0.0.1:11434
AI_TIMEOUT_SECONDS=10
```

Lighter/heavier alternatives: `gemma2:2b` (smaller), `llama3.2:3b` (Llama 3.2
Community License), `qwen2.5:7b` or `mistral:7b` (better quality, more RAM).
Set `AI_MODEL` and `ollama pull` the matching name.

**AI request flow:** `POST /api/chat/` → context extraction → `chatbot/ai.py`
sends the system prompt + extracted context to Ollama (`/api/chat`, JSON mode) →
response is parsed, normalized, and validated against the mission serializer →
`{ reply, mission }` returned to the frontend.

**Fallback:** if Ollama is unreachable, times out, or returns invalid output, the
service logs a warning and serves a mission from the built-in rule-based
generator. The API shape never changes and the app never fails because of the model.

**Testing:** `.venv/bin/python backend/manage.py test users chatbot missions`
passed 61 tests on 2026-10-12, including AI configuration, successful/malformed/unavailable
model responses, structured mission validation, personalization, fallback, and
the `/api/chat/` response structure — all with model/network calls mocked, so
the suite never needs a running model. The client-side start/completion
transitions are covered by `node --test frontend/tests/mission-state.test.mjs`.

### Authentication behavior

Signup, password login, session persistence/refresh, and logout are delegated to
the Supabase browser SDK. The client sends its access token to protected Django
routes; Django calls Supabase Auth's user-verification endpoint and derives the
user identity from that verified response. The backend does not accept a
browser-supplied user ID as proof of identity. The frontend's publishable/anon
key is public configuration, not a service-role secret. Real signup, token
refresh, logout, and protected browser requests remain unverified until a
project owner configures Supabase and tests them in a browser.

### Troubleshooting

| Symptom | Check |
|---|---|
| Frontend says Supabase is not configured | Set the project URL and publishable/anon key in `frontend/js/config.js`. |
| Django returns `503` for a protected request | Set matching `SUPABASE_URL` and `SUPABASE_ANON_KEY` in the server `.env`; verify the API can reach Supabase Auth. |
| Browser request is blocked by CORS | Set `DJANGO_CORS_ALLOWED_ORIGINS` to the exact frontend origin, including scheme and port, then restart Django. |
| Ollama connection warning | Start Ollama and ensure `AI_BASE_URL`/`AI_MODEL` match the installed model, or set `AI_PROVIDER=rule_based`. |
| Frontend cannot reach the API | Start Django on the URL configured by `API_BASE_URL` in `frontend/js/config.js`. |
| Supabase JS fails to load | Check network access to `esm.sh`, project URL, browser console, and Supabase email/password settings. |

For project requirements, contributor checks, and the short demo/capture plan,
see [`PRD.md`](PRD.md), [`CONTRIBUTING.md`](CONTRIBUTING.md), and
[`SUBMISSION.md`](SUBMISSION.md).

---

## 🎨 Design

TouchGrass follows a:

**Minimal • Natural • Modern • Friendly**

design language.

The UI uses:

- Warm cream backgrounds
- Forest green
- Sage green
- Fresh green accents
- Rounded cards
- Simple typography
- Minimal navigation
- Large outdoor imagery

See [`Design.md`](Design.md) for the complete design specification.

---

## 🗺️ Roadmap

### MVP

- [x] Project concept
- [x] UI/UX design
- [x] Project documentation
- [x] Landing page
- [x] Chatbot UI
- [x] Open-weight AI integration
- [x] Rule-based outdoor mission generation
- [x] Personalized mission details, categories, and difficulty
- [x] Lightweight client-side mission start/completion check-in
- [x] Responsive design implementation

### Future Ideas

- 📍 Location-aware recommendations
- 🌦️ Weather-aware missions
- 🐦 Bird identification
- 🌱 Plant identification
- 🥾 Hiking suggestions
- 🏃 Running/walking routes
- 🏆 Outdoor challenges and streaks
- 📵 Screen-free mode
- 📴 Fully offline AI experience

---

## 🌍 The TouchGrass Philosophy

Most AI products try to keep you on the screen longer.

TouchGrass tries to do the opposite.

```text
┌───────────────────────────┐
│                           │
│       Ask TouchGrass      │
│            ↓              │
│       Get a mission       │
│            ↓              │
│       Close the app       │
│            ↓              │
│        🌿 Go outside      │
│                           │
└───────────────────────────┘
```

> **The best AI interaction might be the one that gets you to stop using AI.**

---

## 🤝 Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for development setup, checks, and
project constraints. Contributions are welcome; the project has not yet added a
license file.

---

## 📜 License

No license file has been added yet. Ask the project owner to select a license
before redistributing or contributing under assumed reuse terms.

---

## 🌿 Built for Hacktoberfest

TouchGrass is being prepared for a Hacktoberfest submission. The target event,
its current rules, eligibility, deadline, and submission status have not been
verified here; no project entry has been submitted.

**Less screen. More outside.**

🌿 **TouchGrass**
