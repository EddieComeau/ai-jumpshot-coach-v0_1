const BASE = "http://127.0.0.1:8000";

export async function health() {
  const r = await fetch(`${BASE}/health`);
  if (!r.ok) throw new Error(`Health failed: ${r.status}`);
  return r.json();
}

export async function analyzeVideo(file) {
  const form = new FormData();
  form.append("video", file);

  const r = await fetch(`${BASE}/analyze`, {
    method: "POST",
    body: form,
  });

  if (!r.ok) throw new Error(`Analyze failed: ${r.status}`);
  return r.json();
}

export async function chatCoach(payload) {
  const r = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!r.ok) throw new Error(`Chat failed: ${r.status}`);
  return r.json();
}

export async function chatStatus() {
  const r = await fetch(`${BASE}/chat/status`);
  if (!r.ok) throw new Error(`Chat status failed: ${r.status}`);
  return r.json();
}
