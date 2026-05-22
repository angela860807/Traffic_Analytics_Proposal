import { apiGet, apiPatch } from "@/api/client";

function unwrapData(body) {
  return body && Object.prototype.hasOwnProperty.call(body, "data") ? body.data : body;
}

export async function listSpeedViolations({ start, end }) {
  const body = await apiGet("/api/speed-violations", {
    params: { start, end },
  });
  return unwrapData(body) || [];
}

export async function updateSpeedViolationStatus(violationId, violationStatus, review = {}) {
  const body = await apiPatch(`/api/speed-violations/${violationId}/status`, {
    violationStatus,
    ...review,
  });
  return unwrapData(body);
}
