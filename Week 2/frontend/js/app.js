import { API_BASE_URL, SUPABASE_ANON_KEY, SUPABASE_URL } from "./config.js";
import { transitionMissionState } from "./mission-state.mjs";
import { validateMissionResponse } from "./mission-response.mjs";

const form = document.querySelector("#chat-form");
const input = document.querySelector("#chat-input");
const messages = document.querySelector("#chat-messages");
const suggestions = document.querySelectorAll(".suggestion-chip");
const authDialog = document.querySelector("#auth-dialog");
const authOpen = document.querySelector("#auth-open");
const authClose = document.querySelector("#auth-close");
const authForm = document.querySelector("#auth-form");
const authEmail = document.querySelector("#auth-email");
const authPassword = document.querySelector("#auth-password");
const authFeedback = document.querySelector("#auth-feedback");
const authTitle = document.querySelector("#auth-title");
const authDescription = document.querySelector("#auth-description");
const authSubmit = document.querySelector("#auth-submit");
const authSwitch = document.querySelector("#auth-switch");
const authSwitchCopy = document.querySelector("#auth-switch-copy");
const accountEmail = document.querySelector("#account-email");
const signOutButton = document.querySelector("#sign-out");
const chatStatus = document.querySelector("#chat-status");
const chatFeedback = document.querySelector("#chat-feedback");
const chatPanel = document.querySelector(".chat-panel");
const submitButton = form.querySelector('button[type="submit"]');

let supabase = null;
let activeSession = null;
let authMode = "signin";
let authSetupMessage = "";

function addTextMessage(text, sender) {
  const row = document.createElement("div");
  row.className = `message-row ${sender}-row`;

  if (sender === "assistant") {
    const avatar = document.createElement("span");
    avatar.className = "message-avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = "t";
    row.append(avatar);
  }

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  bubble.append(paragraph);
  row.append(bubble);
  messages.append(row);
  scrollToLatest();
}

function addMission(mission) {
  const row = document.createElement("div");
  row.className = "message-row assistant-row";

  const avatar = document.createElement("span");
  avatar.className = "message-avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.textContent = "t";

  const card = document.createElement("article");
  card.className = "mission-message";

  const kicker = document.createElement("p");
  kicker.className = "mission-kicker";
  kicker.textContent = "Your outdoor mission";
  const title = document.createElement("h3");
  title.textContent = mission.title || "Your outdoor mission";
  const durationLabel = document.createElement("p");
  durationLabel.className = "mission-duration";
  durationLabel.textContent = `ABOUT ${mission.duration_minutes} MINUTES`;
  const metadata = document.createElement("p");
  metadata.className = "mission-meta";
  metadata.textContent = `${mission.category?.replaceAll("_", " ") || "Outdoor mission"} · ${mission.difficulty || "Easy"}`;
  const description = document.createElement("p");
  description.className = "mission-description";
  description.textContent = mission.description || mission.activity || "Spend a little time outdoors at your own pace.";

  const instructions = document.createElement("ol");
  instructions.className = "mission-steps";
  (Array.isArray(mission.instructions) ? mission.instructions : []).forEach((step) => {
    const item = document.createElement("li");
    item.textContent = step;
    instructions.append(item);
  });

  const setting = document.createElement("div");
  setting.className = "mission-detail";
  const settingLabel = document.createElement("strong");
  settingLabel.textContent = "Where: ";
  const settingText = document.createElement("span");
  settingText.textContent = mission.setting === "sheltered_outdoors"
    ? "A comfortable covered outdoor spot."
    : "A nearby park, garden, campus, or familiar outdoor space.";
  setting.append(settingLabel, settingText);

  const challenge = document.createElement("div");
  challenge.className = "mission-detail";
  const challengeLabel = document.createElement("strong");
  challengeLabel.textContent = "Tiny challenge: ";
  const challengeText = document.createElement("span");
  challengeText.textContent = mission.challenge;
  challenge.append(challengeLabel, challengeText);

  const bring = document.createElement("div");
  bring.className = "mission-detail";
  const bringLabel = document.createElement("strong");
  bringLabel.textContent = "Bring: ";
  const bringText = document.createElement("span");
  bringText.textContent = mission.bring;
  bring.append(bringLabel, bringText);

  const safety = document.createElement("div");
  safety.className = "mission-detail";
  const safetyLabel = document.createElement("strong");
  safetyLabel.textContent = "Keep in mind: ";
  const safetyText = document.createElement("span");
  safetyText.textContent = mission.safety_considerations || "Choose a familiar place and stop if conditions feel uncomfortable.";
  safety.append(safetyLabel, safetyText);

  const status = document.createElement("p");
  status.className = "mission-status";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  status.textContent = "Ready when you are.";

  const action = document.createElement("button");
  action.className = "mission-action";
  action.type = "button";
  action.textContent = "I'm Going Outside  →";
  let missionState = "ready";
  action.addEventListener("click", () => {
    if (missionState === "ready") {
      missionState = transitionMissionState(missionState, "start");
      action.textContent = "I'm back — mark complete (optional)";
      status.textContent = "Mission started. Take your time outside; you can mark it complete when you return.";
      return;
    }
    missionState = transitionMissionState(missionState, "complete");
    action.disabled = true;
    action.textContent = "Marked complete";
    status.textContent = "You marked this mission complete. This is only your own check-in; nothing is verified or saved.";
  });

  card.append(
    kicker, title, durationLabel, metadata, description, instructions,
    setting, challenge, bring, safety, action, status,
  );
  row.append(avatar, card);
  messages.append(row);
  scrollToLatest();
}

function setChatFeedback(message = "", isError = false) {
  chatFeedback.textContent = message;
  chatFeedback.classList.toggle("is-error", isError);
  chatFeedback.setAttribute("role", isError ? "alert" : "status");
}

function setMissionLoading(isLoading) {
  input.disabled = isLoading;
  submitButton.disabled = isLoading;
  suggestions.forEach((button) => {
    button.disabled = isLoading;
  });
  chatPanel.setAttribute("aria-busy", String(isLoading));
  if (isLoading) {
    setChatFeedback("Putting together a mission for you…");
  }
}

function scrollToLatest() {
  messages.scrollTop = messages.scrollHeight;
}

function renderSession(session) {
  activeSession = session;
  const email = session?.user?.email;
  authOpen.hidden = Boolean(session);
  accountEmail.hidden = !session;
  signOutButton.hidden = !session;
  accountEmail.textContent = email || "Signed in";
  chatStatus.innerHTML = session
    ? "<i></i> READY FOR A MISSION"
    : "<i></i> SIGN IN REQUIRED";
}

function setAuthFeedback(message, isError = false) {
  authFeedback.textContent = message;
  authFeedback.classList.toggle("is-error", isError);
}

function openAuth(mode = "signin") {
  if (!authDialog.open) authDialog.showModal();
  setAuthMode(mode);
}

function setAuthMode(mode) {
  authMode = mode;
  const signup = mode === "signup";
  authTitle.textContent = signup ? "Find your way out." : "Welcome back.";
  authDescription.textContent = signup
    ? "Create an account to get your first outside mission."
    : "Sign in to get a personal outdoor mission.";
  authSubmit.innerHTML = signup
    ? 'Create account <span aria-hidden="true">↗</span>'
    : 'Sign in <span aria-hidden="true">↗</span>';
  authPassword.autocomplete = signup ? "new-password" : "current-password";
  authSwitchCopy.firstChild.textContent = signup ? "Already have an account? " : "New here? ";
  authSwitch.textContent = signup ? "Sign in" : "Create an account";
  setAuthFeedback("");
}

function apiErrorMessage(data, status) {
  return data?.error?.message || `The request failed (${status}). Please try again.`;
}

async function requestMission(message) {
  const response = await fetch(`${API_BASE_URL.replace(/\/$/, "")}/api/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${activeSession.access_token}`
    },
    body: JSON.stringify({ message })
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401) {
      renderSession(null);
      await supabase.auth.signOut();
      openAuth("signin");
    }
    throw new Error(apiErrorMessage(data, response.status));
  }
  return validateMissionResponse(data);
}

async function sendMessage(text) {
  const message = text.trim();
  if (!message) return;
  if (!activeSession?.access_token) {
    addTextMessage("Sign in first and I'll put together a mission for you.", "assistant");
    openAuth("signin");
    return;
  }

  addTextMessage(message, "user");
  setChatFeedback("");
  setMissionLoading(true);
  try {
    const result = await requestMission(message);
    addMission(result.mission);
  } catch (error) {
    const messageText = error instanceof TypeError
      ? "I couldn't reach the TouchGrass API. Check that the Django server is running and try again."
      : error instanceof Error
        ? error.message
        : "The mission couldn't be generated right now. Please try again.";
    input.value = message;
    setChatFeedback(messageText, true);
  } finally {
    setMissionLoading(false);
    input.focus();
  }
}

function isSupabaseConfigured() {
  return (
    /^https?:\/\/[^/]+\/?$/.test(SUPABASE_URL) &&
    SUPABASE_ANON_KEY.length > 20 &&
    !SUPABASE_ANON_KEY.includes("your-supabase")
  );
}

async function initializeAuth() {
  if (!isSupabaseConfigured()) {
    authSetupMessage = "Add your Supabase project URL and publishable/anon key in frontend/js/config.js.";
    return;
  }

  try {
    const { createClient } = await import("https://esm.sh/@supabase/supabase-js@2");
    supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true
      }
    });
    supabase.auth.onAuthStateChange((_event, session) => {
      renderSession(session);
    });
    const { data, error } = await supabase.auth.getSession();
    if (error) throw error;
    renderSession(data.session);
    await loadUserProfile();
  } catch (error) {
    console.error("Supabase authentication could not be initialized.", error);
    authSetupMessage = "Couldn't load Supabase Auth. Check your connection and project configuration.";
  }
}

async function loadUserProfile() {
  if (!activeSession?.access_token) return;
  try {
    const response = await fetch(`${API_BASE_URL.replace(/\/$/, "")}/api/auth/user/`, {
      headers: { Authorization: `Bearer ${activeSession.access_token}` }
    });
    if (response.status === 401) {
      renderSession(null);
      await supabase.auth.signOut();
      return;
    }
    if (!response.ok) throw new Error(apiErrorMessage(await response.json(), response.status));
    const profile = await response.json();
    accountEmail.textContent = profile.email;
  } catch (error) {
    console.error("Could not load the authenticated profile.", error);
  }
}

authOpen.addEventListener("click", () => {
  openAuth("signin");
  if (authSetupMessage) setAuthFeedback(authSetupMessage, true);
});
authClose.addEventListener("click", () => authDialog.close());
authSwitch.addEventListener("click", () => {
  setAuthMode(authMode === "signin" ? "signup" : "signin");
});

authDialog.addEventListener("click", (event) => {
  if (event.target === authDialog) authDialog.close();
});

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!supabase) {
    setAuthFeedback("Supabase is not configured. Add your project settings in frontend/js/config.js.", true);
    return;
  }
  authSubmit.disabled = true;
  setAuthFeedback("");
  const email = authEmail.value.trim();
  const password = authPassword.value;
  try {
    const result = authMode === "signup"
      ? await supabase.auth.signUp({
          email,
          password,
          options: { emailRedirectTo: window.location.href.split("#")[0] }
        })
      : await supabase.auth.signInWithPassword({ email, password });
    if (result.error) throw result.error;
    if (authMode === "signup" && !result.data.session) {
      setAuthFeedback("Check your email to confirm your account, then come back to sign in.");
      return;
    }
    renderSession(result.data.session);
    authDialog.close();
    await loadUserProfile();
  } catch (error) {
    setAuthFeedback(error.message || "Authentication failed. Please try again.", true);
  } finally {
    authSubmit.disabled = false;
  }
});

signOutButton.addEventListener("click", async () => {
  if (!supabase) return;
  signOutButton.disabled = true;
  try {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    renderSession(null);
    addTextMessage("You're signed out. Hope you get a little fresh air soon.", "assistant");
  } catch (error) {
    console.error("Sign out failed.", error);
    addTextMessage("I couldn't sign you out. Please try again.", "assistant");
  } finally {
    signOutButton.disabled = false;
  }
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = input.value;
  input.value = "";
  void sendMessage(message);
});

suggestions.forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.prompt;
    form.requestSubmit();
  });
});

void initializeAuth();
