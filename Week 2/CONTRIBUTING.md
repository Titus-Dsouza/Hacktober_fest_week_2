# Contributing to TouchGrass

Thanks for considering a contribution. Keep the MVP focused on helping people
get a clear, low-pressure plan and then leave the screen.

## Development setup

1. Install Python 3.12 or newer and Node.js (only needed for the client-state
   tests). Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and set a local Django secret. Configure a
   Supabase project and `frontend/js/config.js` only if testing real
   authentication. Keep secrets out of commits and issue reports.
3. Ollama and `qwen2.5:3b` are optional; the rule-based generator is the
   fallback. Do not download a model without checking its size and obtaining
   approval where required.
4. Start the API and static site in separate terminals:

   ```bash
   .venv/bin/python backend/manage.py migrate
   .venv/bin/python backend/manage.py runserver
   ```

   ```bash
   npm run dev
   ```

## Checks before opening a pull request

Run from the repository root:

```bash
.venv/bin/python backend/manage.py check
.venv/bin/python backend/manage.py makemigrations --check --dry-run
.venv/bin/python backend/manage.py test users chatbot missions
node --test frontend/tests/mission-state.test.mjs
node --check frontend/js/app.js
node --check frontend/js/config.js
node --check frontend/js/mission-state.mjs
node --check frontend/js/mission-response.mjs
```

The backend suite mocks Supabase and Ollama; it does not demonstrate a live
integration. If your change affects the browser, manually check keyboard use,
the loading/error states, and narrow and wide layouts in a real browser, and
report exactly what you tested.

## Contribution guidelines

- Keep the HTML/CSS/vanilla JavaScript, Django/DRF, Supabase Auth, and Ollama
  architecture intact.
- Preserve the `/api/chat/` contract and its legacy fields unless an explicitly
  approved change requires otherwise.
- Keep model output untrusted: validate it and retain deterministic fallback.
- Avoid storing personal data, chat history, or real-world activity records.
- Add regression tests for behavior changes and update the directly affected
  documentation.
- Do not commit `.env`, credentials, database files, virtual environments, or
  generated model artifacts.
- Describe the behavior changed and list actual test results in the pull
  request. Do not claim browser, Supabase, or model validation that was not run.

There is not yet a repository license file. Until the project owner chooses and
adds a license, do not assume that the source is licensed for reuse.
