# 🌿 TouchGrass — Design Document

## 1. Overview

TouchGrass is a minimal AI-powered outdoor activity website prepared for possible
Hacktoberfest participation. The target event and its current rules have not been
verified; no submission is claimed.

The website combines a clean static interface with an AI chatbot that gives users simple outdoor missions.

### Core idea

> **Use AI → Get a plan → Leave the screen → Go outside.**

The website should make the screen the shortest part of the experience.

### Implemented interface (source-checked 2026-10-12)

The current page is a single static `frontend/index.html` with CSS in
`frontend/css/style.css` and behavior in `frontend/js/app.js`. It contains a
compact navigation, illustrated hero, three-step explainer, static sample
mission cards, Supabase sign-in dialog, chat panel, and open-model summary.
Mission cards are added dynamically from the Django response. The hero artwork
uses the repository's SVG assets; it does not use external stock imagery.
Successful API responses are checked for a usable mission before the card is
rendered; malformed payloads result in a retryable error state.

The implemented palette is defined as CSS variables in `style.css`: cream
`#F5F1E8`, paper `#FFFDF7`, forest `#183A2A`, sage `#7A9B76`, lime `#B7D96C`,
charcoal `#20251F`, and soft border `#D9DED2`. Typography uses DM Sans for body
text and Manrope for headings, with generic sans-serif fallbacks. Fonts are
loaded from Google Fonts when network access is available.

These notes describe source code, not a verified browser rendering. Actual
viewport, keyboard, screen-reader, and cross-browser checks remain outstanding.

---

## 2. Design Goals

- Keep the interface simple and easy to understand.
- Make the AI chatbot the main feature.
- Create a calm, natural visual identity.
- Encourage users to leave the website after getting their mission.
- Work well on both desktop and mobile.
- Avoid unnecessary dashboards, accounts, menus, and complex features.
- Make the open-source/open-weight AI aspect clear without making the UI overly technical.

---

## 3. Visual Direction

### Style

**Minimal • Natural • Modern • Friendly**

The design should feel like a modern outdoor/wellness product rather than a typical futuristic AI website.

Avoid:

- Excessive gradients
- Neon/glowing AI effects
- Overly complicated animations
- Crowded dashboards
- Too many colors
- Unnecessary UI elements

Use:

- Large typography
- Generous whitespace
- Rounded cards
- Subtle borders
- Soft shadows
- Natural imagery
- Simple icons

---

## 4. Color Palette

The primary palette is inspired by nature.

| Purpose | Color | Hex |
|---|---|---|
| Background | Warm Cream | `#F5F1E8` |
| Primary | Forest Green | `#183A2A` |
| Secondary | Sage Green | `#7A9B76` |
| Accent | Fresh Lime | `#B7D96C` |
| Text | Dark Charcoal | `#20251F` |
| Cards | Off White | `#FFFDF7` |
| Border | Soft Gray Green | `#D9DED2` |

The interface should remain mostly cream and forest green, with lime used sparingly for important actions.

---

## 5. Typography

Use a modern sans-serif font.

Preferred fonts:

- Inter
- Manrope
- DM Sans

### Hierarchy

```text
Hero Heading
Large / Bold

Section Heading
Medium / Semibold

Body
Regular

Buttons
Medium / Semibold

Chat Messages
Regular
```

The typography should be readable and spacious.

---

# 6. Website Structure

```text
TouchGrass
│
├── Navigation
├── Hero
├── How It Works
├── Outdoor Missions
├── AI Chatbot
├── Why Open AI
└── Footer
```

The website should remain a single-page experience.

---

# 7. Navigation

Keep the navigation minimal.

### Left

```text
🌿 TouchGrass
```

### Right

```text
How it works
Ask AI
GitHub
```

The navigation should remain clean and uncluttered.

At narrow widths the current page hides some navigation links; it does not yet
provide a hamburger or expandable mobile menu.

---

# 8. Hero Section

The hero should immediately explain the purpose of the website.

### Main heading

```text
GO OUTSIDE.
WE'LL HANDLE
THE PLAN.
```

### Supporting text

```text
A little AI. A little adventure.
A lot less screen time.
```

### Primary CTA

```text
Ask TouchGrass AI →
```

### Secondary CTA

```text
How it works
```

### Visual

Use a large nature image or simple outdoor illustration.

Possible visuals:

- Forest trail
- Person walking outdoors
- Park
- Hiking trail
- Trees and sunlight

The image should feel natural and authentic.

---

# 9. How It Works

Use three simple steps.

### 01 — Tell us

Tell the AI:

- How much time you have
- How you feel
- What kind of activity you want
- Your general location if useful

### 02 — Get a mission

The AI creates a short, practical outdoor mission.

### 03 — Touch Grass

Close the website and actually do it.

Visual:

```text
Tell us → Get a mission → Go outside
```

---

# 10. Outdoor Mission Cards

Show a few example missions before the user opens the chatbot.

### 🌿 Nature Walk

> Slow down and explore your surroundings.

### 🐦 Bird Hunt

> Listen for three different bird calls.

### 📸 Photo Walk

> Find five interesting things around you.

### 🏃 Quick Run

> Get outside for a short run or jog.

Each card should have:

- Simple icon
- Activity name
- One-line description
- Optional duration

Cards should use rounded corners and subtle borders.

---

# 11. AI Chatbot

The chatbot is the **main feature** of TouchGrass.

It should feel like a friendly outdoor companion rather than a generic AI chatbot.

### Chatbot heading

```text
What are you feeling like?
```

### Supporting text

```text
Tell me what you want to do outside.
I'll give you a mission.
```

### Input placeholder

```text
"I have 1 hour and want something relaxing..."
```

### Suggested prompts

```text
🌿 Something relaxing

🏃 Something active

📸 Something fun to explore

🌳 I only have 30 minutes
```

---

# 12. Chatbot Response

AI responses should be short and actionable.

Example:

```text
🌿 Your Outdoor Mission

Take a 40-minute walk somewhere with
trees or open space.

🎯 Mission
Find 3 things you've never noticed before.

📵 Challenge
Keep your phone away for the first 20 minutes.

🎒 Bring
Water + comfortable shoes

[ I'm going outside → ]
```

The AI should avoid long explanations.

The intended flow is:

```text
Read → Understand → Leave the screen
```

---

# 13. "I'm Going Outside" State

After the user receives a mission, provide a final action.

```text
I'm going outside →
```

After clicking it:

```text
🌿 Good choice.

We'll see you when you're back.

Go touch some grass.
```

The website should not encourage the user to continue browsing.

---

# 14. Why Open AI Section

The website should briefly explain why open-source/open-weight AI is important.

### Heading

```text
Why open AI?
```

### Message

```text
TouchGrass uses open AI because we want
more control over how the assistant works.

Open models let us experiment, swap models,
run AI locally, and build without depending
entirely on a closed AI provider.
```

Keep this section short and understandable.

---

# 15. GitHub Section

Include a small call-to-action:

```text
Built in the open.

View the project on GitHub →
```

The repository should contain:

- Source code
- README.md
- Design.md
- Setup instructions
- AI/model information
- License

---

# 16. Responsive Design

## Desktop

- Large hero typography
- Two-column hero layout
- Spacious cards
- Centered chatbot
- Generous whitespace

## Tablet

- Reduced spacing
- Smaller hero heading
- Flexible card layout

## Mobile

- Single-column layout
- Full-width buttons
- Compact navigation
- Touch-friendly chatbot
- Readable text
- Chat input fixed or easily accessible

The chatbot should be comfortable to use from a phone.

### Implemented responsive behavior

The current stylesheet uses breakpoints at `800px` and `600px`. Above 800px,
the hero and chat section use two-column layouts and sample missions use a
three-column grid. At 800px and below, spacing and type sizes reduce while the
hero and chat remain two-column. At 600px and below, the hero, explainer cards,
sample missions, and chat become single-column. Some navigation links are
hidden on small screens rather than moved into a menu. These are CSS
observations only; actual overflow and readability at device viewports have not
been tested in a browser.

### Implemented accessibility decisions

- Semantic header, navigation, main, section, form, and footer landmarks.
- Explicit labels for the chat message and authentication fields, plus a named
  send button and dialog close button.
- Native dialog behavior and keyboard-focusable links and buttons.
- A live chat log, status/error announcements, and `aria-busy` during mission
  generation.
- Dynamic mission content is inserted with `textContent`, not interpreted as
  HTML.
- Visible keyboard focus styles and a reduced-motion media query.

These source-level affordances are not a substitute for keyboard, screen-reader,
contrast, or browser accessibility testing.

---

# 17. UI Components

Required components:

```text
Navbar
Hero
CTA Button
Activity Card
How-It-Works Card
Chat Window
Chat Input
Chat Message
AI Response Card
Mission Card
Footer
```

All components should share the same:

- Border radius
- Typography
- Spacing system
- Color palette
- Button style

---

# 18. Interaction Principles

### Keep it simple

Only add features that improve the main experience.

### Outdoor first

Every major interaction should lead toward an outdoor activity.

### AI should be useful

The chatbot should produce practical activities rather than generic conversation.

### Keep responses short

The user should understand the mission within a few seconds.

### Keep accounts lightweight

Supabase email/password authentication is used to protect chat and user API requests.
Browsing example missions remains public. The MVP still avoids dashboards, social feeds,
and unnecessary profile data.

---

# 19. Technical Design

## Frontend

```text
HTML5
CSS3
JavaScript
```

The initial interface should be a static website.

## AI

Use an **open-weight/open-source AI model**.

Possible local inference option:

```text
Ollama
```

The final model should be selected based on local performance and compatibility.

## Backend

A lightweight API/backend may be used to connect the static frontend to the local AI model.

The backend should remain minimal.

---

# 20. Architecture

```text
                 ┌──────────────────┐
                 │   TouchGrass UI  │
                 │   HTML/CSS/JS    │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Chat Interface │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   AI API Layer   │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Open-Weight AI   │
                 │   Local Model    │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Outdoor Mission  │
                 └──────────────────┘
```

---

# 21. Design Philosophy

Most AI products are designed to keep users engaged with the screen.

TouchGrass is intentionally different.

> **The best AI interaction might be the one that gets you to stop using AI.**

The ideal experience is:

```text
Open website
      ↓
Ask AI
      ↓
Get a mission
      ↓
Close website
      ↓
🌿 Go outside
```

---

# 22. MVP Scope

The first version should include:

- [ ] Landing page
- [ ] Responsive navigation
- [ ] Hero section
- [ ] Outdoor activity cards
- [ ] Chatbot UI
- [ ] Open-weight AI integration
- [ ] Outdoor mission generation
- [ ] "I'm Going Outside" interaction
- [ ] Why Open AI section
- [ ] GitHub link
- [ ] Mobile responsiveness

Avoid adding extra features until the core experience works.

---

# 23. Success Criteria

TouchGrass is successful if a user can:

1. Open the website.
2. Understand what it does within 5 seconds.
3. Ask the AI for an outdoor activity.
4. Receive a short and useful mission.
5. Know exactly what to do next.
6. Close the website and go outside.

**The goal is not to build the biggest AI app.**

**The goal is to build an AI app that makes people need the screen less.**

🌿 **TouchGrass**
