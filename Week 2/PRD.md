# TouchGrass — Product Requirements

## Product summary

TouchGrass turns a short description of a user's mood, available time, activity
preference, setting, energy, or supported constraints into one practical outdoor mission.
The intended interaction is deliberately brief: ask, get a plan, then leave the
screen.

## Problem and users

People who want to spend more time outside may not know what to do, may have
little time or energy, or may need an activity that fits their circumstances.
TouchGrass is for anyone seeking a low-cost, low-pressure idea; it does not
assume fitness level, precise location, special equipment, or a particular
ability.

## MVP requirements

1. Explain the product and let users reach the mission request from the landing
   page.
2. Let users sign up, sign in, and sign out through Supabase Auth when the
   project is configured.
3. Require verified Supabase access tokens for user and chat endpoints.
4. Accept a single chat message (up to 400 characters); do not accept or save
   conversation history.
5. Generate one structured mission through local Ollama when available and
   otherwise use the deterministic rule generator.
6. Validate mission fields, duration, category, difficulty, constraints, and
   application-controlled safety guidance before returning a response.
7. Preserve the existing `POST /api/chat/` response and mission fields used by
   the frontend.
8. Let users start a mission and optionally self-report completion in browser
   state only. Do not represent the button as proof of real-world completion.
9. Provide public sample missions through `GET /api/missions/`.
10. Show a recoverable error if the browser receives an incomplete successful
    mission response rather than rendering partial or misleading content.

Recognized constraints currently include step-free/accessible routes, no
equipment, sheltered fresh-air alternatives for rain or indoor preferences,
nearby activities, and seated/stationary alternatives. This is keyword-based
context extraction, not a general natural-language understanding guarantee.

## Non-functional requirements

- Keep the client as static HTML, CSS, and vanilla JavaScript; keep the API on
  Django REST Framework.
- Keep model inference local to the configured Ollama service. Do not send
  requests to a hosted model provider.
- Fail over to rules when Ollama is unavailable, times out, or returns invalid
  content.
- Never return internal exceptions or tracebacks in API responses.
- Store no mission history or chat transcript in the MVP.
- Keep requests stateless and avoid requiring geolocation or paid services.
- Support narrow and wide layouts in CSS; actual browser/device verification
  remains a release check.

## Out of scope

Persistent profiles or mission tracking, rewards, social feeds, live weather,
location services, maps, fitness integrations, a native app, model downloads
performed by the application, and production deployment are not part of the
current MVP.

## Acceptance and verification

Backend automated tests cover request validation, authentication behavior
through mocked Supabase responses, mission schema and personalization, mocked
Ollama success and fallback, public sample missions, and API error envelopes.
Node tests cover mission start/completion state. See `README.md` and `PHASE.md`
for the latest executed commands and for browser, live Supabase, real Ollama,
load, and cross-browser checks that remain unverified.
