# TouchGrass — Demo and Submission Preparation

## Project description

TouchGrass is a lightweight outdoor-mission companion. A user shares how they
feel, how much time they have, and a supported activity or constraint preference;
the application returns one short, actionable outdoor plan. Its core idea is:
**Use AI → Get a plan → Leave the screen.**

## Problem, audience, and differentiator

People may want to go outside but lack an easy starting point or need an idea
that fits their time, energy, or constraints. TouchGrass targets people who want
a practical, low-cost activity without location tracking, a long chat, or a
gamification loop. The differentiator is a deliberately short AI interaction
backed by validation and deterministic rules, with the goal of reducing screen
time rather than extending it.

## Features and stack

- Personalized categories, duration, difficulty, instructions, setting, items,
  and application-controlled safety guidance.
- Local Ollama integration configured for `qwen2.5:3b`, with a rule-based
  fallback. Real inference has not been verified in this environment.
- Static HTML/CSS/vanilla JavaScript frontend; Django and Django REST Framework
  API; Supabase Auth.
- Protected user/chat routes verify the bearer token with Supabase. The chat
  endpoint is stateless and stores no conversation history.
- Start and optional completion are client-side self-check-ins, not verified or
  persisted.

See `README.md`, `Design.md`, `architecture.md`, and `PRD.md` for detailed
architecture and setup.

## Relevant Hacktoberfest challenge

At the supplied timestamp, **Hacktoberfest Open-Source AI Challenge: Week 1**
(event ID **79**) is active and directly matches the “Touch Grass” theme:
build with open-source AI to get people off screens and into the world. It
closes **2026-10-12 06:59 UTC / 12:29 IST**, about **2 hours 46 minutes after
the supplied 09:43 IST timestamp**. See the [event page](https://dev.to/events/79)
and [Hacktoberfest challenge hub](https://dev.to/challenges/hf26).

The event details require a new project started and completed within the
challenge window and one DEV post using the challenge-page submission template
and `#hf26challenge` tag. Writing quality carries the most judging weight,
followed by relevance/theme, creativity, and technical execution. Partner
categories are optional; TouchGrass has not been verified against or entered
into one. The project theme fits, but eligibility and the requirement that the
repository be a new in-window project must be confirmed by the owner: the
current workspace is untracked and has no commit history to establish
provenance. No post has been drafted or submitted externally.

## Verification evidence

Latest repository checks for this preparation run:

- `.venv/bin/python backend/manage.py check` — passed.
- `.venv/bin/python backend/manage.py makemigrations --check --dry-run` —
  passed; no changes detected.
- `.venv/bin/python backend/manage.py test users chatbot missions` — 61 tests
  passed.
- `node --test frontend/tests/mission-state.test.mjs` — 4 tests passed.
- JavaScript syntax checks passed.
- Django `check --deploy` reports six deployment-security warnings.

These are automated and local checks. Supabase, browser end-to-end, real model
inference, responsive viewport, cross-browser, production load, and deployment
behavior have not been verified. A 20-request local smoke check exercised only
the public sample-missions route.

## Short demo script (about 2 minutes)

1. **Problem (15 seconds):** “TouchGrass helps when you want to go outside but
   do not know what fits your day. It tries to make the screen interaction the
   shortest part.”
2. **Request (20 seconds):** Sign in using a configured demo Supabase account.
   Ask: “I have 20 minutes, feel low-energy, and want to watch birds near
   home.”
3. **Personalization (25 seconds):** Point out the mission duration, nature
   observation category, easy difficulty, practical steps, setting, and
   safety note. Explain that only provided preferences are used.
4. **Start (10 seconds):** Select “I'm Going Outside.” Explain that this is a
   browser-only self-check-in, not activity tracking.
5. **Fallback (20 seconds):** In a local demo environment, stop or point
   `AI_BASE_URL` at an unavailable local Ollama endpoint and submit another
   request. Show that a rule-generated mission still returns. Do not claim the
   model generated this response.
6. **Architecture (20 seconds):** Show the frontend → authenticated Django API
   → Ollama adapter → validation → rule fallback flow and note that no
   conversation history is stored.
7. **Open-weight model (10 seconds):** Explain that the default is the local
   `qwen2.5:3b` Ollama model when installed and configured; use the fallback for
   the recorded demo until real inference has been confirmed.

Do not run the authenticated demo until Supabase and frontend configuration are
set up with owner-controlled credentials. Do not expose credentials in the
recording.

## Screenshots and recording still needed

No screenshots or demo recording were captured in this environment. Capture
these manually in a configured browser:

- Desktop landing page and hero.
- Mobile landing page at a narrow viewport.
- Chat request and a mission card with all details visible.
- Loading and recoverable error state.
- Started mission self-check-in.
- Rule-based fallback with Ollama unavailable.
- Optional: model-backed mission only after real inference is observed.

Before capture, use a test account, remove personal information, and ensure no
tokens, browser storage, environment values, or private URLs are visible.

## Final submission checklist

- [x] Repository-controlled project description, problem, audience, features,
  differentiator, stack, architecture, setup links, test evidence, and known
  limitations documented.
- [x] Demo sequence and manual screenshot list prepared.
- [ ] Owner selects and adds a repository license.
- [ ] Owner configures Supabase and verifies signup, login, token refresh,
  logout, and protected requests in a browser.
- [ ] Owner installs/configures Ollama and verifies actual `qwen2.5:3b`
  inference, quality, and latency (or clearly demos rule fallback).
- [ ] Owner captures real screenshots/video and verifies responsive behavior in
  supported browsers.
- [ ] Production settings, HTTPS/TLS, host/origin configuration, and live
  deployment are reviewed and tested.
- [x] Identify the related active Week 1 challenge, prompt, deadline, required
  tag, submission-template requirement, and judging criteria.
- [ ] Owner confirms age/team eligibility and that this is a new project started
  and completed within the challenge window; workspace history cannot prove it.
- [ ] Owner writes/reviews a DEV post using the official challenge template and
  `#hf26challenge`, then submits it before the deadline if eligible.
- [ ] Owner reviews and submits the project. Nothing has been published or
  submitted on the owner's behalf.
