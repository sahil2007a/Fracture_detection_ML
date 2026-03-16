/**
 * API service — talks to FastAPI backend
 */

const API_BASE = "http://localhost:8000/api";

/**
 * POST /api/analyze-image
 */
export async function analyzeImage(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/analyze-image`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error ${res.status}`);
  }

  return res.json();
}

/**
 * POST /api/analyze-report
 */
export async function analyzeReport(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/analyze-report`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error ${res.status}`);
  }

  return res.json();
}

/**
 * GET /api/health
 */
export async function healthCheck() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}