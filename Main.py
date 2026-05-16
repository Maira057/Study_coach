import { useState, useEffect, useRef, useCallback } from "react";

// ─── Fonts ───────────────────────────────────────────────────────────────────
const fontLink = document.createElement("link");
fontLink.rel = "stylesheet";
fontLink.href = "https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap";
document.head.appendChild(fontLink);

// ─── Global styles ────────────────────────────────────────────────────────────
const GlobalStyle = () => (
  <style>{`
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body, #root { height: 100%; }
    body {
      background: #0a0b0f;
      color: #e8e6e0;
      font-family: 'DM Sans', sans-serif;
      -webkit-font-smoothing: antialiased;
    }
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #2a2d3a; border-radius: 2px; }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(18px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; } 50% { opacity: 0.4; }
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    @keyframes shimmer {
      0% { background-position: -200% 0; }
      100% { background-position: 200% 0; }
    }
    @keyframes checkPop {
      0% { transform: scale(0.6); opacity: 0; }
      60% { transform: scale(1.2); }
      100% { transform: scale(1); opacity: 1; }
    }

    .fade-up { animation: fadeUp 0.45s ease both; }
    .fade-up-d1 { animation: fadeUp 0.45s 0.07s ease both; }
    .fade-up-d2 { animation: fadeUp 0.45s 0.14s ease both; }
    .fade-up-d3 { animation: fadeUp 0.45s 0.21s ease both; }
    .fade-up-d4 { animation: fadeUp 0.45s 0.28s ease both; }

    .grain {
      position: fixed; inset: 0; pointer-events: none; z-index: 9999;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
      opacity: 0.35;
    }

    .task-check {
      width: 20px; height: 20px; border-radius: 5px;
      border: 1.5px solid #2e3245;
      background: transparent; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      transition: all 0.2s ease; flex-shrink: 0;
    }
    .task-check:hover { border-color: #c8f060; background: rgba(200,240,96,0.08); }
    .task-check.done { background: #c8f060; border-color: #c8f060; }
    .task-check.done svg { animation: checkPop 0.25s ease; }

    .btn-primary {
      background: #c8f060; color: #0a0b0f;
      border: none; border-radius: 10px;
      font-family: 'Syne', sans-serif; font-weight: 700; font-size: 14px;
      padding: 10px 20px; cursor: pointer;
      transition: all 0.2s ease; letter-spacing: 0.02em;
    }
    .btn-primary:hover { background: #d8ff70; transform: translateY(-1px); }
    .btn-primary:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

    .btn-ghost {
      background: transparent; color: #9098b0;
      border: 1.5px solid #2a2d3a; border-radius: 10px;
      font-family: 'DM Sans', sans-serif; font-size: 14px;
      padding: 9px 18px; cursor: pointer;
      transition: all 0.2s ease;
    }
    .btn-ghost:hover { border-color: #454a60; color: #e8e6e0; }

    .input-field {
      background: #13151e; border: 1.5px solid #2a2d3a;
      border-radius: 10px; color: #e8e6e0;
      font-family: 'DM Sans', sans-serif; font-size: 14px;
      padding: 10px 14px; outline: none; width: 100%;
      transition: border-color 0.2s;
    }
    .input-field:focus { border-color: #c8f060; }
    .input-field::placeholder { color: #454a60; }

    .chat-bubble-user {
      background: #c8f060; color: #0a0b0f;
      border-radius: 16px 16px 4px 16px;
      padding: 10px 14px; max-width: 80%; align-self: flex-end;
      font-size: 14px; line-height: 1.5;
    }
    .chat-bubble-ai {
      background: #1c2030; color: #e8e6e0;
      border-radius: 16px 16px 16px 4px;
      padding: 10px 14px; max-width: 85%; align-self: flex-start;
      font-size: 14px; line-height: 1.6;
      border: 1px solid #252c3d;
    }
    .chat-bubble-ai p { margin-bottom: 8px; }
    .chat-bubble-ai p:last-child { margin-bottom: 0; }

    .difficulty-btn {
      padding: 6px 16px; border-radius: 8px; cursor: pointer;
      border: 1.5px solid #2a2d3a; font-size: 13px;
      font-family: 'DM Mono', monospace; transition: all 0.18s;
      background: transparent; color: #9098b0;
    }
    .difficulty-btn:hover { border-color: #454a60; color: #e8e6e0; }
    .difficulty-btn.active-easy { background: rgba(80,220,140,0.15); border-color: #50dc8c; color: #50dc8c; }
    .difficulty-btn.active-medium { background: rgba(255,190,60,0.12); border-color: #ffbe3c; color: #ffbe3c; }
    .difficulty-btn.active-hard { background: rgba(255,80,80,0.12); border-color: #ff5050; color: #ff5050; }

    textarea.input-field { resize: vertical; min-height: 80px; }
  `}</style>
);

// ─── Constants ────────────────────────────────────────────────────────────────
const DIFF_COLORS = { easy: "#50dc8c", medium: "#ffbe3c", hard: "#ff5050" };
const SUBJECT_ACCENTS = ["#c8f060", "#60d0f0", "#f060c8", "#f0a060", "#60f0a0", "#a060f0"];

// ─── Helpers ──────────────────────────────────────────────────────────────────
function daysUntil(dateStr) {
  if (!dateStr) return null;
  const diff = new Date(dateStr) - new Date();
  return Math.ceil(diff / 86400000);
}

function formatDate(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}

async function callClaude(messages, systemPrompt, pdfBase64 = null) {
  const userMsg = messages[messages.length - 1];
  let content = [];

  if (pdfBase64 && typeof userMsg.content === "string") {
    content = [
      { type: "document", source: { type: "base64", media_type: "application/pdf", data: pdfBase64 } },
      { type: "text", text: userMsg.content }
    ];
  } else {
    content = typeof userMsg.content === "string" ? userMsg.content : userMsg.content;
  }

  const builtMessages = [
    ...messages.slice(0, -1),
    { role: userMsg.role, content }
  ];

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1000,
      system: systemPrompt,
      messages: builtMessages,
    }),
  });
  const data = await res.json();
  return data.content?.map(b => b.text || "").join("") || "Sorry, I couldn't get a response.";
}

// ─── Landing Page ─────────────────────────────────────────────────────────────
function LandingPage({ subjects, onAddSubject, onOpenSubject }) {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");

  const create = () => {
    if (!name.trim()) return;
    onAddSubject(name.trim());
    setName("");
    setShowForm(false);
  };

  return (
    <div style={{ minHeight: "100vh", padding: "0 24px 60px" }}>
      {/* Header */}
      <div className="fade-up" style={{ paddingTop: 56, marginBottom: 64, maxWidth: 900, margin: "0 auto" }}>
        <div style={{ paddingTop: 56, display: "flex", alignItems: "flex-end", justifyContent: "space-between", flexWrap: "wrap", gap: 20 }}>
          <div>
            <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#c8f060", letterSpacing: "0.15em", marginBottom: 12, textTransform: "uppercase" }}>
              Study Coach
            </div>
            <h1 style={{ fontFamily: "'Syne', sans-serif", fontSize: "clamp(36px, 5vw, 58px)", fontWeight: 800, lineHeight: 1.05, color: "#e8e6e0" }}>
              Your subjects,<br />
              <span style={{ color: "#c8f060" }}>your plan.</span>
            </h1>
            <p style={{ marginTop: 14, color: "#6b7190", fontSize: 15, maxWidth: 420, lineHeight: 1.6 }}>
              Add a subject, upload your material, and let AI build your daily study checklist — automatically.
            </p>
          </div>
          <button className="btn-primary fade-up-d2" style={{ fontSize: 15, padding: "12px 28px" }} onClick={() => setShowForm(true)}>
            + New subject
          </button>
        </div>
      </div>

      <div style={{ maxWidth: 900, margin: "0 auto" }}>
        {/* Add form */}
        {showForm && (
          <div className="fade-up" style={{ background: "#13151e", border: "1.5px solid #2a2d3a", borderRadius: 16, padding: 24, marginBottom: 32 }}>
            <p style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, marginBottom: 14, fontSize: 16 }}>New subject</p>
            <div style={{ display: "flex", gap: 10 }}>
              <input
                className="input-field"
                placeholder="e.g. Machine Learning, Analysis II, Corporate Law…"
                value={name}
                onChange={e => setName(e.target.value)}
                onKeyDown={e => e.key === "Enter" && create()}
                autoFocus
              />
              <button className="btn-primary" onClick={create}>Create</button>
              <button className="btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </div>
        )}

        {/* Subject grid */}
        {subjects.length === 0 && !showForm && (
          <div className="fade-up-d1" style={{ textAlign: "center", padding: "80px 0", color: "#3a3f55" }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>📚</div>
            <p style={{ fontFamily: "'Syne', sans-serif", fontSize: 18, color: "#454a60" }}>No subjects yet — add your first one above</p>
          </div>
        )}

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 16 }}>
          {subjects.map((s, i) => {
            const days = daysUntil(s.examDate);
            const accent = SUBJECT_ACCENTS[i % SUBJECT_ACCENTS.length];
            const done = s.tasks?.filter(t => t.done).length || 0;
            const total = s.tasks?.length || 0;
            const pct = total > 0 ? Math.round((done / total) * 100) : 0;
            return (
              <div
                key={s.id}
                className={`fade-up-d${Math.min(i + 1, 4)}`}
                onClick={() => onOpenSubject(s.id)}
                style={{
                  background: "#13151e", border: "1.5px solid #1e2130",
                  borderRadius: 16, padding: 24, cursor: "pointer",
                  transition: "all 0.22s ease", position: "relative", overflow: "hidden"
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = accent; e.currentTarget.style.transform = "translateY(-2px)"; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = "#1e2130"; e.currentTarget.style.transform = "translateY(0)"; }}
              >
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: accent, marginBottom: 16 }} />
                <div style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 18, marginBottom: 6 }}>{s.name}</div>
                {s.examDate && (
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#6b7190", marginBottom: 4 }}>
                    Exam: {formatDate(s.examDate)}
                  </div>
                )}
                {days !== null && (
                  <div style={{ fontSize: 12, color: days <= 7 ? "#ff5050" : days <= 21 ? "#ffbe3c" : "#50dc8c", marginBottom: 14 }}>
                    {days > 0 ? `${days} days left` : days === 0 ? "Today!" : "Exam passed"}
                  </div>
                )}
                {s.difficulty && (
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: DIFF_COLORS[s.difficulty], marginBottom: 14, textTransform: "uppercase", letterSpacing: "0.1em" }}>
                    {s.difficulty}
                  </div>
                )}
                {total > 0 && (
                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6, fontSize: 11, color: "#6b7190" }}>
                      <span>Progress</span><span style={{ fontFamily: "'DM Mono', monospace" }}>{done}/{total}</span>
                    </div>
                    <div style={{ height: 3, background: "#1e2130", borderRadius: 2 }}>
                      <div style={{ height: "100%", width: `${pct}%`, background: accent, borderRadius: 2, transition: "width 0.4s ease" }} />
                    </div>
                  </div>
                )}
                {!s.examDate && !total && (
                  <div style={{ fontSize: 12, color: "#3a3f55" }}>Click to set up →</div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ─── Subject Page ─────────────────────────────────────────────────────────────
function SubjectPage({ subject, onBack, onUpdate }) {
  const [tab, setTab] = useState("setup"); // setup | plan | chat
  const [difficulty, setDifficulty] = useState(subject.difficulty || "");
  const [examDate, setExamDate] = useState(subject.examDate || "");
  const [pdfBase64, setPdfBase64] = useState(subject.pdfBase64 || null);
  const [pdfName, setPdfName] = useState(subject.pdfName || "");
  const [hoursPerDay, setHoursPerDay] = useState(subject.hoursPerDay || "2");
  const [priorKnowledge, setPriorKnowledge] = useState(subject.priorKnowledge || "");
  const [tasks, setTasks] = useState(subject.tasks || []);
  const [planLoading, setPlanLoading] = useState(false);
  const [planGenerated, setPlanGenerated] = useState(subject.planGenerated || false);
  const [chatMessages, setChatMessages] = useState(subject.chatMessages || []);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const accent = SUBJECT_ACCENTS[0]; // could be passed per-subject

  // persist changes upward
  useEffect(() => {
    onUpdate({ ...subject, difficulty, examDate, pdfBase64, pdfName, hoursPerDay, priorKnowledge, tasks, planGenerated, chatMessages });
  }, [difficulty, examDate, pdfBase64, pdfName, hoursPerDay, priorKnowledge, tasks, planGenerated, chatMessages]);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [chatMessages]);

  // PDF upload
  const handlePdf = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setPdfName(file.name);
    const reader = new FileReader();
    reader.onload = (ev) => setPdfBase64(ev.target.result.split(",")[1]);
    reader.readAsDataURL(file);
  };

  // Generate study plan
  const generatePlan = async () => {
    if (!examDate) { alert("Please set an exam date first."); return; }
    setPlanLoading(true);
    const days = daysUntil(examDate);
    const prompt = `You are an expert study planner. The student has ${days} days until their ${subject.name} exam.
Difficulty: ${difficulty || "medium"}. Available hours per day: ${hoursPerDay}h. Prior knowledge: ${priorKnowledge || "some basics"}.
${pdfBase64 ? "Course material (PDF) is attached. Use it to create specific tasks referencing actual content (e.g. 'Read slides 12-20 on Gradient Descent', 'Solve exercise 3.2 on page 45')." : "No material uploaded — create generic but structured tasks."}

Return ONLY a JSON array (no markdown, no explanation) like:
[
  {"day": 1, "date": "YYYY-MM-DD", "tasks": [{"id": "t1", "text": "Read lecture 1: Introduction (slides 1-15)", "type": "read", "duration": "30min"}, ...]},
  ...
]
Create ${Math.min(days, 30)} day entries. Each day has 2-4 tasks appropriate for ${hoursPerDay}h study. Include a mix of reading, exercises, and review sessions. Be very specific about what to study.`;

    try {
      const today = new Date();
      const msgContent = pdfBase64
        ? [{ type: "document", source: { type: "base64", media_type: "application/pdf", data: pdfBase64 } }, { type: "text", text: prompt }]
        : prompt;

      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          messages: [{ role: "user", content: msgContent }],
        }),
      });
      const data = await res.json();
      const text = data.content?.map(b => b.text || "").join("") || "[]";
      const clean = text.replace(/```json|```/g, "").trim();
      const planDays = JSON.parse(clean);

      // Flatten into task list
      const flat = [];
      planDays.forEach(d => {
        d.tasks.forEach(t => {
          flat.push({ id: `${d.day}-${t.id}`, day: d.day, date: d.date, text: t.text, type: t.type, duration: t.duration, done: false });
        });
      });
      setTasks(flat);
      setPlanGenerated(true);
      setTab("plan");
    } catch (err) {
      console.error(err);
      alert("Failed to generate plan. Check console.");
    }
    setPlanLoading(false);
  };

  // Toggle task
  const toggleTask = (id) => {
    setTasks(prev => prev.map(t => t.id === id ? { ...t, done: !t.done } : t));
  };

  // Chat
  const sendChat = async () => {
    if (!chatInput.trim() || chatLoading) return;
    const userMsg = { role: "user", content: chatInput.trim() };
    const newHistory = [...chatMessages, userMsg];
    setChatMessages(newHistory);
    setChatInput("");
    setChatLoading(true);

    const systemPrompt = `You are a dedicated study tutor for the subject "${subject.name}".
${pdfBase64 ? "The student has uploaded their course material (PDF). Use it to give specific, relevant answers." : "No material uploaded."}
Help the student understand concepts, work through exercises, answer questions, and quiz them.
Keep responses focused, clear, and educational. Use examples. If the student asks for an exercise, give one and then evaluate their answer.`;

    try {
      const lastMsg = { role: "user", content: pdfBase64 && chatMessages.length === 0
        ? [{ type: "document", source: { type: "base64", media_type: "application/pdf", data: pdfBase64 } }, { type: "text", text: userMsg.content }]
        : userMsg.content
      };
      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          system: systemPrompt,
          messages: [...newHistory.slice(0, -1), lastMsg],
        }),
      });
      const data = await res.json();
      const reply = data.content?.map(b => b.text || "").join("") || "Sorry, no response.";
      setChatMessages(prev => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setChatMessages(prev => [...prev, { role: "assistant", content: "Connection error. Please try again." }]);
    }
    setChatLoading(false);
  };

  const days = daysUntil(examDate);
  const doneTasks = tasks.filter(t => t.done).length;
  const totalTasks = tasks.length;

  // Group tasks by day for plan view
  const tasksByDay = {};
  tasks.forEach(t => {
    if (!tasksByDay[t.day]) tasksByDay[t.day] = { day: t.day, date: t.date, tasks: [] };
    tasksByDay[t.day].tasks.push(t);
  });
  const dayGroups = Object.values(tasksByDay).sort((a, b) => a.day - b.day);

  // Today's tasks
  const todayStr = new Date().toISOString().split("T")[0];
  const todayTasks = tasks.filter(t => t.date === todayStr);

  const TABS = [
    { id: "setup", label: "Setup" },
    { id: "plan", label: "Study Plan" },
    { id: "chat", label: "AI Tutor" },
  ];

  return (
    <div style={{ minHeight: "100vh", padding: "0 24px 80px" }}>
      <div style={{ maxWidth: 860, margin: "0 auto" }}>
        {/* Top bar */}
        <div className="fade-up" style={{ paddingTop: 40, display: "flex", alignItems: "center", gap: 16, marginBottom: 32 }}>
          <button className="btn-ghost" style={{ padding: "7px 14px", fontSize: 13 }} onClick={onBack}>← Back</button>
          <div>
            <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#c8f060", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 4 }}>Subject</div>
            <h2 style={{ fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: 28 }}>{subject.name}</h2>
          </div>
          {days !== null && (
            <div style={{ marginLeft: "auto", textAlign: "right" }}>
              <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 28, fontWeight: 500, color: days <= 7 ? "#ff5050" : days <= 21 ? "#ffbe3c" : "#c8f060" }}>{days > 0 ? days : 0}</div>
              <div style={{ fontSize: 11, color: "#6b7190" }}>days left</div>
            </div>
          )}
        </div>

        {/* Progress bar */}
        {totalTasks > 0 && (
          <div className="fade-up-d1" style={{ marginBottom: 28 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#6b7190", fontFamily: "'DM Mono', monospace", marginBottom: 6 }}>
              <span>Overall progress</span><span>{doneTasks}/{totalTasks} tasks</span>
            </div>
            <div style={{ height: 4, background: "#1e2130", borderRadius: 2 }}>
              <div style={{ height: "100%", width: `${Math.round(doneTasks/totalTasks*100)}%`, background: "#c8f060", borderRadius: 2, transition: "width 0.5s ease" }} />
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="fade-up-d1" style={{ display: "flex", gap: 4, marginBottom: 28, background: "#13151e", borderRadius: 12, padding: 4, width: "fit-content" }}>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} style={{
              padding: "8px 20px", borderRadius: 9, border: "none", cursor: "pointer",
              fontFamily: "'Syne', sans-serif", fontWeight: 600, fontSize: 13,
              background: tab === t.id ? "#c8f060" : "transparent",
              color: tab === t.id ? "#0a0b0f" : "#6b7190",
              transition: "all 0.2s"
            }}>{t.label}</button>
          ))}
        </div>

        {/* ── SETUP TAB ── */}
        {tab === "setup" && (
          <div className="fade-up">
            <div style={{ display: "grid", gap: 20 }}>
              {/* Exam date */}
              <div style={{ background: "#13151e", border: "1.5px solid #1e2130", borderRadius: 16, padding: 24 }}>
                <label style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 14, display: "block", marginBottom: 12 }}>📅 Exam date</label>
                <input type="date" className="input-field" value={examDate} onChange={e => setExamDate(e.target.value)} style={{ maxWidth: 220 }} />
              </div>

              {/* Difficulty */}
              <div style={{ background: "#13151e", border: "1.5px solid #1e2130", borderRadius: 16, padding: 24 }}>
                <label style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 14, display: "block", marginBottom: 12 }}>⚡ Difficulty</label>
                <div style={{ display: "flex", gap: 8 }}>
                  {["easy", "medium", "hard"].map(d => (
                    <button key={d} className={`difficulty-btn ${difficulty === d ? `active-${d}` : ""}`} onClick={() => setDifficulty(d)}>
                      {d.charAt(0).toUpperCase() + d.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Hours per day */}
              <div style={{ background: "#13151e", border: "1.5px solid #1e2130", borderRadius: 16, padding: 24 }}>
                <label style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 14, display: "block", marginBottom: 12 }}>⏱ Hours available per day</label>
                <div style={{ display: "flex", gap: 8 }}>
                  {["1", "1.5", "2", "3", "4", "5"].map(h => (
                    <button key={h} className={`difficulty-btn ${hoursPerDay === h ? "active-medium" : ""}`} onClick={() => setHoursPerDay(h)} style={{ padding: "6px 12px" }}>
                      {h}h
                    </button>
                  ))}
                </div>
              </div>

              {/* Prior knowledge */}
              <div style={{ background: "#13151e", border: "1.5px solid #1e2130", borderRadius: 16, padding: 24 }}>
                <label style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 14, display: "block", marginBottom: 4 }}>🧠 Your prior knowledge</label>
                <p style={{ fontSize: 12, color: "#6b7190", marginBottom: 12 }}>Tell the AI what you already know so it can calibrate the plan.</p>
                <textarea className="input-field" placeholder="e.g. I know basic linear algebra and Python, but haven't done any ML yet. Weak on probability." value={priorKnowledge} onChange={e => setPriorKnowledge(e.target.value)} />
              </div>

              {/* PDF upload */}
              <div style={{ background: "#13151e", border: "1.5px solid #1e2130", borderRadius: 16, padding: 24 }}>
                <label style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 14, display: "block", marginBottom: 4 }}>📄 Upload course material (PDF)</label>
                <p style={{ fontSize: 12, color: "#6b7190", marginBottom: 14 }}>The AI will read your slides/script and reference specific pages & exercises in your study plan.</p>
                <input type="file" accept=".pdf" ref={fileInputRef} style={{ display: "none" }} onChange={handlePdf} />
                {pdfBase64 ? (
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{ background: "rgba(200,240,96,0.1)", border: "1px solid rgba(200,240,96,0.3)", borderRadius: 8, padding: "8px 14px", fontSize: 13, color: "#c8f060", fontFamily: "'DM Mono', monospace" }}>
                      ✓ {pdfName}
                    </div>
                    <button className="btn-ghost" style={{ fontSize: 12, padding: "7px 12px" }} onClick={() => { setPdfBase64(null); setPdfName(""); }}>Remove</button>
                  </div>
                ) : (
                  <button className="btn-ghost" onClick={() => fileInputRef.current?.click()}>
                    + Upload PDF
                  </button>
                )}
              </div>

              {/* Generate */}
              <button
                className="btn-primary"
                style={{ width: "100%", padding: "14px", fontSize: 16 }}
                onClick={generatePlan}
                disabled={planLoading}
              >
                {planLoading ? (
                  <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
                    <span style={{ width: 16, height: 16, border: "2px solid #0a0b0f", borderTopColor: "transparent", borderRadius: "50%", display: "inline-block", animation: "spin 0.7s linear infinite" }} />
                    Generating your study plan…
                  </span>
                ) : planGenerated ? "✓ Regenerate study plan" : "✨ Generate my study plan"}
              </button>
            </div>
          </div>
        )}

        {/* ── PLAN TAB ── */}
        {tab === "plan" && (
          <div className="fade-up">
            {!planGenerated ? (
              <div style={{ textAlign: "center", padding: "60px 0", color: "#3a3f55" }}>
                <div style={{ fontSize: 40, marginBottom: 12 }}>🗓</div>
                <p style={{ fontFamily: "'Syne', sans-serif", fontSize: 16, color: "#454a60", marginBottom: 20 }}>No plan yet — go to Setup to generate one</p>
                <button className="btn-primary" onClick={() => setTab("setup")}>Go to Setup</button>
              </div>
            ) : (
              <div style={{ display: "grid", gap: 14 }}>
                {/* Today highlight */}
                {todayTasks.length > 0 && (
                  <div style={{ background: "rgba(200,240,96,0.06)", border: "1.5px solid rgba(200,240,96,0.25)", borderRadius: 16, padding: 20, marginBottom: 8 }}>
                    <div style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 14, color: "#c8f060", marginBottom: 12 }}>📌 Today</div>
                    {todayTasks.map(t => <TaskRow key={t.id} task={t} onToggle={toggleTask} />)}
                  </div>
                )}

                {dayGroups.map((dg, idx) => {
                  const isToday = dg.date === todayStr;
                  const isPast = dg.date < todayStr;
                  const doneCount = dg.tasks.filter(t => t.done).length;
                  return (
                    <div key={dg.day} style={{ background: "#13151e", border: `1.5px solid ${isToday ? "rgba(200,240,96,0.2)" : "#1e2130"}`, borderRadius: 14, overflow: "hidden" }}>
                      <div style={{ padding: "14px 18px", display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #1a1d28" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                          <span style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 13 }}>Day {dg.day}</span>
                          <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#6b7190" }}>{dg.date}</span>
                          {isToday && <span style={{ fontSize: 10, background: "rgba(200,240,96,0.15)", color: "#c8f060", padding: "2px 8px", borderRadius: 20, fontFamily: "'DM Mono', monospace" }}>TODAY</span>}
                          {isPast && !isToday && <span style={{ fontSize: 10, color: "#3a3f55", fontFamily: "'DM Mono', monospace" }}>past</span>}
                        </div>
                        <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: doneCount === dg.tasks.length ? "#c8f060" : "#6b7190" }}>
                          {doneCount}/{dg.tasks.length}
                        </span>
                      </div>
                      <div style={{ padding: "12px 18px", display: "grid", gap: 8 }}>
                        {dg.tasks.map(t => <TaskRow key={t.id} task={t} onToggle={toggleTask} />)}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ── CHAT TAB ── */}
        {tab === "chat" && (
          <div className="fade-up" style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 280px)", minHeight: 400 }}>
            <div style={{ background: "#13151e", border: "1.5px solid #1e2130", borderRadius: 16, flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
              {/* Messages */}
              <div style={{ flex: 1, overflowY: "auto", padding: 20, display: "flex", flexDirection: "column", gap: 12 }}>
                {chatMessages.length === 0 && (
                  <div style={{ textAlign: "center", margin: "auto", color: "#3a3f55" }}>
                    <div style={{ fontSize: 36, marginBottom: 12 }}>🤖</div>
                    <p style={{ fontFamily: "'Syne', sans-serif", fontWeight: 600, color: "#454a60", marginBottom: 6 }}>Your AI tutor is ready</p>
                    <p style={{ fontSize: 13, color: "#3a3f55", maxWidth: 320, margin: "0 auto" }}>
                      Ask anything about {subject.name}. Request explanations, exercises, quick quizzes, or concept reviews.
                    </p>
                    <div style={{ marginTop: 20, display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center" }}>
                      {["Give me a quick quiz on today's topic", "Explain this concept with an example", "What should I focus on before the exam?", "Give me a practice exercise"].map(s => (
                        <button key={s} className="btn-ghost" style={{ fontSize: 12, padding: "6px 12px" }} onClick={() => setChatInput(s)}>{s}</button>
                      ))}
                    </div>
                  </div>
                )}
                {chatMessages.map((m, i) => (
                  <div key={i} className={m.role === "user" ? "chat-bubble-user" : "chat-bubble-ai"}>
                    {m.content.split("\n").map((line, j) => line ? <p key={j}>{line}</p> : <br key={j} />)}
                  </div>
                ))}
                {chatLoading && (
                  <div className="chat-bubble-ai" style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#c8f060", animation: "pulse 1s 0s infinite" }} />
                    <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#c8f060", animation: "pulse 1s 0.2s infinite" }} />
                    <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#c8f060", animation: "pulse 1s 0.4s infinite" }} />
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Input */}
              <div style={{ padding: 16, borderTop: "1px solid #1a1d28", display: "flex", gap: 10 }}>
                <input
                  className="input-field"
                  placeholder={`Ask about ${subject.name}…`}
                  value={chatInput}
                  onChange={e => setChatInput(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendChat()}
                />
                <button className="btn-primary" onClick={sendChat} disabled={chatLoading || !chatInput.trim()} style={{ flexShrink: 0 }}>
                  Send
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Task Row ─────────────────────────────────────────────────────────────────
function TaskRow({ task, onToggle }) {
  const typeIcon = { read: "📖", exercise: "✏️", review: "🔄", practice: "💪", quiz: "❓" };
  return (
    <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
      <button className={`task-check ${task.done ? "done" : ""}`} onClick={() => onToggle(task.id)}>
        {task.done && (
          <svg width="11" height="9" viewBox="0 0 11 9" fill="none">
            <path d="M1 4L4 7L10 1" stroke="#0a0b0f" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        )}
      </button>
      <div style={{ flex: 1 }}>
        <span style={{ fontSize: 14, color: task.done ? "#454a60" : "#e8e6e0", textDecoration: task.done ? "line-through" : "none", lineHeight: 1.5 }}>
          {typeIcon[task.type] || "▸"} {task.text}
        </span>
        {task.duration && (
          <span style={{ marginLeft: 8, fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#454a60" }}>{task.duration}</span>
        )}
      </div>
    </div>
  );
}

// ─── App Root ─────────────────────────────────────────────────────────────────
export default function App() {
  const [subjects, setSubjects] = useState(() => {
    try { return JSON.parse(localStorage.getItem("studycoach_subjects") || "[]"); } catch { return []; }
  });
  const [activeId, setActiveId] = useState(null);

  useEffect(() => {
    try { localStorage.setItem("studycoach_subjects", JSON.stringify(subjects)); } catch {}
  }, [subjects]);

  const addSubject = (name) => {
    const s = { id: Date.now().toString(), name, examDate: "", difficulty: "", pdfBase64: null, pdfName: "", hoursPerDay: "2", priorKnowledge: "", tasks: [], planGenerated: false, chatMessages: [] };
    setSubjects(prev => [...prev, s]);
    setActiveId(s.id);
  };

  const updateSubject = (updated) => {
    setSubjects(prev => prev.map(s => s.id === updated.id ? updated : s));
  };

  const active = subjects.find(s => s.id === activeId);

  return (
    <>
      <GlobalStyle />
      <div className="grain" />
      {active ? (
        <SubjectPage
          key={active.id}
          subject={active}
          onBack={() => setActiveId(null)}
          onUpdate={updateSubject}
        />
      ) : (
        <LandingPage
          subjects={subjects}
          onAddSubject={addSubject}
          onOpenSubject={setActiveId}
        />
      )}
    </>
  );
}

