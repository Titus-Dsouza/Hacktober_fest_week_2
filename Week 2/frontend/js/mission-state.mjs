const TRANSITIONS = {
  ready: { start: "started" },
  started: { complete: "completed" },
  completed: {},
};

export function transitionMissionState(state, action) {
  const nextState = TRANSITIONS[state]?.[action];
  if (!nextState) {
    throw new RangeError(`Cannot ${action} a mission while it is ${state}.`);
  }
  return nextState;
}
