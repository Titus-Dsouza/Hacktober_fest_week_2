# TouchGrass — Development Phases

## Overview

This document outlines the development phases for TouchGrass, an AI-powered application designed to help users spend less time on screens and more time outside. Each phase builds upon the previous one, progressing from project setup to production-ready submission.

---

## Phase 1 — Project Setup

**Objective:** Establish the foundation for the project with proper configuration and repository structure.

### Tasks
- [ ] Set up GitHub repository
- [x] Create frontend and backend directory structure
- [x] Configure Django project and apps
- [x] Set up Python virtual environment
- [x] Document environment variables and provide `.env.example`
- [x] Add `.gitignore` for Python and Node.js dependencies

### Deliverables
- Repository initialized with proper structure
- Virtual environment ready for development
- All dependencies listed in `requirements.txt`
- Environment variables documented

### Exit Criteria
- Repo is accessible and organized
- Local development environment is ready

---

## Phase 2 — Frontend

**Objective:** Build a responsive, user-friendly interface with core components.

### Tasks
- [x] Build landing page using HTML, CSS, and JavaScript
- [x] Create responsive UI (mobile-first design)
- [x] Implement chatbot interface and connect mission requests to the Django API
- [x] Add outdoor mission cards
- [x] Add "I'm Going Outside" button
- [ ] Ensure cross-browser compatibility

### Deliverables
- Landing page with hero section
- Chatbot UI component
- Mission card components
- Call-to-action button with proper styling
- Mobile-responsive layout

### Exit Criteria
- Frontend renders correctly on mobile and desktop
- All UI components are functional and styled
- No console errors or warnings

---

## Phase 3 — Authentication

**Objective:** Implement secure user authentication using Supabase.

### Tasks
- [ ] Create and configure the Supabase project (requires project owner credentials)
- [x] Add Supabase email/password signup and login flows
- [x] Implement logout flow
- [x] Handle persisted sessions and token refresh through the Supabase JS client
- [x] Add authentication error handling

### Deliverables
- Signup and login dialog with input validation
- Session handling and persistence on frontend
- Supabase user verification for protected API requests

### Exit Criteria
- Users can sign up with email/password
- Users can log in and maintain sessions
- Users can log out
- Protected routes work correctly

---

## Phase 4 — Django Backend

**Objective:** Build a robust REST API backend using Django and Django REST Framework.

### Tasks
- [x] Set up Django REST Framework
- [x] Create REST API endpoints for user verification, chat, and missions
- [x] Connect frontend with Django chat API
- [x] Verify Supabase access tokens on protected endpoints
- [x] Create chatbot API endpoint
- [x] Add request validation and consistent error handling
- [x] Configure CORS settings

### Deliverables
- Django REST API with endpoints for:
  - Supabase-authenticated user verification and profile
  - Chatbot mission generation
  - Public sample mission data
- API documentation
- Error handling and status codes

### Exit Criteria
- Frontend can communicate with backend
- All API endpoints are functional
- Authentication tokens are verified
- API responses follow consistent format

---

## Phase 5 — AI Chatbot

**Objective:** Build a chatbot service that interacts with users and encourages outdoor activities.

### Tasks
- [x] Build chatbot service using Python
- [x] Create system prompts and request-context flow
- [x] Implement rule-based chatbot logic and structured mission generation
- [x] Connect chatbot service with the Django API endpoint
- [x] Add response validation and error handling
- [x] Keep server-side conversation history disabled

### Deliverables
- Python chatbot module with deterministic response generation
- Prompt template ready for later open-weight model integration
- Authenticated API endpoint returning structured missions
- Per-request context extraction without storing conversation history
- Validated input and response fields with consistent API errors

### Exit Criteria
- Chatbot returns a mission for a valid user message
- Missions use available time, mood, activity, setting, energy, and constraints
- Requests are stateless; server-side conversation history is not accepted or stored
- Chatbot responses are validated and retain frontend-compatible mission fields
- Integration with the Django backend works

---

## Phase 6 — Open-Weight AI

**Objective:** Integrate an open-weight AI model for chatbot responses.

### Tasks
- [x] Select an open-weight AI model (e.g., Llama 2, Mistral, OpenChat)
- [x] Set up Ollama or alternative Python-compatible framework
- [x] Configure model parameters and inference settings
- [x] Connect the model to the chatbot service
- [ ] Test response quality and performance
- [ ] Optimize for latency and resource usage
- [x] Document model selection rationale

### Deliverables
- Ollama/framework setup and configuration
- Integration with chatbot service
- Model performance benchmarks
- Response quality evaluation
- Documentation on model capabilities

### Phase 6 evidence (2026-10-08)

- **Model selected:** `qwen2.5:3b` (Apache-2.0, ~3B parameters, ~2 GB download,
  runs on CPU-only laptops) via a local Ollama server. Rationale and setup are
  documented in `README.md` and `architecture.md`.
- **Integration:** `backend/chatbot/ai.py` talks to Ollama's `/api/chat` endpoint
  with JSON output mode, normalizes and validates the result against the existing
  mission serializer, and raises `AIError` on any failure. `services.py` catches
  `AIError` and falls back to the existing rule-based generator. No frontend or
  API-contract changes.
- **Verified:** `manage.py check` passed; `manage.py test users chatbot` passed
  all 36 tests (22 pre-existing + 14 new AI/fallback tests, model mocked); a live
  run with AI enabled and no Ollama server fell back to the rule-based generator
  without error.
- **Not yet verified:** real local model inference — Ollama is not installed in
  the environment where this phase was implemented, so response-quality and
  latency tasks remain unchecked. Setup steps are in `README.md`.

### Exit Criteria
- Model responds to chatbot prompts
- Response quality meets requirements
- Response time is acceptable
- Model runs reliably without errors

---

## Phase 7 — Outdoor Mission Generation

**Objective:** Create a system to generate personalized outdoor missions.

### Tasks
- [x] Define a structured mission response while keeping `/api/chat/` and legacy fields
- [x] Personalize missions from the available time, mood, activity, setting, energy, and recognized constraints
- [x] Display mission title, duration, category, difficulty, instructions, setting, items, and safety guidance
- [x] Track mission start and optional self-reported completion in the browser
- [x] Validate mission categories and difficulty; use conservative difficulty defaults
- [x] Encourage users to leave the website without introducing rewards, accounts history, or a database

### Deliverables
- Existing authenticated `POST /api/chat/` mission response (no new endpoint)
- AI-backed generation with validated rule-based fallback
- Responsive mission card with loading/error states and call-to-action
- Client-only start/completion check-in; no persistence or real-world verification

### Exit Criteria
- [x] Missions are generated dynamically by the model when valid, otherwise by rules
- [x] Users can view the main mission details and a clear place to begin
- [x] "I'm Going Outside" and optional completion check-ins update client-side state
- [x] The experience encourages users to leave the screen

### Phase 7 evidence (2026-10-11)

- **Implemented:** Added validated mission categories, difficulty, and safety
  considerations; expanded rule generation for nature observation, mindfulness,
  gentle movement, gardening, and social activities; and kept duration within
  the user's available time. The model response is validated and constrained
  before it can be returned; invalid, unavailable, or timed-out AI responses
  use the deterministic generator.
- **API compatibility:** `POST /api/chat/`, authentication, `reply`, `mission`,
  and all existing mission fields are preserved. New mission fields are
  additive. No database, new endpoint, location access, or server-side tracking
  was added.
- **Frontend:** Mission cards show the instructions, suggested setting,
  category, difficulty, items, and safety notes. Loading and recoverable error
  states are accessible. Starting and optionally completing a mission are
  client-side self-check-ins; the app does not verify or persist completion.
- **Verified:** `.venv/bin/python backend/manage.py check` passed;
  `.venv/bin/python backend/manage.py test users chatbot` passed all 47 tests
  (including mocked model/network tests); `node --test
  frontend/tests/mission-state.test.mjs` passed both state-transition tests;
  `node --check frontend/js/app.js` and `git diff --check` passed.
- **Not verified:** Real Ollama inference, a configured Supabase/browser
  end-to-end run, and cross-browser behavior. Phase 6's model quality and
  latency work remains incomplete; these limits do not block the mocked-AI and
  deterministic Phase 7 behavior tested above.

---

## Phase 8 — Testing

**Objective:** Ensure all components work together reliably.

### Tasks
- [x] Exercise Supabase token verification, expiry, malformed profile, outage, and CORS via mocked Django API tests
- [x] Test chatbot input validation, response structure, AI success/failure, timeouts, fallback, and generic internal errors
- [x] Test public sample mission response, anonymous access, and unsupported methods
- [x] Check the frontend's local module/asset loading over HTTP and JavaScript syntax
- [ ] Verify authenticated frontend/API flow against a configured Supabase project in a browser
- [x] Test AI success and fallback using mocked Ollama/network responses
- [ ] Test real model response quality, latency, and performance with Ollama
- [ ] Verify mobile, tablet, and desktop rendering in browser/device viewports
- [x] Test targeted error cases and add regression coverage for defects found
- [ ] Perform load testing
- [ ] Verify cross-browser behavior

### Deliverables
- Backend automated tests for API, authentication, mission generation, validation, AI fallback, and errors
- Client-side mission state tests plus JavaScript syntax and local asset HTTP smoke checks
- Regression fix for unhandled API exceptions leaking Django debug HTML
- Ignore rules for local `.env.*` files while keeping `.env.example` trackable
- Public missions endpoint tests and a bounded local smoke/load helper (20 requests, four workers; not production load testing)
- Recorded manual/browser/model/deployment checks that remain outstanding

### Exit Criteria
- [x] Relevant automated backend and client-side tests pass
- [x] Django development system check and migration drift check pass
- [x] AI fallback, protected API errors, and CORS allow/deny behavior are tested
- [ ] Authenticated browser flow, rendered responsive layouts, real Ollama, and load testing are verified
- [ ] No known defects remain across the complete MVP flow

### Phase 8 evidence (2026-10-12)

- **Checks passed:** `.venv/bin/python backend/manage.py check`;
  `.venv/bin/python backend/manage.py makemigrations --check --dry-run`
  (no model migration changes); `.venv/bin/python backend/manage.py test users
  chatbot` (57 tests passed); `node --test
  frontend/tests/mission-state.test.mjs` (2 tests passed); JavaScript syntax
  checks; `git diff --check`; local HTTP smoke of the landing page and 8
  referenced local assets/modules (all returned successfully).
- **Regression fixed:** Unhandled API exceptions previously fell through DRF's
  exception handler and produced Django debug HTML (including traceback
  content) in the test client. The handler now logs only request method/path
  and exception class, then returns a generic JSON `500` envelope; regression
  tests confirm exception text/tracebacks are absent from both response and
  logs. Also added a single auth-button
  listener for the missing/unavailable Supabase setup feedback, and `.env.*`
  ignore coverage with an explicit `.env.example` exception.
- **Auth/CORS:** Tests mock Supabase verification and cover missing, malformed,
  expired, invalid, and unavailable token/service cases. Configured localhost
  CORS preflight is allowed and an unconfigured origin is denied. There is no
  root `.env`; `frontend/js/config.js` and `.env.example` still contain setup
  placeholders. Live Supabase signup/login/token refresh is not verified and
  requires the project owner to configure Supabase URL/anon key, enable
  email/password auth, and set redirect/CORS origins.
- **AI:** `ollama` is not installed and `http://127.0.0.1:11434/api/tags` is
  unavailable. Model success, invalid output, network failure, timeout, and
  deterministic fallback were tested with mocks. No model was installed or
  downloaded; real inference, quality, and latency remain unverified.
- **Frontend/responsive:** Node is available; browser automation packages and
  browser executables were not available. Static frontend HTTP resource smoke
  checks passed and CSS contains 800px and 600px breakpoints, but actual layout,
  interaction, mobile/tablet/desktop rendering, and cross-browser behavior
  still require manual browser testing.
- **Security/deployment:** No frontend service-role key, Django secret, or
  token-like secret was found. `.env`, `.env.*`, virtualenv, and SQLite paths
  are ignored; `.env.example` remains explicitly exempt. Django
  `check --deploy` reports six deployment warnings: HSTS, SSL redirect, weak
  local fallback `SECRET_KEY`, secure session cookie, secure CSRF cookie, and
  `DEBUG=True`. These are production configuration blockers, not fixed by
  blindly enabling TLS-only settings in an unconfigured local project.
- **Migration plan:** `showmigrations --plan` reports Django's built-in
  migrations applied; no project app declares database models or migrations.
- **Status:** Phase 8 is **not complete**. Core automated checks pass, but
  authenticated browser testing, actual responsive viewport testing, real
  Ollama inference/performance, load testing, and production deployment
  settings remain unverified or blocked.

### Phase 8 final rerun (2026-10-12)

- **Passed:** `.venv/bin/python backend/manage.py check` (no issues);
  `.venv/bin/python backend/manage.py makemigrations --check --dry-run` (no
  changes); `.venv/bin/python backend/manage.py test users chatbot missions`
  (61 tests); `node --test frontend/tests/mission-state.test.mjs` (4 tests);
  syntax checks for all frontend JavaScript modules; and a local frontend HTTP
  smoke (landing page plus 7 referenced local assets/modules; 8 resources
  fetched successfully, including the mission response validator).
- **API coverage added:** `backend/missions/tests.py` checks the public
  missions response shape, anonymous access, and the consistent `405` error.
  Existing authentication, chat, CORS, AI fallback, statelessness, malformed
  request, and unexpected-error checks remain in the user/chatbot suites.
- **Log privacy:** unexpected API and defensive model failures no longer log
  raw exception text or stack traces that could include user/model content.
  A regression test injects private-marker values and verifies they do not
  appear in logs; this intentionally trades traceback detail for reduced
  sensitive-data exposure.
- **Bounded smoke/load observation:** `.venv/bin/python scripts/api_smoke_load.py`
  passed 20 loopback `GET /api/missions/` requests using four workers against
  the local Django development server (latest observed average 6.4 ms, maximum
  22.8 ms,
  0.03 s wall time). This only checks a public lightweight route locally; it
  is not a chat, model, production, or capacity/load test.
- **Deployment check:** `check --deploy` reports the same six warnings:
  HSTS, SSL redirect, weak local fallback secret, secure session cookie,
  secure CSRF cookie, and `DEBUG=True`. They require deployment-specific
  configuration.
- **Tooling limitation:** `.venv/bin/python backend/manage.py test` without
  app labels discovered 0 tests; the verified command explicitly labels all
  project test apps (`users chatbot missions`).
- **Still blocked/not run:** Chrome and Safari are installed and Safari
  WebDriver is present, but no browser automation package or actual browser
  session was used. Configured Supabase credentials, Ollama/model inference,
  rendered viewport and cross-browser checks, production load testing, and a
  deployed HTTPS environment remain unverified. Phase 8 remains incomplete.

---

## Phase 9 — Documentation

**Objective:** Create comprehensive documentation for users and contributors.

### Tasks
- [x] Complete `README.md` with project overview, setup, API, testing, troubleshooting, and known limits
- [x] Complete `architecture.md` with current system design, trust boundaries, and API flow
- [x] Complete `Design.md` with implemented UI, design system, responsive source behavior, and accessibility notes
- [x] Add `PRD.md` with product requirements and scope
- [x] Reconcile `PHASE.md` (this file) with observed evidence
- [x] Add local development setup and deployment-only requirements
- [x] Add `CONTRIBUTING.md` with setup, checks, and contribution boundaries
- [x] Document API routes and payload/response shape in `README.md`
- [ ] Run setup from a clean environment and verify a configured end-to-end flow
- [ ] Select/add an open-source license (owner decision)

### Deliverables
- README, design, architecture, phase, and product requirements documentation
- Contributor setup and pull-request/test instructions
- API examples, environment setup, troubleshooting, and honest verification status
- Setup and live integration verification remains pending

### Exit Criteria
- [x] Required repository documents and contributor process are present and source-checked
- [ ] Setup instructions have been proven from a clean environment
- [ ] Supabase/model/browser/deployment-dependent claims verified where applicable
- [ ] License decision made by the owner

**Status:** Documentation deliverables were added or reconciled on 2026-10-12
(`README.md`, `Design.md`, `architecture.md`, `PRD.md`, `CONTRIBUTING.md`, and
`PHASE.md`). `SUBMISSION.md` contains the demo and capture checklist. Phase 9
remains partial until a clean setup is exercised and the owner resolves the
license/configuration-dependent work.

---

## Phase 10 — Hacktoberfest Submission

**Objective:** Prepare the project for Hacktoberfest and public release.

### Tasks
- [ ] Clean and publish the repository (source files are currently untracked in this local snapshot)
- [x] Document installation and run instructions; clean-environment verification remains pending
- [ ] Add actual screenshots and demo recording
- [x] Prepare a concise demo script and manual screenshot checklist
- [x] Explain the configured open-weight model and deterministic fallback
- [ ] Add license and license-dependent badges (owner decision)
- [ ] Test the complete configured browser/auth/model flow end-to-end
- [x] Prepare submission description, audience, features, architecture, evidence, and limitations in `SUBMISSION.md`
- [x] Verify the related Hacktoberfest Week 1 event prompt, deadline, submission
  tag/template requirement, and judging criteria
- [ ] Confirm owner eligibility/new-project provenance and set up public GitHub
  community links
- [ ] Owner reviews and submits externally (not performed)

### Deliverables
- Repository-controlled submission description and demo preparation materials
- Actual visuals, license, public project links, production readiness, and external entry remain pending

### Exit Criteria
- [x] Project description, architecture, setup, test evidence, and demo sequence prepared
- [x] Open-weight model and fallback design explained without claiming real inference
- [ ] License, screenshots/recording, clean setup, real integrations, production configuration, and external submission completed

**Status:** Repository-controlled submission materials are prepared, and the
related Week 1 challenge was verified from its event page and challenge hub.
The challenge closes 2026-10-12 06:59 UTC (12:29 IST); owner eligibility and
new-project provenance cannot be established from this untracked workspace.
Phase 10 remains **partial**, not publication-ready: no post or external
submission was made, and screenshots, license, public repository/community
links, configured integrations, and production evidence remain outstanding.

---

## MVP Goal

The MVP is considered **complete** when:

The project checklist below describes intended MVP scope, not a claim that each
item has been verified in a configured production-like environment. In
particular, Supabase credentials, real model inference, and end-to-end browser
behavior remain environment-dependent and are not certified here.

- [x] Frontend and backend implementation are present
- [x] Supabase authentication integration is present (configured flow unverified)
- [x] Python chatbot and open-weight AI adapter with fallback are implemented
- [x] Outdoor missions are generated dynamically
- [ ] Complete authenticated end-to-end user flow verified

### MVP User Flow
1. User visits the site and signs up/logs in
2. User chats with the AI chatbot about outdoor activities
3. Chatbot encourages outdoor participation
4. User receives a personalized outdoor mission
5. User clicks "I'm Going Outside" and leaves the platform

---

## Future Enhancements

After the MVP, consider these features:

- **User Preferences:** Store and personalize based on location, interests, fitness level
- **Mission History:** Track completed missions and achievements
- **Weather-Aware Activities:** Recommend activities based on current weather
- **Location-Aware Recommendations:** Suggest nearby parks, trails, and outdoor venues
- **Community Challenges:** Social features for group outdoor activities
- **Mobile App:** Native iOS/Android applications
- **Gamification:** Points, badges, leaderboards for outdoor activities
- **Integration:** Connect with fitness trackers and mapping services

---

## Timeline Estimate

- **Phases 1-2:** 1-2 weeks (setup & frontend)
- **Phases 3-4:** 1-2 weeks (auth & backend)
- **Phases 5-6:** 1-2 weeks (chatbot & AI)
- **Phase 7:** 1 week (missions)
- **Phase 8:** 1 week (testing & bug fixes)
- **Phase 9:** 1 week (documentation)
- **Phase 10:** 1 week (submission prep)

**Total Estimate:** 7-10 weeks for MVP completion

---

## Success Metrics

- MVP features are functional and bug-free
- User feedback is positive on UI/UX
- Open-weight AI model performs well (response quality, latency)
- Documentation is clear and helpful
- Community engagement (stars, forks, contributions)

---

## Mission Statement

> **Use AI to help people spend less time on screens and more time outside.**

This project succeeds when it measurably increases the time users spend outdoors while providing an enjoyable, engaging experience.
