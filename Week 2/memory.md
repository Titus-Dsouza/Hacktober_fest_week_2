# TouchGrass Project Memory

> Persistent project context for contributors and AI assistants. Use this file to
> avoid inventing implementation details or reporting planned work as completed.

## How to use this file

- Treat statements under **Current documented state** as facts supported by the
  repository documentation or visible project structure.
- A checkbox in `PHASE.md` records the project's stated progress; it does not
  prove that a feature has been tested or works in the current environment.
- Do not claim that a command, test, deployment, integration, or user flow works
  unless it has actually been run and its result observed.
- When code and documentation disagree, inspect the implementation and update
  the relevant documentation. Until then, call out the discrepancy instead of
  guessing.
- Update this file when a phase meaningfully changes. Record completed work,
  evidence, and remaining blockers separately.

## Project identity

- **Name:** TouchGrass
- **Purpose:** Help people spend less time on screens and more time outdoors by
  giving them short, personalized outdoor missions.
- **Product principle:** “Use AI → Get a plan → Leave the screen.”
- **Current documented architecture:** Static HTML/CSS/JavaScript frontend,
  Django REST API backend, and Supabase Auth for account sessions.
- **AI status:** Open-weight AI integration (Phase 6) is implemented: the chat
  service calls a local Ollama server running `qwen2.5:3b` first and falls back
  to the rule-based generator on any failure. Real local inference was not
  verified in the implementation environment (Ollama not installed there).

## Current documented state

The following is based on `PHASE.md`, `README.md`, and the repository structure
as last reviewed on 2026-10-12. It is documentation-backed status, not a claim
that each feature has been independently tested.

### Completed or implemented according to project notes

- **Phase 1 — Project setup:** Frontend/backend structure, Django scaffold,
  virtual environment, environment example, and ignore rules are checked
  complete in `PHASE.md`. The GitHub-repository setup task is not checked.
- **Phase 2 — Frontend:** Landing page, responsive UI, chatbot interface/API
  connection, mission cards, and the “I'm Going Outside” button are checked
  complete in `PHASE.md`. Cross-browser compatibility remains unchecked.
- **Phase 3 — Authentication:** Signup/login, logout, persisted sessions/token
  refresh, and auth error handling are checked complete in `PHASE.md`. Creating
  and configuring the Supabase project is explicitly pending and requires the
  project owner's credentials.
- **Phase 4 — Django backend:** DRF setup, auth/chat/missions endpoints, token
  verification, request validation, error handling, and CORS are checked
  complete in `PHASE.md`.
- The documented API routes are `GET /api/auth/verify/`,
  `GET /api/auth/user/`, `POST /api/chat/`, and `GET /api/missions/`.
- The README documents Supabase bearer-token authentication for protected
  endpoints, no server-side conversation history, and API errors shaped as
  `{ "error": { "code", "message", "details" } }`.
- **Phase 5 — AI chatbot foundation:** The authenticated Django chat endpoint
  is stateless, rejects client-supplied history, and retains the legacy mission
  response fields used by the frontend. Phase 6 subsequently added the local
  model adapter and kept the Phase 5 rule generator as fallback.

### In progress, partial, or not complete

- **Phase 6 — Open-weight AI:** The integration code exists
  (`backend/chatbot/ai.py`, `AI_*` env vars, prompts, and mocked tests); the
  rule-based generator remains the fallback. On 2026-10-08, Django checks and
  all 36 backend tests passed, and a live no-Ollama fallback run was verified.
  Real model inference, response-quality review, and latency benchmarks remain
  UNVERIFIED (Ollama was not installed in that implementation environment).
- **Phase 7 — Outdoor mission generation:** Implemented and targeted tests
  passed on 2026-10-11. The existing `POST /api/chat/` response now carries
  validated category, difficulty, and safety fields without removing its
  legacy fields. Time, mood, activity, setting, energy, and recognized
  constraints guide the AI prompt and rule-based fallback. Mission cards show
  the activity, steps, suggested setting, items, and safety notes, with loading
  and error feedback. Start and optional completion are client-only
  self-check-ins; no mission history, rewards, database writes, or real-world
  verification were introduced.
- **Verification limits:** Real Ollama inference, configured Supabase and
  browser end-to-end behavior, cross-browser behavior, and load testing are not
  verified. The Phase 7 checks are targeted tests, not completion of Phase 8's
  broader testing plan.
- **Phase 8 — Testing:** On 2026-10-12, Django `check` passed,
  `makemigrations --check --dry-run` reported no pending model changes, and
  `test users chatbot missions` passed 61 tests. The four Node client behavior
  tests, JavaScript syntax checks, a local frontend HTTP smoke check (landing
  page plus local assets/modules), and a bounded sample-missions API check
  passed. Supabase verification is mocked; no local
  `.env` or configured Supabase project was available. Ollama executable/API
  are unavailable, so AI tests use mocks and real inference is unverified.
  Chrome and Safari are installed and Safari WebDriver is present, but no
  browser session or automation was run. Responsive breakpoints were inspected
  statically; actual device/browser layouts, authenticated frontend flow,
  production load testing, and cross-browser behavior remain incomplete. The
  20-request, four-worker loopback sample-route smoke is not production load
  testing. Django
  `check --deploy` reports six production configuration warnings (HSTS,
  SSL redirect, local fallback secret, secure session/CSRF cookies, and
  `DEBUG=True`).
- **Phase 8 defect fix:** A newly exercised unexpected exception escaped
  DRF's exception handler and returned Django debug HTML. `config/api_errors.py`
  now logs only method/path and exception class and emits a generic JSON 500
  response; regression tests verify no traceback/internal marker reaches the
  response or logs. Defensive AI failure logs are likewise sanitized. `.gitignore`
  now ignores `.env.*` while preserving `.env.example`; Supabase user-profile
  shape and email are validated before accepting identity.
- **Phase 9 — Documentation:** `README.md`, `Design.md`, `architecture.md`,
  `PHASE.md`, `PRD.md`, and `CONTRIBUTING.md` are present; API, setup,
  troubleshooting, and verification status are documented. `SUBMISSION.md`
  carries the demo and screenshot checklist. Clean setup and live integrations
  remain unverified, and no owner-selected license exists, so the phase is
  still partial.
- **Phase 10 — Hacktoberfest submission:** A project description, limitations,
  test evidence, short demo script, and screenshot checklist are prepared in
  `SUBMISSION.md`. The DEV API and challenge hub verify that Hacktoberfest
  Open-Source AI Challenge: Week 1 uses the matching “Touch Grass” theme and
  closes 2026-10-12 06:59 UTC (12:29 IST); its new-project window, DEV post
  template/tag, and judging criteria are recorded. Owner eligibility and
  in-window project provenance remain unverified because this workspace has no
  commit history. There is no license, actual screenshot/video, external
  submission, public project/community link, deployed demo, or complete browser
  integration evidence. Phase 10 is partial and nothing was externally
  submitted.

## Documentation notes

- `PHASE.md` records the project's progress, not independent runtime proof.
- Prefer inspecting current source code when a feature's status matters.

## Technology and local setup documented by the project

- **Frontend:** HTML5, CSS3, vanilla JavaScript; files are under `frontend/`.
- **Backend:** Django 6.x and Django REST Framework; files are under `backend/`.
- **Authentication:** Supabase email/password auth in the browser; Django
  verifies Supabase bearer tokens for protected routes.
- **Python requirement in README:** Python 3.12 or newer.
- **Install:** `python3 -m venv .venv`, activate it, then
  `python -m pip install -r requirements.txt`.
- **Frontend server:** `python3 -m http.server 8080 --directory frontend`.
- **Django checks:** `.venv/bin/python backend/manage.py check`.
- **Migrations:** `.venv/bin/python backend/manage.py migrate`.
- **API tests documented:** `.venv/bin/python backend/manage.py test users chatbot missions`.
- **Environment:** Copy `.env.example` to `.env`; set a unique
  `DJANGO_SECRET_KEY`, Supabase URL/key, and allowed frontend origin. Configure
  the matching Supabase project URL and publishable/anon key in
  `frontend/js/config.js`.
- Never put a Supabase service-role key in frontend code. Do not expose secrets
  in this file or commit local `.env` values.
- These commands are project documentation, not test results; run them before
  reporting successful setup or behavior.

## Design direction

- Minimal, natural, modern, friendly.
- Warm cream and forest green are primary; sage and lime are supporting accents.
- Emphasize readability, whitespace, rounded cards, and a responsive layout.
- Keep the screen interaction short and encourage the user to go outside.
- See `Design.md` for the design specification.

## Next actions suggested by the documented phase status

1. Before the verified Week 1 deadline (2026-10-12 06:59 UTC / 12:29 IST),
   the owner should confirm eligibility and new-project provenance, then
   prepare and submit a DEV post using the official template and
   `#hf26challenge` if eligible. The workspace cannot establish its provenance.
2. Select/add the repository license.
3. Configure Supabase and test signup/login/token refresh/logout plus protected API flow in a browser.
4. Install/configure Ollama and the model only with approval as appropriate; evaluate real inference, quality, and latency.
5. Capture real desktop/mobile screenshots and a demo recording; manually check responsive, keyboard, and cross-browser behavior.
6. Configure and verify deployment HTTPS, HSTS, secure cookies, allowed hosts/origins, and production secret settings.

## Update log

- **2026-10-08:** Created from the repository's README, phase checklist, design
  document, architecture document, requirements, environment example, and
  visible frontend/backend directory structure. No application tests were run
  while creating this file.
- **2026-10-08 (21:32):** Reviewed the current phase checklist and Git state.
  No newer phase-completion evidence was present; the repository has no commits
  yet and its project files are untracked. No application tests were run, so no
  new runtime verification is recorded.
- **2026-10-08:** Implemented and verified the Phase 5 chatbot foundation.
  `manage.py check` passed and `manage.py test users chatbot` passed all 22
  tests. The service remains rule-based and stateless; no model or conversation
  history storage was added.
- **2026-10-08 (22:42):** Rechecked `PHASE.md`, the chatbot service/tests, and
  the project file list. Phase 5 remains the latest phase with completed tasks;
  Phases 6–10 are still outstanding. The earlier check/test results remain
  historical evidence and were not rerun during this review.
- **2026-10-08 (Phase 6):** Implemented the open-weight AI integration:
  `backend/chatbot/ai.py` (Ollama provider, JSON parsing, mission
  normalization/validation, `AIError`), AI-first flow with automatic
  rule-based fallback in `chatbot/services.py`, `AI_*` settings and
  `.env.example` entries, `build_mission_json_prompt` in `prompts.py`, and
  14 new tests (config, success, malformed, unavailable, fallback, API shape).
  Verified: `manage.py check` passed, `manage.py test users chatbot` passed
  36/36, and a live call with AI enabled but no Ollama server fell back
  cleanly. Not verified: real inference (Ollama absent in this environment).
  Docs updated: `PHASE.md`, `README.md`, `architecture.md`.
- **2026-10-11 (Phase 7):** Extended the existing chat service with validated
  mission categories, difficulty, and application-controlled safety guidance;
  added rule-based missions for nature observation, mindfulness, movement,
  gardening, and social activities; bounded generated duration to the user's
  available time; and added tests for preferences, missing context, malformed AI
  fields, safety constraints, fallback, and API compatibility. Updated mission
  cards and added accessible loading/error states plus client-only start and
  optional self-reported completion. Targeted test results are recorded in
  `PHASE.md`; real Ollama inference and browser/auth end-to-end remain
  unverified.
- **2026-10-12 (Phase 8 QA):** Ran Django checks, migration drift and plan
  checks, the complete user/chatbot suite (57 passed), Node client-state tests
  (2 passed), frontend syntax checks, and a local HTTP smoke check (8 local
  resources passed). Added coverage for malformed chat requests, method errors,
  timeout fallback, Supabase expiry/profile/outage, CORS allow/deny, and
  generic 500 responses. Fixed unhandled DRF exception responses, validated
  Supabase profile email/type, and added `.env.*` ignores. `check --deploy`
  reports six environment-dependent production warnings. No browser, real
  Supabase, or real Ollama inference was tested; Phase 8 remains incomplete
  pending those checks and load/cross-browser testing.
- **2026-10-12 (memory refresh):** Re-reviewed the project file set and
  repository state. The repo is still effectively a local project snapshot with
  all source files untracked, so this file remains a documentation-backed memory
  rather than a commit/history-derived status. The documented facts above are
  retained as the working baseline until new implementation or verification
  evidence changes them.
- **2026-10-12 (Phases 8–10 continuation):** Added tests for the public
  missions route and sanitized error logs, bringing the labeled backend suite to
  the latest observed 61 passing
  tests. Rechecked Django and migration checks, 4 client tests, JavaScript
  syntax, frontend asset delivery over local HTTP, and a bounded 20-request
  loopback check of the public missions endpoint. Real browser, Supabase,
  Ollama, cross-browser, deployment, and production load tests remain blocked
  or not run. Added/reconciled `README.md`, `Design.md`, `architecture.md`,
  `PHASE.md`, `PRD.md`, `CONTRIBUTING.md`, and `SUBMISSION.md`, plus
  `scripts/api_smoke_load.py`. Phase 9 and Phase 10 remain partial pending
  owner-controlled license/configuration/screenshots/submission and clean
  setup/integration verification. No commit or external submission was made.
- **2026-10-12 (final QA and challenge check):** Reran `.venv/bin/python
  backend/manage.py check` (passed), `makemigrations --check --dry-run` (no
  changes), and `test users chatbot missions` (61 passed); reran
  `node --test frontend/tests/mission-state.test.mjs` (4 passed) and syntax
  checks for every frontend JavaScript module. The corrected recursive local
  HTTP smoke fetched the landing page and all 7 referenced local
  assets/modules (8 resources total). The 20-request/four-worker loopback API
  smoke passed (average 6.4 ms, max 22.8 ms, 0.03 s wall time; not production
  load testing). `check --deploy` still reports six environment-dependent
  warnings; the built-in migration plan is applied. Chrome/Safari and Safari
  WebDriver are installed, but no browser session, Supabase integration, or
  real Ollama inference was run. `.env` and `.env.local` are absent and ignored;
  frontend configuration remains placeholder-only and has no JWT-shaped
  credential literal. Verified the related Hacktoberfest Week 1 challenge,
  matching theme, required DEV tag/template, judging criteria, and
  2026-10-12 06:59 UTC deadline. Owner must confirm age/team eligibility and
  that the project satisfies the new in-window-project rule. Updated
  `SUBMISSION.md` and `PHASE.md`; no project was committed or submitted
  externally.
- **2026-10-12 (current snapshot refresh):** Re-read the working project
  documentation and repository state. The source tree is present and locally
  configured, but the project remains a documented local snapshot rather than a
  verified production deployment. This memory file keeps the latest observed
  evidence only: automated local checks and documentation state are recorded,
  while owner-configured Supabase, live browser, real Ollama inference, and
  external submission steps remain explicitly unverified.
