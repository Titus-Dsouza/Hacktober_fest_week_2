export function validateMissionResponse(data) {
  const mission = data?.mission;
  if (
    !data ||
    typeof data !== "object" ||
    Array.isArray(data) ||
    !mission ||
    typeof mission !== "object" ||
    Array.isArray(mission) ||
    typeof mission.title !== "string" ||
    typeof mission.duration_minutes !== "number" ||
    !Array.isArray(mission.instructions)
  ) {
    throw new Error("TouchGrass received an incomplete mission response. Please try again.");
  }
  return data;
}
