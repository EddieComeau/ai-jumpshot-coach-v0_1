import React, { useEffect, useMemo, useState } from "react";
import { health, analyzeVideo, chatCoach, chatStatus } from "./api.js";

function splitCsv(input) {
  return input
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [healthRes, setHealthRes] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [chatReply, setChatReply] = useState("");
  const [chatConn, setChatConn] = useState(null);
  const [chatMessage, setChatMessage] = useState("What should I fix first?");
  const [prefs, setPrefs] = useState({
    shot_style: "",
    do_not_change: "",
    focus_areas: "",
    physical_constraints: "",
    environment_notes: "",
  });
  const [error, setError] = useState("");

  const fileInfo = useMemo(() => {
    if (!selectedFile) return "No file selected";
    return `${selectedFile.name} (${Math.round(selectedFile.size / 1024)} KB)`;
  }, [selectedFile]);

  useEffect(() => {
    onCheckChatStatus();
  }, []);

  function parsedPreferences() {
    return {
      shot_style: prefs.shot_style.trim() || null,
      do_not_change: splitCsv(prefs.do_not_change),
      focus_areas: splitCsv(prefs.focus_areas),
      physical_constraints: splitCsv(prefs.physical_constraints),
      environment_notes: splitCsv(prefs.environment_notes),
    };
  }

  async function onCheckHealth() {
    setError("");
    try {
      setHealthRes(await health());
    } catch (e) {
      setError(String(e.message || e));
    }
  }

  async function onAnalyze() {
    setError("");
    setAnalysis(null);

    if (!selectedFile) {
      setError("Pick a video file first.");
      return;
    }

    try {
      setAnalysis(await analyzeVideo(selectedFile));
    } catch (e) {
      setError(String(e.message || e));
    }
  }

  async function onCheckChatStatus() {
    try {
      const res = await chatStatus();
      setChatConn(res);
    } catch (e) {
      setChatConn({
        ok: false,
        provider: "unknown",
        ollama: { connected: false, model_available: false, error: String(e.message || e) },
      });
    }
  }

  async function onChat() {
    setError("");
    setChatReply("");

    if (!chatMessage.trim()) {
      setError("Type a chat message first.");
      return;
    }

    try {
      const payload = {
        message: chatMessage,
        preferences: parsedPreferences(),
        last_analysis: analysis,
      };
      const res = await chatCoach(payload);
      setChatReply(res.reply || "");
    } catch (e) {
      setError(String(e.message || e));
    }
  }

  return (
    <div className="wrap">
      <header className="header">
        <h1>AI Jumpshot Coach v0.1</h1>
        <p className="sub">Upload video, analyze mechanics, and chat with preference-aware coaching.</p>
      </header>

      <section className="card">
        <h2>Upload</h2>
        <input
          type="file"
          accept="video/mp4,video/quicktime,video/mov,video/*"
          onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
        />
        <div className="muted">{fileInfo}</div>

        <div className="row">
          <button onClick={onCheckHealth}>Check /health</button>
          <button className="primary" onClick={onAnalyze}>Analyze</button>
        </div>

        {error ? <div className="error">{error}</div> : null}
      </section>

      <section className="grid">
        <div className="card">
          <h2>Health</h2>
          <pre>{healthRes ? JSON.stringify(healthRes, null, 2) : "No data yet."}</pre>
        </div>

        <div className="card">
          <h2>Analysis</h2>
          <pre>{analysis ? JSON.stringify(analysis, null, 2) : "Upload a clip and click Analyze."}</pre>
        </div>
      </section>

      <section className="grid">
        <div className="card">
          <h2>Preferences</h2>
          <label className="fieldLabel">Shot style</label>
          <input
            className="field"
            value={prefs.shot_style}
            placeholder="e.g., across-face at peak"
            onChange={(e) => setPrefs((p) => ({ ...p, shot_style: e.target.value }))}
          />

          <label className="fieldLabel">Do not change (comma-separated)</label>
          <input
            className="field"
            value={prefs.do_not_change}
            placeholder="e.g., across-face release"
            onChange={(e) => setPrefs((p) => ({ ...p, do_not_change: e.target.value }))}
          />

          <label className="fieldLabel">Focus areas (comma-separated)</label>
          <input
            className="field"
            value={prefs.focus_areas}
            placeholder="e.g., consistency, arc"
            onChange={(e) => setPrefs((p) => ({ ...p, focus_areas: e.target.value }))}
          />

          <label className="fieldLabel">Physical constraints (comma-separated)</label>
          <input
            className="field"
            value={prefs.physical_constraints}
            placeholder="e.g., low jump height"
            onChange={(e) => setPrefs((p) => ({ ...p, physical_constraints: e.target.value }))}
          />

          <label className="fieldLabel">Environment notes (comma-separated)</label>
          <input
            className="field"
            value={prefs.environment_notes}
            placeholder="e.g., double rim"
            onChange={(e) => setPrefs((p) => ({ ...p, environment_notes: e.target.value }))}
          />
        </div>

        <div className="card">
          <h2>Coach Chat</h2>
          <div className="row rowBetween">
            <span className={`statusPill ${chatConn?.ollama?.connected ? "on" : "off"}`}>
              {chatConn?.provider === "ollama"
                ? chatConn?.ollama?.connected
                  ? "Ollama connected"
                  : "Ollama disconnected"
                : chatConn?.provider === "rules"
                  ? "Rules mode"
                  : "Mesh mode"}
            </span>
            <button onClick={onCheckChatStatus}>Refresh chat status</button>
          </div>
          <div className="muted">
            Provider: {chatConn?.provider || "unknown"} | Model: {chatConn?.ollama?.model || "n/a"}
          </div>
          <label className="fieldLabel">Message</label>
          <textarea
            className="field"
            rows={4}
            value={chatMessage}
            onChange={(e) => setChatMessage(e.target.value)}
          />

          <div className="row">
            <button className="primary" onClick={onChat}>Send to /chat</button>
          </div>

          <pre>{chatReply || "No reply yet."}</pre>
        </div>
      </section>
    </div>
  );
}
