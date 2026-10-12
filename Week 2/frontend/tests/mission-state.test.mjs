import assert from "node:assert/strict";
import test from "node:test";

import { transitionMissionState } from "../js/mission-state.mjs";
import { validateMissionResponse } from "../js/mission-response.mjs";

test("a mission can be started and optionally marked complete", () => {
  assert.equal(transitionMissionState("ready", "start"), "started");
  assert.equal(transitionMissionState("started", "complete"), "completed");
});

test("a mission cannot be completed before it is started or changed twice", () => {
  assert.throws(
    () => transitionMissionState("ready", "complete"),
    /Cannot complete a mission while it is ready/,
  );
  assert.throws(
    () => transitionMissionState("completed", "start"),
    /Cannot start a mission while it is completed/,
  );
});

test("a complete API mission response is accepted", () => {
  const result = {
    reply: "A little outside mission.",
    mission: {
      title: "A quiet pause",
      duration_minutes: 15,
      instructions: ["Choose a place.", "Notice the sounds.", "Head back when ready."],
    },
  };
  assert.equal(validateMissionResponse(result), result);
});

test("an incomplete API mission response becomes an understandable error", () => {
  for (const response of [null, {}, { mission: [] }, { mission: { title: "No steps" } }]) {
    assert.throws(
      () => validateMissionResponse(response),
      /incomplete mission response/,
    );
  }
});
