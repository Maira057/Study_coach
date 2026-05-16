import streamlit as st
import anthropic
import json
import base64
from datetime import date, datetime, timedelta

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Study Coach",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0b0f;
    color: #e8e6e0;
}
.stApp { background-color: #0a0b0f; }

h1, h2, h3 { font-family: 'Syne', sans-serif !important; color: #e8e6e0 !important; }

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 860px; }

/* Cards */
.subject-card {
    background: #13151e;
    border: 1.5px solid #1e2130;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
    cursor: pointer;
    transition: all 0.2s;
}
.subject-card:hover { border-color: #c8f060; }

.info-card {
    background: #13151e;
    border: 1.5px solid #1e2130;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
}

.accent-label {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #c8f060;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.days-badge {
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    padding: 4px 10px;
    border-radius: 20px;
    display: inline-block;
}

.task-done { text-decoration: line-through; color: #454a60; }
.task-normal { color: #e8e6e0; }

/* Chat bubbles */
.user-bubble {
    background: #c8f060;
    color: #0a0b0f;
    border-radius: 16px 16px 4px 16px;
    padding: 10px 14px;
    margin: 6px 0;
    max-width: 80%;
    margin-left: auto;
    font-size: 14px;
    line-height: 1.5;
}
.ai-bubble {
    background: #1c2030;
    color: #e8e6e0;
    border-radius: 16px 16px 16px 4px;
    padding: 10px 14px;
    margin: 6px 0;
    max-width: 85%;
    font-size: 14px;
    line-height: 1.6;
    border: 1px solid #252c3d;
}

/* Buttons */
.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    transition: all 0.2s !important;
}

/* Progress */
.stProgress > div > div { background-color: #c8f060 !important; }

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stDateInput > div > div > input {
    background: #13151e !important;
    border: 1.5px solid #2a2d3a !important;
    color: #e8e6e0 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #c8f060 !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: #13151e !important;
    border: 1.5px solid #2a2d3a !important;
    color: #e8e6e0 !important;
    border-radius: 10px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #13151e;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 9px;
    color: #6b7190;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: #c8f060 !important;
    color: #0a0b0f !important;
}
.stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 20px; }

/* File uploader */
.stFileUploader > div {
    background: #13151e !important;
    border: 1.5px dashed #2a2d3a !important;
    border-radius: 12px !important;
}

/* Checkbox */
.stCheckbox > label { color: #e8e6e0 !important; }

/* Sidebar */
.css-1d391kg { background: #0d0f14; }

div[data-testid="stSidebar"] {
    background-color: #0d0f14;
    border-right: 1px solid #1e2130;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────────
if "subjects" not in st.session_state:
    st.session_state.subjects = {}
if "current_subject" not in st.session_state:
    st.session_state.current_subject = None
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

# ── Helpers ────────────────────────────────────────────────────────────────────
def days_until(exam_date):
    if not exam_date:
        return None
    delta = exam_date - date.today()
    return delta.days

def get_day_color(days):
    if days is None:
        return "#6b7190"
    if days <= 7:
        return "#ff5050"
    if days <= 21:
        return "#ffbe3c"
    return "#50dc8c"

DIFF_COLORS = {"Easy": "#50dc8c", "Medium": "#ffbe3c", "Hard": "#ff5050"}
ACCENT_COLORS = ["#c8f060", "#60d0f0", "#f060c8", "#f0a060", "#60f0a0", "#a060f0"]
TYPE_ICONS = {"read": "📖", "exercise": "✏️", "review": "🔄", "practice": "💪", "quiz": "❓"}

def get_client():
    try:
        return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    except Exception:
        st.error("⚠️ Add your Anthropic API key to `.streamlit/secrets.toml` as `ANTHROPIC_API_KEY = 'sk-...'`")
        st.stop()

def call_claude(messages, system="", pdf_base64=None):
    client = get_client()
    built = []
    for i, m in enumerate(messages):
        if pdf_base64 and i == 0 and m["role"] == "user":
            content = [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_base64}},
                {"type": "text", "text": m["content"]}
            ]
        else:
            content = m["content"]
        built.append({"role": m["role"], "content": content})

    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system,
        messages=built,
    )
    return resp.content[0].text

# ── Sidebar: subject list ──────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="accent-label">Study Coach</div>', unsafe_allow_html=True)
        st.markdown("### 📚 My Subjects")
        st.divider()

        if st.button("＋ New Subject", use_container_width=True, type="primary"):
            st.session_state.show_add_form = True
            st.session_state.current_subject = None

        st.divider()

        for sid, subj in st.session_state.subjects.items():
            days = days_until(subj.get("exam_date"))
            label = subj["name"]
            if days is not None:
                label += f"  ·  {days}d"
            if st.button(label, key=f"nav_{sid}", use_container_width=True):
                st.session_state.current_subject = sid
                st.session_state.show_add_form = False

        if st.session_state.current_subject:
            st.divider()
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.current_subject = None
                st.session_state.show_add_form = False

# ── Landing Page ───────────────────────────────────────────────────────────────
def render_landing():
    st.markdown('<div class="accent-label">Study Coach</div>', unsafe_allow_html=True)
    st.markdown("# Your subjects, **your plan.**")
    st.markdown('<p style="color:#6b7190; font-size:15px; margin-bottom:32px;">Add a subject, upload your material, and let AI build your daily study checklist — automatically.</p>', unsafe_allow_html=True)

    # Add form
    if st.session_state.show_add_form:
        with st.container():
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("**New Subject**")
            name = st.text_input("Subject name", placeholder="e.g. Machine Learning, Analysis II, Corporate Law…", key="new_subject_name")
            c1, c2 = st.columns([1, 3])
            with c1:
                if st.button("Create", type="primary"):
                    if name.strip():
                        sid = str(len(st.session_state.subjects) + 1) + "_" + name[:8].replace(" ", "")
                        st.session_state.subjects[sid] = {
                            "name": name.strip(),
                            "exam_date": None,
                            "difficulty": "Medium",
                            "hours_per_day": "2",
                            "prior_knowledge": "",
                            "pdf_base64": None,
                            "pdf_name": "",
                            "tasks": [],
                            "plan_generated": False,
                            "chat_messages": [],
                        }
                        st.session_state.current_subject = sid
                        st.session_state.show_add_form = False
                        st.rerun()
            with c2:
                if st.button("Cancel"):
                    st.session_state.show_add_form = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Subject grid
    if not st.session_state.subjects:
        st.markdown('<div style="text-align:center; padding:80px 0; color:#3a3f55;"><div style="font-size:48px; margin-bottom:16px;">📚</div><p style="font-family:Syne,sans-serif; font-size:18px;">No subjects yet — click "+ New Subject" in the sidebar</p></div>', unsafe_allow_html=True)
        return

    cols = st.columns(3)
    for i, (sid, subj) in enumerate(st.session_state.subjects.items()):
        accent = ACCENT_COLORS[i % len(ACCENT_COLORS)]
        days = days_until(subj.get("exam_date"))
        day_color = get_day_color(days)
        tasks = subj.get("tasks", [])
        done = sum(1 for t in tasks if t.get("done"))
        total = len(tasks)
        pct = int(done / total * 100) if total > 0 else 0

        with cols[i % 3]:
            exam_str = subj["exam_date"].strftime("%d %b %Y") if subj.get("exam_date") else "No exam set"
            days_str = f"{days} days left" if days and days > 0 else ("Today!" if days == 0 else "Exam passed") if days is not None else ""
            diff = subj.get("difficulty", "")
            diff_color = DIFF_COLORS.get(diff, "#6b7190")

            st.markdown(f"""
            <div class="subject-card" style="border-left: 3px solid {accent};">
                <div style="width:8px;height:8px;border-radius:50%;background:{accent};margin-bottom:12px;"></div>
                <div style="font-family:Syne,sans-serif;font-weight:700;font-size:18px;margin-bottom:6px;">{subj["name"]}</div>
                <div style="font-family:'DM Mono',monospace;font-size:11px;color:#6b7190;margin-bottom:4px;">Exam: {exam_str}</div>
                <div style="font-size:12px;color:{day_color};margin-bottom:10px;">{days_str}</div>
                {"<div style='font-family:DM Mono,monospace;font-size:11px;color:" + diff_color + ";margin-bottom:10px;text-transform:uppercase;'>" + diff + "</div>" if diff else ""}
                {"<div style='font-size:11px;color:#6b7190;margin-bottom:6px;'>Progress: " + str(done) + "/" + str(total) + "</div><div style='height:3px;background:#1e2130;border-radius:2px;'><div style='height:100%;width:" + str(pct) + "%;background:" + accent + ";border-radius:2px;'></div></div>" if total > 0 else "<div style='font-size:12px;color:#3a3f55;'>Click to set up →</div>"}
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Open {subj['name']}", key=f"open_{sid}", use_container_width=True):
                st.session_state.current_subject = sid
                st.rerun()

# ── Subject Page ───────────────────────────────────────────────────────────────
def render_subject(sid):
    subj = st.session_state.subjects[sid]
    days = days_until(subj.get("exam_date"))
    day_color = get_day_color(days)

    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<div class="accent-label">Subject</div>', unsafe_allow_html=True)
        st.markdown(f"# {subj['name']}")
    with col2:
        if days is not None:
            st.markdown(f'<div style="text-align:right;margin-top:20px;"><div style="font-family:DM Mono,monospace;font-size:36px;font-weight:500;color:{day_color};">{max(days,0)}</div><div style="font-size:11px;color:#6b7190;">days left</div></div>', unsafe_allow_html=True)

    # Progress bar
    tasks = subj.get("tasks", [])
    if tasks:
        done = sum(1 for t in tasks if t.get("done"))
        total = len(tasks)
        pct = done / total
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:11px;color:#6b7190;margin-bottom:4px;">Overall progress — {done}/{total} tasks</div>', unsafe_allow_html=True)
        st.progress(pct)

    st.divider()

    tab1, tab2, tab3 = st.tabs(["⚙️ Setup", "🗓 Study Plan", "🤖 AI Tutor"])

    # ── SETUP TAB ──────────────────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("**📅 Exam Date**")
        exam_date = st.date_input("Exam date", value=subj.get("exam_date"), key=f"exam_{sid}", label_visibility="collapsed")
        if exam_date:
            subj["exam_date"] = exam_date
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("**⚡ Difficulty**")
        diff = st.select_slider("Difficulty", options=["Easy", "Medium", "Hard"], value=subj.get("difficulty", "Medium"), key=f"diff_{sid}", label_visibility="collapsed")
        subj["difficulty"] = diff
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("**⏱ Hours available per day**")
        hours = st.select_slider("Hours", options=["1", "1.5", "2", "3", "4", "5"], value=subj.get("hours_per_day", "2"), key=f"hours_{sid}", label_visibility="collapsed")
        subj["hours_per_day"] = hours
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("**🧠 Your prior knowledge**")
        st.caption("Tell the AI what you already know so it can calibrate the plan.")
        prior = st.text_area("Prior knowledge", value=subj.get("prior_knowledge", ""), placeholder="e.g. I know basic linear algebra and Python, but haven't done any ML yet. Weak on probability.", key=f"prior_{sid}", label_visibility="collapsed")
        subj["prior_knowledge"] = prior
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("**📄 Upload Course Material (PDF)**")
        st.caption("The AI will read your slides/script and reference specific pages & exercises in your study plan.")
        if subj.get("pdf_name"):
            st.success(f"✓ {subj['pdf_name']}")
            if st.button("Remove PDF", key=f"remove_pdf_{sid}"):
                subj["pdf_base64"] = None
                subj["pdf_name"] = ""
                st.rerun()
        else:
            uploaded = st.file_uploader("Upload PDF", type=["pdf"], key=f"pdf_{sid}", label_visibility="collapsed")
            if uploaded:
                subj["pdf_base64"] = base64.b64encode(uploaded.read()).decode()
                subj["pdf_name"] = uploaded.name
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        btn_label = "✨ Generate My Study Plan" if not subj.get("plan_generated") else "🔄 Regenerate Study Plan"
        if st.button(btn_label, type="primary", use_container_width=True, key=f"gen_{sid}"):
            if not subj.get("exam_date"):
                st.error("Please set an exam date first.")
            else:
                generate_plan(sid)

    # ── PLAN TAB ───────────────────────────────────────────────────────────────
    with tab2:
        if not subj.get("plan_generated"):
            st.markdown('<div style="text-align:center;padding:60px 0;color:#3a3f55;"><div style="font-size:40px;margin-bottom:12px;">🗓</div><p style="font-family:Syne,sans-serif;font-size:16px;color:#454a60;">No plan yet — go to Setup to generate one</p></div>', unsafe_allow_html=True)
        else:
            tasks = subj.get("tasks", [])

            # Today highlight
            today_str = date.today().isoformat()
            today_tasks = [t for t in tasks if t.get("date") == today_str]
            if today_tasks:
                st.markdown("### 📌 Today")
                for t in today_tasks:
                    render_task(sid, t)
                st.divider()

            # Group by day
            days_map = {}
            for t in tasks:
                d = t.get("day", 1)
                if d not in days_map:
                    days_map[d] = {"day": d, "date": t.get("date", ""), "tasks": []}
                days_map[d]["tasks"].append(t)

            for day_num in sorted(days_map.keys()):
                dg = days_map[day_num]
                is_today = dg["date"] == today_str
                is_past = dg["date"] < today_str if dg["date"] else False
                done_count = sum(1 for t in dg["tasks"] if t.get("done"))
                total_count = len(dg["tasks"])

                day_label = f"Day {day_num}"
                if dg["date"]:
                    day_label += f"  ·  {dg['date']}"
                if is_today:
                    day_label += "  🟢 TODAY"
                elif is_past:
                    day_label += "  (past)"

                with st.expander(f"{day_label}  —  {done_count}/{total_count}", expanded=is_today):
                    for t in dg["tasks"]:
                        render_task(sid, t)

    # ── CHAT TAB ───────────────────────────────────────────────────────────────
    with tab3:
        chat_messages = subj.get("chat_messages", [])

        # Display chat history
        chat_container = st.container()
        with chat_container:
            if not chat_messages:
                st.markdown(f"""
                <div style="text-align:center;padding:40px 0;color:#3a3f55;">
                    <div style="font-size:36px;margin-bottom:12px;">🤖</div>
                    <p style="font-family:Syne,sans-serif;font-weight:600;color:#454a60;margin-bottom:6px;">Your AI tutor is ready</p>
                    <p style="font-size:13px;color:#3a3f55;max-width:320px;margin:0 auto;">
                        Ask anything about {subj['name']}. Request explanations, exercises, quick quizzes, or concept reviews.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            for msg in chat_messages:
                if msg["role"] == "user":
                    st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="ai-bubble">{msg["content"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

        # Quick start prompts
        if not chat_messages:
            st.markdown("**Quick start:**")
            qs_cols = st.columns(2)
            prompts = [
                "Give me a quick quiz on a key topic",
                "Explain the most important concept",
                "What should I focus on before the exam?",
                "Give me a practice exercise",
            ]
            for i, p in enumerate(prompts):
                with qs_cols[i % 2]:
                    if st.button(p, key=f"qs_{sid}_{i}", use_container_width=True):
                        send_chat(sid, p)
                        st.rerun()

        # Input
        st.divider()
        with st.form(key=f"chat_form_{sid}", clear_on_submit=True):
            col_in, col_btn = st.columns([5, 1])
            with col_in:
                user_input = st.text_input("Message", placeholder=f"Ask about {subj['name']}…", label_visibility="collapsed", key=f"chat_input_{sid}")
            with col_btn:
                submitted = st.form_submit_button("Send", type="primary", use_container_width=True)
            if submitted and user_input.strip():
                send_chat(sid, user_input.strip())
                st.rerun()

# ── Task rendering ─────────────────────────────────────────────────────────────
def render_task(sid, task):
    subj = st.session_state.subjects[sid]
    tasks = subj["tasks"]
    task_id = task["id"]
    icon = TYPE_ICONS.get(task.get("type", ""), "▸")
    label = f"{icon} {task['text']}"
    if task.get("duration"):
        label += f"  ·  {task['duration']}"

    checked = st.checkbox(label, value=task.get("done", False), key=f"task_{sid}_{task_id}")
    # Update done state
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = checked
            break

# ── Generate plan ──────────────────────────────────────────────────────────────
def generate_plan(sid):
    subj = st.session_state.subjects[sid]
    days = days_until(subj["exam_date"])

    with st.spinner("✨ Reading your material and building your study plan…"):
        prompt = f"""You are an expert study planner. The student has {days} days until their {subj['name']} exam.
Difficulty: {subj.get('difficulty', 'Medium')}. Available hours per day: {subj.get('hours_per_day', '2')}h.
Prior knowledge: {subj.get('prior_knowledge') or 'some basics'}.
{"Course material (PDF) is attached. Use it to create specific tasks referencing actual content (e.g. 'Read slides 12-20 on Gradient Descent', 'Solve exercise 3.2 on page 45')." if subj.get('pdf_base64') else "No material uploaded — create generic but structured tasks."}

Return ONLY a valid JSON array (no markdown, no backticks, no explanation) like:
[
  {{"day": 1, "date": "YYYY-MM-DD", "tasks": [{{"id": "t1", "text": "Read lecture 1: Introduction (slides 1-15)", "type": "read", "duration": "30min"}}, ...]}},
  ...
]
Create {min(days, 30)} day entries starting from today ({date.today().isoformat()}).
Each day has 2-4 tasks appropriate for {subj.get('hours_per_day', '2')}h study.
Include a mix of reading, exercises, and review sessions. Be very specific about what to study.
Types must be one of: read, exercise, review, practice, quiz."""

        try:
            response_text = call_claude(
                [{"role": "user", "content": prompt}],
                system="",
                pdf_base64=subj.get("pdf_base64")
            )
            clean = response_text.strip().replace("```json", "").replace("```", "").strip()
            plan_days = json.loads(clean)

            flat_tasks = []
            for d in plan_days:
                for t in d["tasks"]:
                    flat_tasks.append({
                        "id": f"{d['day']}_{t['id']}",
                        "day": d["day"],
                        "date": d["date"],
                        "text": t["text"],
                        "type": t.get("type", "read"),
                        "duration": t.get("duration", ""),
                        "done": False,
                    })

            subj["tasks"] = flat_tasks
            subj["plan_generated"] = True
            st.success(f"✅ Study plan generated — {len(flat_tasks)} tasks across {len(plan_days)} days!")
            st.rerun()

        except Exception as e:
            st.error(f"Failed to generate plan: {e}")

# ── Send chat message ──────────────────────────────────────────────────────────
def send_chat(sid, user_input):
    subj = st.session_state.subjects[sid]
    chat_messages = subj.setdefault("chat_messages", [])
    chat_messages.append({"role": "user", "content": user_input})

    system = f"""You are a dedicated study tutor for the subject "{subj['name']}".
{"The student has uploaded their course material (PDF). Use it to give specific, relevant answers." if subj.get('pdf_base64') else "No material uploaded."}
Help the student understand concepts, work through exercises, answer questions, and quiz them.
Keep responses focused, clear, and educational. Use examples. If the student asks for an exercise, give one and then evaluate their answer."""

    # Only send PDF on the very first message
    use_pdf = subj.get("pdf_base64") if len(chat_messages) == 1 else None

    with st.spinner("Thinking…"):
        try:
            reply = call_claude(chat_messages, system=system, pdf_base64=use_pdf)
            chat_messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            chat_messages.append({"role": "assistant", "content": f"Error: {e}"})

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    render_sidebar()

    if st.session_state.current_subject and st.session_state.current_subject in st.session_state.subjects:
        render_subject(st.session_state.current_subject)
    else:
        render_landing()

if __name__ == "__main__":
    main()