# TouchGrass — Architecture

## 1. Project Overview

**TouchGrass** is an outdoor activity website designed to encourage people to spend less time on screens and more time outside. Its chatbot uses a local open-weight language model first and deterministic Python rules as a fallback.

The user interacts with the chatbot, shares their available time, mood, preferences, or location type, and receives a simple outdoor mission or activity suggestion.

The chatbot remains a stateless Python service: it calls a local Ollama server
running an open-weight model when configured, and never stores conversation
history. If the model is unavailable or returns invalid output, the built-in
rule-based generator answers instead.

Mission generation enriches the existing authenticated `POST /api/chat/`
response; it does not add a second AI service or a new mission endpoint.
Validated mission metadata is additive to the fields already consumed by the
frontend. Mission start and optional completion are browser-only self-check-ins.

## Current implementation snapshot

The source of truth for this architecture is the current repository:

```text
frontend/
  index.html
  css/style.css
  js/app.js
  js/config.js
  js/mission-state.mjs
  js/mission-response.mjs
  tests/mission-state.test.mjs
backend/
  config/       Django settings, URL routing, generic API exception handling
  users/        Supabase bearer-token verification and user endpoints
  chatbot/      request/response serializers, context rules, Ollama adapter
  missions/     public sample mission endpoint
  manage.py
```

The API routes are `GET /api/auth/verify/`, `GET /api/auth/user/`,
`POST /api/chat/`, and `GET /api/missions/`. The two auth routes and chat
require a bearer token that Django verifies with Supabase Auth; the sample
mission list is public. `POST /api/chat/` accepts one message (maximum 400
characters), rejects client-supplied `history`, and returns the legacy
`{reply, mission}` contract with additive mission metadata. There are no app
models, stored chat transcripts, or mission activity records.

The frontend uses Supabase JS for email/password auth, session persistence,
token refresh, and logout. It sends the current access token to Django. The
backend derives user ID and email only from Supabase's verified response. The
`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `DJANGO_SECRET_KEY`,
`DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, and
`DJANGO_CORS_ALLOWED_ORIGINS` settings are environment-configured; browser
Supabase values and `API_BASE_URL` live in `frontend/js/config.js`. The
`.env.example` contains placeholders, not usable credentials.

For chat, the backend extracts supported context from the message, calls the
local Ollama `/api/chat` adapter when enabled, validates and normalizes the
model output, and applies application-selected category, difficulty, duration,
setting constraints, and safety text. On unavailable, timeout, or invalid
model output, the deterministic mission rules provide the response. The
response serializer validates both paths. Unexpected API exceptions are logged
server-side using only the request method/path and exception class (not
exception text or a traceback), then returned as a generic JSON error envelope.
The browser also checks that a successful response contains a minimally
complete mission before rendering it; malformed responses receive an inline
retryable error rather than being treated as a network outage.

Trust boundaries: browser values are input, not identity proof; Supabase
publishes only its browser-appropriate anon/publishable key; the Ollama model
is untrusted and cannot select final safety guidance; user messages are
processed per request and not persisted. Production HTTPS, HSTS, secure
cookies, allowed hosts/origins, and secrets still require deployment-specific
configuration. As of 2026-10-12, Django deployment checks report six security
warnings; no production deployment has been verified.

Later sections retain original design rationale and illustrative future
architecture. Where those aspirational examples conflict with this snapshot,
the current implementation snapshot takes precedence.

---

## 2. Technology Stack

### Frontend
- **HTML5** — page structure and content
- **CSS3** — styling, responsive design, animations, and layout
- **JavaScript** — frontend interactions, chatbot UI, API requests, and dynamic content

### Backend
- **Django** — main backend framework
- **Django REST Framework (DRF)** — REST APIs between frontend and backend
- **Python** — backend and chatbot development

### Authentication
- **Supabase Auth** — user authentication and session management
- Supabase can handle login, signup, and authentication tokens.
- Django verifies authenticated requests before allowing protected operations.

### Chatbot
The chatbot is built using **Python** and uses open-source/open-weight AI.

Implemented components:
- **Ollama** — local model execution (chosen framework)
- **`qwen2.5:3b`** — default open-weight model (Apache-2.0)
- **`chatbot/ai.py`** — small provider adapter with automatic rule-based fallback

No additional AI framework (Transformers, LangChain, FastAPI) is needed; the
adapter uses Python's standard library to call the local Ollama HTTP API, which
keeps `requirements.txt` unchanged.

### Database
- Django is configured with local SQLite for built-in Django components.
- The project apps declare no application models or migrations; chat and
  mission self-check-in state are not stored.
- Supabase is used for Auth, not as a project data store. A different database
  would be a future design decision, not part of this implementation.

---

## 3. High-Level Architecture

```text
                    ┌─────────────────────────┐
                    │        USER             │
                    │   Browser / Mobile Web  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       FRONTEND          │
                    │     HTML + CSS + JS     │
                    │                         │
                    │  • Landing Page         │
                    │  • Login / Signup       │
                    │  • Chatbot UI            │
                    │  • Outdoor Missions      │
                    └────────────┬────────────┘
                                 │
                       REST API Requests
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │        DJANGO           │
                    │       BACKEND           │
                    │                         │
                    │  • REST API             │
                    │  • Authentication Check │
                    │  • User Requests        │
                    │  • Chatbot Requests     │
                    │  • Business Logic       │
                    └───────┬─────────┬───────┘
                            │         │
                Auth        │         │ Chat Request
                            │         │
                            ▼         ▼
                  ┌──────────────┐  ┌──────────────────┐
                  │   SUPABASE   │  │  PYTHON CHATBOT  │
                  │              │  │                  │
                  │ • Auth       │  │ • Rules (fallback│
                  │ • Sessions   │  │ • AI adapter     │
                  │ • Tokens     │  │   (chatbot/ai.py)│
                  └──────────────┘  └────────┬─────────┘
                                             │
                                             ▼
                                  ┌────────────────────┐
                                  │ Open-Weight Model  │
                                  │                    │
                                  │ Local Ollama       │
                                  │ (qwen2.5:3b)       │
                                  └────────────────────┘
```

---

## 4. Frontend Architecture

The frontend is intentionally lightweight.

### Technologies

```text
HTML5
CSS3
JavaScript
```

### Main frontend sections

```text
frontend/
│
├── index.html
├── css/style.css
├── js/app.js
├── js/config.js
├── js/mission-state.mjs
├── tests/mission-state.test.mjs
└── assets/ (leaf.svg, park.svg)
```

### Frontend responsibilities

The frontend handles:

- Displaying the website
- Login/signup interface
- Chatbot interface
- Sending user messages to Django
- Displaying chatbot replies and missions
- Showing generated outdoor missions
- Responsive design
- UI state changes
- Logout
- Basic client-side validation

The frontend should **not** contain secret API keys or AI model credentials.

---

## 5. Django Backend Architecture

Django acts as the main application backend.

Current structure:

```text
backend/
│
├── manage.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── users/
│   ├── authentication.py
│   ├── views.py
│   ├── urls.py
│   └── serializers.py
│
├── chatbot/
│   ├── views.py
│   ├── urls.py
│   ├── services.py
│   ├── mission_rules.py
│   ├── ai.py
│   ├── prompts.py
│   ├── serializers.py
│   └── tests.py
│
└── missions/
    ├── views.py
    └── urls.py
```

### Django responsibilities

Django currently:

1. Receive requests from the frontend.
2. Validate requests.
3. Verify Supabase authentication.
4. Process application logic.
5. Send chatbot requests to the Python chatbot service.
6. Return chatbot responses to the frontend.
7. Do not store application chat, mission, or profile history.

---

## 6. Authentication Architecture

Authentication is handled using **Supabase Auth**.

### Login flow

```text
User
 │
 ▼
Frontend Login / Signup
 │
 ▼
Supabase Auth (email + password)
 │
 ├── Access token + refresh token
 │
 ▼
Supabase JS session (browser storage)
 │
 ▼
Authorization: Bearer <access token>
 │
 ▼
Django REST API
 │
 ▼
Supabase Auth /auth/v1/user verification
 │
 ▼
Verified user-scoped API response
```

### Important rule

Supabase handles authentication.

Django handles application authorization and protected API access.

The frontend should never trust a username or user ID supplied directly by the browser.
Django verifies each access token with Supabase Auth and derives the API user identity
from that verified response. The Supabase publishable/anon key may be used in the
frontend; the service-role key must never be exposed there.

---

## 7. Chatbot Architecture

The chatbot is the main interaction feature of TouchGrass. Its implementation asks a
local open-weight model first and uses deterministic Python rules as a fallback.

The chatbot should be focused specifically on helping users get outside.

### Example

User:

> "I have 45 minutes and I'm feeling stressed."

Chatbot:

> "Try a 30–40 minute walk somewhere with trees or open space. Leave your phone in your pocket and notice three things you normally overlook."

### Chatbot flow

```text
User Message
     │
     ▼
Chatbot UI
     │
     ▼
JavaScript API Request + Supabase bearer token
     │
     ▼
Django /chat API
     │
     ▼
Stateless mission service: context extraction → open-weight model
(chatbot/ai.py → local Ollama); any failure → rule-based generator
     │
     ▼
Django
     │
     ▼
Frontend Chatbot UI
```

---

## 8. Python Chatbot Layer

The chatbot logic should be separated from Django views so it can be changed or upgraded easily.

Example:

```text
chatbot/
│
├── services.py
├── prompts.py
├── ai.py
└── tests.py
```

### `services.py`

Responsible for:

- Extracting available time, mood, activity, energy, setting preference, and constraints
- Asking the open-weight model for a mission first (`chatbot/ai.py`)
- Falling back to the rule-based generator whenever the model fails
- Validating the mission category, difficulty, duration, setting, and safety policy
- Returning the legacy mission fields plus additive category, difficulty, and safety fields

### `ai.py`

The open-weight model adapter (Phase 6). It reads AI settings, calls the local
Ollama server with structured-JSON instructions, parses and normalizes the model
output, validates it against the mission serializer, and raises `AIError` on any
failure so `services.py` can fall back to the rules. No AI/model logic lives in
the Django view.

### `prompts.py`

Contains the model-facing system prompt and the structured-JSON mission prompt
that are sent to the open-weight model.

Example concept:

```text
You are TouchGrass AI.

Your goal is to help users spend meaningful time outdoors.

Give simple, realistic outdoor activities.

Prefer activities that:
- require little or no equipment
- can be completed in the user's available time
- encourage users to put their phone away
- are safe and accessible

Keep responses short and actionable.
```

---

## 9. Open-Source AI

Open-source/open-weight AI is important to the project because the chatbot should not depend entirely on a closed AI API.

Implemented architecture (Phase 6):

```text
Django
   │
   ▼
Python Chatbot Service (services.py)
   │
   ▼
Model adapter (chatbot/ai.py)
   │
   ▼
Local Ollama server (http://127.0.0.1:11434)
   │
   ▼
Open-Weight Model (qwen2.5:3b, Apache-2.0)
   │
   ▼
Structured JSON mission → validated → response
```

If any step fails (server down, timeout, invalid JSON, failed validation),
`services.py` logs a warning and serves a mission from the rule-based generator
instead. The model is therefore replaceable without changing the view, the API,
or the frontend.

### Selected model: `qwen2.5:3b`

| Criterion | Value |
|---|---|
| License | Apache-2.0 (open-weight and OSI-approved open source) |
| Size | ~3B parameters, ~2 GB download |
| Hardware | Runs on a normal CPU-only laptop; ~3–4 GB free RAM |
| Runner | Ollama (local, no API key, no data leaves the machine) |
| Why | Small enough for laptops, unambiguous license, good instruction following for structured JSON |

Alternatives considered: `gemma2:2b` (smaller), `llama3.2:3b` (Llama 3.2
Community License), `mistral:7b` / `qwen2.5:7b` (higher quality, more RAM).
Model parameters used: `format: "json"`, `temperature: 0.6`, `num_predict: 400`,
`stream: false`, request timeout `AI_TIMEOUT_SECONDS` (default 10s).

The model should be replaceable without changing the frontend.

---

## 10. API Architecture

The frontend communicates with Django through Django REST Framework APIs. The chat
endpoint asks the local open-weight model for a mission first and falls back to
server-side rules when the model is unavailable.

### Example endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/auth/verify/` | Verify authenticated user |
| GET | `/api/auth/user/` | Get current user information |
| POST | `/api/chat/` | Send message to chatbot |
| GET | `/api/missions/` | Get outdoor missions |

Authentication verification and the user endpoint require a Supabase bearer token.
The missions list is public. Chat requires a verified user. Signup, login, refresh, and
logout are performed by the Supabase browser SDK; Django does not proxy passwords or
create a second session.

---

## 11. Chat API Example

### Request

```json
{
  "message": "I have one hour and want something relaxing."
}
```

### Django processing

```text
Request
   ↓
Authentication check
   ↓
Validate message
   ↓
Extract context (time, mood, activity, energy, setting, constraints)
   ↓
Open-weight model via chatbot/ai.py (Ollama, JSON mode)
   │        ↘ any failure → rule-based mission generator
   ↓
Validate mission against the serializer
   ↓
Return JSON
```

### Response

```json
{
  "reply": "I picked a low-pressure mission to help you slow down outside.",
  "mission": {
    "title": "The quiet reset",
    "duration": "40 minutes",
    "duration_minutes": 40,
    "activity": "Take a gentle walk somewhere with trees, fresh air, and room to breathe. Let the pace stay easy.",
    "instructions": [
      "Choose a familiar nearby route with a comfortable place to pause.",
      "Walk at an easy pace and let your shoulders relax.",
      "Notice one sound you usually miss and one thing that feels lighter."
    ],
    "description": "Take a gentle walk somewhere with trees, fresh air, and room to breathe. Let the pace stay easy.",
    "challenge": "Notice one sound you usually miss and one thing that feels lighter.",
    "bring": "Comfortable shoes; no special gear is needed.",
    "setting": "outdoors",
    "energy_level": "low",
    "category": "relaxation_mindfulness",
    "difficulty": "Easy",
    "safety_considerations": "Choose a familiar place, follow local guidance and current conditions, and stop or head home if you feel uncomfortable.",
    "type": "outdoor_mission"
  }
}
```

---

Each request is stateless: Django does not accept or store conversation history.
Request validation and response serialization preserve the API's standard error
envelope and the legacy fields expected by the frontend. The new mission fields
are additive. The frontend renders instructions, suggested setting, items, and
safety considerations; users can start a mission and optionally mark it complete
in client-side state. That check-in is not persisted or independently verified.

## 12. Data Flow

### Normal website request

```text
Browser
   ↓
HTML / CSS / JavaScript
   ↓
Django REST API
   ↓
Business Logic
   ↓
Response
   ↓
Browser
```

### Chatbot request

```text
Browser
   ↓
JavaScript
   ↓
Django REST API (verified Supabase bearer token)
   ↓
Context extraction (services.py)
   ↓
Open-weight model adapter (chatbot/ai.py → local Ollama)
   │        ↘ unavailable / invalid → rule-based generator
   ↓
Django
   ↓
JavaScript
   ↓
Chatbot UI
```

The model call is synchronous with a short timeout; the rule-based generator
always keeps the endpoint working.

### Authentication request

```text
Browser
   ↓
Supabase Auth
   ↓
Session / Token
   ↓
Django API
   ↓
Token Verification
   ↓
Protected Response
```

---

## 13. Security

The application should follow basic security practices.

### Frontend

- Do not store secret keys in JavaScript.
- Do not expose AI model credentials.
- Validate user input.
- Use HTTPS in production.

### Django

- Keep `SECRET_KEY` outside the repository.
- Store credentials in environment variables.
- Enable Django security settings in production.
- Validate API input.
- Verify authentication tokens.
- Apply appropriate CORS and CSRF configuration.

### Supabase

- Keep public and secret keys separate.
- Never expose the Supabase service-role key in frontend code.
- Use Supabase policies where database access is enabled.

---

## 14. Environment Variables

Server configuration belongs in an ignored local `.env` or the deployment
environment. `.env.example` is a placeholder template; the browser Supabase
URL and publishable/anon key are separately configured in `frontend/js/config.js`.
The publishable key is not a service-role secret.

Example:

```env
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080

SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Open-weight AI (no secrets — local Ollama only)
AI_PROVIDER=ollama
AI_MODEL=qwen2.5:3b
AI_BASE_URL=http://127.0.0.1:11434
AI_TIMEOUT_SECONDS=10
```

`.env` must be added to `.gitignore`.

For production, set `DJANGO_DEBUG=False`, a unique high-entropy
`DJANGO_SECRET_KEY`, exact `DJANGO_ALLOWED_HOSTS`, and the deployed frontend
origin in `DJANGO_CORS_ALLOWED_ORIGINS`. The current settings do not expose
environment variables for HSTS, HTTPS redirect, or secure cookie flags; these
must be set in reviewed deployment-specific Django settings or a correctly
configured TLS-terminating proxy. Do not blindly turn on HSTS or redirects for
plain-HTTP local development. `manage.py check --deploy` currently reports six
warnings, and the application has not been deployed or production-tested.

---

## 15. Deployment Architecture

### Development

```text
Browser
   │
   ├── Frontend
   │
   ▼
Django localhost
   │
   ▼
Python Chatbot Service
   │
   ▼
Local Ollama + open-weight model (AI_PROVIDER=ollama)
   └──► fallback: rule-based generator
```

No model runs inside Django; Ollama runs as a separate local process.

### Production

```text
User Browser
      │
      ▼
Frontend Hosting
      │
      ▼
Django Backend
      │
      ├──────────► Supabase Auth
      │
      ▼
Python Chatbot Service
      │
      ├──────────► Ollama host (open-weight model, private network only)
      │
      └──► fallback: rule-based generator
```

The model adapter only needs `AI_BASE_URL`/`AI_MODEL` to point at any Ollama
host, so the model stays replaceable in production too.

---

## 16. Why This Architecture?

### Simple frontend

HTML, CSS, and JavaScript keep the frontend lightweight and easy to understand.

### Django backend

Django provides:

- Structured backend development
- REST API support
- Authentication integration
- Business logic
- Easy future expansion

### Supabase Authentication

Supabase removes the need to build authentication completely from scratch while still giving the project a modern authentication system.

### Python chatbot layer

Python has a large ecosystem for AI and machine learning. Separating the chatbot from Django makes it easier to change models and frameworks later.

### Open-weight AI

Using an open-weight model gives the project more control over:

- Privacy
- Model selection
- Local inference
- Cost
- Customization
- Future fine-tuning

---

## 17. Scalability

The initial version should remain simple.

Future versions can add:

```text
User Profiles
     │
     ├── Activity History
     ├── Favourite Activities
     ├── Personal Preferences
     └── Outdoor Goals

AI
     │
     ├── Better Personalization
     ├── Local Recommendations
     ├── Weather-aware Missions
     └── Multiple Open Models
```

The chatbot service should remain modular so the AI model can be swapped without rebuilding the frontend.

---

## 18. MVP Architecture

For the first working version, only the following components are required:

```text
HTML
CSS
JavaScript
     │
     ▼
Django
     │
     ├── Supabase Authentication
     │
     └── Python Chatbot
              │
              ▼
        (Phase 6: Open-Weight Model)
```

The frontend and backend are separate local development servers. Configure CORS to
allow only the frontend's development/production origin. The frontend sends Supabase
access tokens in the `Authorization` header; Django validates them through Supabase
before serving protected profile or chatbot endpoints.

### MVP Features

- Landing page
- Login/signup
- Chatbot interface
- Rule-based outdoor missions
- "I'm Going Outside" button
- Responsive design
- Basic REST API
- Open-weight AI integration

No complex database, social system, ranking system, or recommendation engine is required for the initial version.

---

## 19. Project Principle

The architecture follows one main principle:

> **The AI should help the user leave the screen, not keep the user on it.**

TouchGrass should therefore keep AI interactions short, useful, and action-oriented.

The ideal chatbot response ends with the user closing the website and going outside.
