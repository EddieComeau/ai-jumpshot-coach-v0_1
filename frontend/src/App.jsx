import React, { useEffect, useMemo, useState } from "react";
import { health, analyzeVideo, chatCoach, chatStatus } from "./api.js";

function splitCsv(input) {
  return input
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

const METRIC_COPY = {
  knee_bend_depth: {
    label: "Knee Bend Depth",
    getStatus(metric) {
      if (metric.value < 45) return "needs work";
      if (metric.value < 55) return "warning";
      return "good";
    },
    getCoachingText(metric) {
      if (metric.value < 45) return "Your dip is reading shallow. Think smooth hip load before rising into the shot.";
      if (metric.value < 55) return "Your load is close. Keep the dip controlled and repeatable.";
      return "Your lower-body load is in a stronger range for this early-stage read.";
    },
  },
  drift: {
    label: "Forward Drift",
    getStatus(metric) {
      if (metric.value > 0.18) return "needs work";
      if (metric.value > 0.12) return "warning";
      return "good";
    },
    getCoachingText(metric) {
      if (metric.value > 0.18) return "You are drifting forward. Focus on going up through the shot instead of out.";
      if (metric.value > 0.12) return "Your drift is worth watching. Keep your finish tall and balanced.";
      return "Your forward movement looks controlled in this early-stage read.";
    },
  },
};

function formatMetricPercent(metric) {
  const value = metric.name === "drift" ? metric.value * 100 : metric.value;
  return `${Math.round(value)}%`;
}

function getMetricUi(metric) {
  const config = METRIC_COPY[metric.name] || {
    label: metric.name,
    getStatus: () => "warning",
    getCoachingText: () => "Review this metric as an early-stage signal, not a final diagnosis.",
  };

  return {
    label: config.label,
    value: formatMetricPercent(metric),
    status: config.getStatus(metric),
    coachingText: config.getCoachingText(metric),
  };
}

function hasPreferenceInput(prefs) {
  return Boolean(
    prefs.shot_style.trim() ||
      splitCsv(prefs.do_not_change).length ||
      splitCsv(prefs.focus_areas).length ||
      splitCsv(prefs.physical_constraints).length ||
      splitCsv(prefs.environment_notes).length
  );
}

function splitChatReply(reply) {
  return reply
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function getChatSectionKey(line, hasPriority) {
  const lower = line.toLowerCase();

  if (
    lower.includes("fix first") ||
    lower.startsWith("fix ") ||
    lower.includes("recommend") ||
    lower.includes("suggest") ||
    lower.includes("addressing") ||
    lower.includes("starting with") ||
    lower.includes("start with") ||
    lower.includes("start by") ||
    lower.includes("let's start")
  ) {
    return "priority";
  }

  if (
    lower.includes("constraint") ||
    lower.includes("preference") ||
    lower.includes("preferred") ||
    lower.includes("won't force") ||
    lower.includes("locked mechanics") ||
    lower.includes("shot style noted") ||
    lower.includes("priority focus") ||
    lower.includes("environment context")
  ) {
    return "constraints";
  }

  if (
    lower.includes("analysis") ||
    lower.includes("metric") ||
    lower.includes("confidence") ||
    lower.includes("because") ||
    lower.includes("evidence") ||
    lower.includes("knee") ||
    lower.includes("drift")
  ) {
    return "reasoning";
  }

  if (!hasPriority || lower.includes("what should i fix")) {
    return "priority";
  }

  return "supporting";
}

function parseChatSections(reply) {
  const lines = splitChatReply(reply);
  const sections = {
    priority: [],
    supporting: [],
    reasoning: [],
    constraints: [],
  };

  lines.forEach((line) => {
    const key = getChatSectionKey(line, sections.priority.length > 0);
    sections[key].push(line);
  });

  return [
    ["priority", "Priority Fix"],
    ["supporting", "Supporting Adjustments"],
    ["reasoning", "Reasoning"],
    ["constraints", "Constraints Awareness"],
  ]
    .map(([key, label]) => ({ key, label, lines: sections[key] }))
    .filter((section) => section.lines.length);
}

function getChatStatusLabel(chatConn) {
  if (chatConn?.provider === "rules") return "Rules mode";
  if (chatConn?.provider === "ollama") {
    return chatConn?.ollama?.connected ? "Ollama connected" : "Ollama disconnected";
  }
  if (chatConn?.provider === "mesh") {
    return chatConn?.ollama?.connected ? "Mesh + Ollama" : "Mesh fallback";
  }
  return "Checking chat";
}

function getChatStatusClass(chatConn) {
  if (chatConn?.provider === "rules") return "neutral";
  return chatConn?.ollama?.connected ? "on" : "off";
}

function ChatResponsePanel({ reply, hasAnalysis, hasPreferences, isLoading }) {
  const sections = parseChatSections(reply);

  return (
    <div className="chatResponsePanel">
      <div className="chatResponseHeader">
        <h3>Coach Response</h3>
        {isLoading ? <span className="loadingText">Thinking with current context...</span> : null}
      </div>

      <div className="chatContextRow">
        {hasAnalysis ? <span className="contextChip">Based on latest shot analysis</span> : null}
        {hasPreferences ? <span className="contextChip">Adjusted for your preferences</span> : null}
        {!hasAnalysis && !hasPreferences ? <span className="contextChip mutedChip">General coaching context</span> : null}
      </div>

      {isLoading ? (
        <p className="muted">Waiting for coach response...</p>
      ) : sections.length ? (
        <div className="chatSections">
          {sections.map((section) => (
            <section className="chatSection" key={section.key}>
              <h3>{section.label}</h3>
              {section.lines.map((line, index) => (
                <p key={`${section.key}-${index}`}>{line}</p>
              ))}
            </section>
          ))}
        </div>
      ) : (
        <p className="muted">No reply yet.</p>
      )}

      <div className="chatDisclaimer">
        Coaching is based on the current limited analysis and any preferences you provide. It is not a full biomechanics review yet.
      </div>
    </div>
  );
}

function ShotAnalysisResults({ analysis }) {
  const trackedMetrics = ["knee_bend_depth", "drift"]
    .map((name) => analysis?.metrics?.find((metric) => metric.name === name))
    .filter(Boolean);

  if (!analysis) {
    return (
      <div className="emptyState">
        <h2>Shot Analysis</h2>
        <p>Upload a clip and click Analyze to see your early-stage shot readout.</p>
      </div>
    );
  }

  return (
    <div className="analysisResults">
      <div className="sectionTitleRow">
        <div>
          <h2>Shot Analysis</h2>
          <p className="muted compact">Results for {analysis.video_filename || "uploaded clip"}</p>
        </div>
        <span className="statusPill off">Placeholder analysis</span>
      </div>

      <div className="disclaimer">
        Early-stage placeholder analysis: these metrics are fixed MVP signals, not validated pose tracking or real biomechanics yet.
      </div>

      <div className="metricGrid">
        {trackedMetrics.map((metric) => {
          const ui = getMetricUi(metric);
          return (
            <article className="metricCard" key={metric.name}>
              <div className="metricCardHeader">
                <h3>{ui.label}</h3>
                <span className={`metricStatus ${ui.status.replaceAll(" ", "-")}`}>{ui.status}</span>
              </div>
              <div className="metricValue">{ui.value}</div>
              <p>{ui.coachingText}</p>
              <div className="metricMeta">
                Confidence: {Math.round((metric.confidence || 0) * 100)}% | Source: placeholder
              </div>
            </article>
          );
        })}
      </div>

      <div className="topFixes">
        <h3>Top Fixes</h3>
        {analysis.fixes?.length ? (
          <ol className="fixList">
            {analysis.fixes.map((fix, index) => (
              <li key={`${fix.issue}-${index}`}>
                <strong>{fix.issue}</strong>
                <span>{fix.cue}</span>
                <small>{fix.drill}</small>
              </li>
            ))}
          </ol>
        ) : (
          <p className="muted">No fixes returned for this clip.</p>
        )}
      </div>

      {analysis.notes?.length ? (
        <div className="analysisNotes">
          <h3>Coach Notes</h3>
          <ul>
            {analysis.notes.map((note, index) => (
              <li key={`${note}-${index}`}>{note}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [healthRes, setHealthRes] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [chatReply, setChatReply] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
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
      setChatLoading(true);
      const payload = {
        message: chatMessage,
        preferences: parsedPreferences(),
        last_analysis: analysis,
      };
      const res = await chatCoach(payload);
      setChatReply(res.reply || "");
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setChatLoading(false);
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
          <ShotAnalysisResults analysis={analysis} />
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
            <span className={`statusPill ${getChatStatusClass(chatConn)}`}>
              {getChatStatusLabel(chatConn)}
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
            <button className="primary" onClick={onChat} disabled={chatLoading}>
              {chatLoading ? "Sending..." : "Send to /chat"}
            </button>
          </div>

          <ChatResponsePanel
            reply={chatReply}
            hasAnalysis={Boolean(analysis)}
            hasPreferences={hasPreferenceInput(prefs)}
            isLoading={chatLoading}
          />
        </div>
      </section>
    </div>
  );
}
