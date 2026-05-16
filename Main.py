import streamlit as st
import anthropic
import json
import base64
from datetime import date, timedelta
import requests

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Study Coach 🌸",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,400;0,600;0,700;0,800;0,900;1,400&family=Quicksand:wght@400;500;600;700;800&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #fdf6ff 0%, #fff0f8 40%, #f0f8ff 100%) !important;
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 900px !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fff0fb 0%, #f3eeff 100%) !important;
    border-right: 2px solid #f0d6f5 !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: white !important;
    border: 2px solid #f0d6f5 !important;
    border-radius: 16px !important;
    color: #7c4d99 !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(180,120,220,0.1) !important;
    margin-bottom: 4px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #f9eeff !important;
    border-color: #c084e8 !important;
    color: #7c4d99 !important;
    transform: translateX(3px) !important;
}
[data-testid="stSidebar"] .stButton > button:focus,
[data-testid="stSidebar"] .stButton > button:active {
    background: #f9eeff !important;
    border-color: #c084e8 !important;
    color: #7c4d99 !important;
}

/* ── Hide Material icon text that leaks ── */
[data-testid="stSidebarCollapseButton"] span,
button[aria-label="Close sidebar"] span,
[data-testid="collapsedControl"] span {
    display: none !important;
}

/* ── Primary buttons ── */
.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #e879f9, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 20px !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 15px rgba(168,85,247,0.35) !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #e879f9, #a855f7) !important;
    color: white !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(168,85,247,0.45) !important;
}
.stButton > button[kind="primary"]:focus,
.stButton > button[kind="primary"]:active {
    background: linear-gradient(135deg, #e879f9, #a855f7) !important;
    color: white !important;
}

.stButton > button {
    border-radius: 16px !important;
    font-weight: 700 !important;
    transition: all 0.2s !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stDateInput > div > div > input {
    background: white !important;
    border: 2px solid #e9d5ff !important;
    border-radius: 14px !important;
    color: #4a1d75 !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #a855f7 !important;
    box-shadow: 0 0 0 3px rgba(168,85,247,0.15) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.8) !important;
    border-radius: 20px !important;
    padding: 5px !important;
    gap: 4px !important;
    border: 2px solid #f0d6f5 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 16px !important;
    color: #9d75c2 !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 8px 20px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #e879f9, #a855f7) !important;
    color: white !important;
}
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 20px !important; }

/* ── Progress ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #e879f9, #a855f7) !important;
    border-radius: 10px !important;
}
.stProgress > div > div { background: #f0d6f5 !important; border-radius: 10px !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: white !important;
    border-radius: 14px !important;
    border: 2px solid #f0d6f5 !important;
    color: #6d28d9 !important;
    font-weight: 700 !important;
}
.streamlit-expanderContent {
    background: #fefcff !important;
    border: 2px solid #f0d6f5 !important;
    border-top: none !important;
    border-radius: 0 0 14px 14px !important;
}

/* ── Checkboxes ── */
.stCheckbox > label { color: #4a1d75 !important; font-weight: 600 !important; font-size: 14px !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: white !important;
    border: 2px dashed #c084e8 !important;
    border-radius: 16px !important;
}

/* ── Alerts ── */
.stSuccess { background: #f0fdf4 !important; border: 2px solid #86efac !important; border-radius: 14px !important; }
.stError   { background: #fff1f2 !important; border: 2px solid #fda4af !important; border-radius: 14px !important; }
.stAlert   { border-radius: 14px !important; }
hr         { border-color: #f0d6f5 !important; }

/* ── Cards ── */
.cute-card {
    background: white;
    border: 2px solid #f0d6f5;
    border-radius: 20px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 16px rgba(180,120,220,0.08);
    transition: all 0.2s;
}

/* ── Chat bubbles ── */
.user-bubble {
    background: linear-gradient(135deg, #e879f9, #a855f7);
    color: white;
    border-radius: 20px 20px 4px 20px;
    padding: 12px 18px;
    margin: 8px 0 8px auto;
    max-width: 75%;
    display: table;
    font-size: 14px;
    line-height: 1.5;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(168,85,247,0.3);
}
.ai-bubble {
    background: white;
    color: #4a1d75;
    border-radius: 20px 20px 20px 4px;
    padding: 12px 18px;
    margin: 8px 0;
    max-width: 80%;
    display: table;
    font-size: 14px;
    line-height: 1.6;
    border: 2px solid #f0d6f5;
    box-shadow: 0 2px 10px rgba(180,120,220,0.1);
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def days_until(exam_date):
    if not exam_date:
        return None
    return (exam_date - date.today()).days

def get_day_color(days):
    if days is None: return "#9d75c2"
    if days <= 7:    return "#f43f5e"
    if days <= 21:   return "#f59e0b"
    return "#22c55e"

DIFF_COLORS   = {"Easy": "#22c55e", "Medium": "#f59e0b", "Hard": "#f43f5e"}
ACCENT_COLORS = ["#e879f9","#a78bfa","#60a5fa","#34d399","#fb923c","#f472b6"]
TYPE_ICONS    = {"read":"📖","exercise":"✏️","review":"🔄","practice":"💪","quiz":"❓"}
EMOJIS        = ["🌸","🌻","🦋","🌈","⭐","🍀"]

def get_client():
    try:
        return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    except Exception:
        st.error("Add ANTHROPIC_API_KEY to your Streamlit secrets!")
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

# ── Supabase ───────────────────────────────────────────────────────────────────
FIXED_ID = "maira_study_coach"  # single-user fixed key

def sb_headers():
    return {
        "apikey": st.secrets["SUPABASE_KEY"],
        "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }

def sb_url():
    return st.secrets["SUPABASE_URL"].rstrip("/") + "/rest/v1/subjects"

def load_from_db():
    try:
        r = requests.get(sb_url(), headers=sb_headers(),
                         params={"id": f"eq.{FIXED_ID}"})
        rows = r.json()
        if rows and isinstance(rows, list) and len(rows) > 0:
            raw = rows[0]["data"]
            # Convert exam_date strings back to date objects
            for sid, subj in raw.items():
                if subj.get("exam_date"):
                    try:
                        subj["exam_date"] = date.fromisoformat(subj["exam_date"])
                    except Exception:
                        subj["exam_date"] = None
            return raw
    except Exception:
        pass
    return {}

def save_to_db(subjects):
    try:
        # Convert date objects to strings for JSON
        serializable = {}
        for sid, subj in subjects.items():
            s = dict(subj)
            if isinstance(s.get("exam_date"), date):
                s["exam_date"] = s["exam_date"].isoformat()
            serializable[sid] = s
        requests.post(sb_url(), headers=sb_headers(),
                      json={"id": FIXED_ID, "data": serializable})
    except Exception:
        pass


# ── Session state ──────────────────────────────────────────────────────────────
if "subjects" not in st.session_state:
    st.session_state.subjects = load_from_db()
if "current_subject" not in st.session_state:
    st.session_state.current_subject = None
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

# ── Sidebar ────────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🌸 Study Coach")
        st.markdown("<p style='color:#9d75c2;font-size:13px;margin-top:-10px;margin-bottom:16px;font-weight:600;'>your personal study bestie ✨</p>", unsafe_allow_html=True)
        st.divider()

        if st.button("＋ New Subject ✨", use_container_width=True, type="primary"):
            st.session_state.show_add_form = not st.session_state.show_add_form
            st.rerun()

        if st.session_state.show_add_form:
            new_name = st.text_input("Subject name", placeholder="e.g. Machine Learning…",
                                     key="new_subject_input")
            if st.button("Create 🌸", type="primary", use_container_width=True, key="create_subject_btn"):
                if new_name.strip():
                    sid = f"{len(st.session_state.subjects)}_{new_name[:10].replace(' ','')}"
                    st.session_state.subjects[sid] = {
                        "name": new_name.strip(), "exam_date": None,
                        "difficulty": "Medium", "hours_per_day": "2",
                        "prior_knowledge": "", "pdf_base64": None,
                        "pdf_name": "", "pdf_files": [], "tasks": [],
                        "plan_generated": False, "chat_messages": [],
                    }
                    save_to_db(st.session_state.subjects)
                    st.session_state.current_subject = sid
                    st.session_state.show_add_form   = False
                    st.rerun()

        st.markdown("<p style='color:#9d75c2;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;margin:16px 0 8px;'>My Subjects</p>", unsafe_allow_html=True)

        if not st.session_state.subjects:
            st.markdown("<p style='color:#c4a8e0;font-size:13px;font-style:italic;'>No subjects yet 🌱</p>", unsafe_allow_html=True)

        for i, (sid, subj) in enumerate(st.session_state.subjects.items()):
            days  = days_until(subj.get("exam_date"))
            emoji = EMOJIS[i % len(EMOJIS)]
            day_str = f" · {days}d" if days is not None and days >= 0 else ""
            if st.button(f"{emoji} {subj['name']}{day_str}", key=f"nav_{sid}", use_container_width=True):
                st.session_state.current_subject = sid
                st.session_state.show_add_form   = False
                st.rerun()

        if st.session_state.current_subject:
            st.divider()
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.current_subject = None
                st.rerun()

# ── Landing ────────────────────────────────────────────────────────────────────
def render_landing():
    st.write("")
    st.markdown("# 📚 Study Coach")
    st.markdown("Add your subjects, upload your material, and let AI build your perfect daily study plan.")
    st.divider()

    if not st.session_state.subjects:
        st.write("")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("### 📚\n**Add Your Subjects**\n\nCreate a page for each subject with its exam date and difficulty level.")
        with col2:
            st.info("### 📄\n**Upload Your Material**\n\nUpload your lecture PDFs and the AI reads them to plan specifically for you.")
        with col3:
            st.info("### ✅\n**Get Your Daily Plan**\n\nA day-by-day checklist with specific tasks — just tick them off as you go!")

        st.write("")
        st.success("🌱  **Ready to start?** Click **+ New Subject** in the sidebar to add your first subject ✨")
        return

    cols = st.columns(min(len(st.session_state.subjects), 3))
    for i, (sid, subj) in enumerate(st.session_state.subjects.items()):
        accent   = ACCENT_COLORS[i % len(ACCENT_COLORS)]
        emoji    = EMOJIS[i % len(EMOJIS)]
        days     = days_until(subj.get("exam_date"))
        dc       = get_day_color(days)
        tasks    = subj.get("tasks", [])
        done     = sum(1 for t in tasks if t.get("done"))
        total    = len(tasks)
        pct      = int(done / total * 100) if total else 0
        exam_str = subj["exam_date"].strftime("%d %b %Y") if subj.get("exam_date") else "No date set"
        days_str = f"{days} days left" if days and days > 0 else ("Today! 🔥" if days == 0 else "Passed ✅") if days is not None else ""
        diff     = subj.get("difficulty","")
        diff_col = DIFF_COLORS.get(diff, "#9d75c2")

        with cols[i % 3]:
            progress_html = f"""<div style='margin-top:10px;'>
                <div style='display:flex;justify-content:space-between;font-size:11px;color:#9d75c2;margin-bottom:4px;'>
                <span>Progress</span><span>{done}/{total}</span></div>
                <div style='height:6px;background:#f0d6f5;border-radius:10px;'>
                <div style='height:100%;width:{pct}%;background:{accent};border-radius:10px;'></div>
                </div></div>""" if total else ""

            st.markdown(f"""
            <div class="cute-card" style="border-left:4px solid {accent};">
                <div style="font-size:28px;margin-bottom:8px;">{emoji}</div>
                <div style="font-family:'Quicksand',sans-serif;font-weight:800;font-size:18px;color:#4a1d75;margin-bottom:6px;">{subj['name']}</div>
                <div style="font-size:12px;color:#9d75c2;margin-bottom:4px;">📅 {exam_str}</div>
                <div style="font-size:13px;color:{dc};font-weight:700;margin-bottom:8px;">{days_str}</div>
                {"<span style='font-size:11px;font-weight:700;color:" + diff_col + ";background:" + diff_col + "22;padding:2px 10px;border-radius:20px;'>" + diff + "</span>" if diff else ""}
                {progress_html}
            </div>""", unsafe_allow_html=True)

            if st.button(f"Open {emoji}", key=f"open_{sid}", use_container_width=True):
                st.session_state.current_subject = sid
                st.rerun()

# ── Subject page ───────────────────────────────────────────────────────────────
def render_subject(sid):
    subj  = st.session_state.subjects[sid]
    days  = days_until(subj.get("exam_date"))
    dc    = get_day_color(days)
    i     = list(st.session_state.subjects.keys()).index(sid)
    emoji = EMOJIS[i % len(EMOJIS)]

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="margin-bottom:8px;">
            <span style="font-size:13px;font-weight:700;color:#a855f7;text-transform:uppercase;letter-spacing:0.1em;">Subject</span><br>
            <span style="font-family:'Quicksand',sans-serif;font-size:32px;font-weight:800;color:#4a1d75;">{emoji} {subj['name']}</span>
        </div>""", unsafe_allow_html=True)
    with col2:
        if days is not None:
            st.markdown(f"""
            <div style="text-align:center;background:white;border:2px solid #f0d6f5;
                        border-radius:20px;padding:14px;margin-top:8px;
                        box-shadow:0 4px 12px rgba(168,85,247,0.1);">
                <div style="font-size:32px;font-weight:900;color:{dc};">{max(days,0)}</div>
                <div style="font-size:12px;color:#9d75c2;font-weight:700;">days left</div>
            </div>""", unsafe_allow_html=True)

    tasks = subj.get("tasks", [])
    if tasks:
        done  = sum(1 for t in tasks if t.get("done"))
        total = len(tasks)
        st.markdown(f"<p style='color:#9d75c2;font-size:13px;font-weight:700;margin-bottom:4px;'>Progress ✨ — {done}/{total} tasks done</p>", unsafe_allow_html=True)
        st.progress(done / total)

    st.divider()
    tab1, tab2, tab3 = st.tabs(["⚙️ Setup", "🗓 Study Plan", "🤖 AI Tutor"])

    # SETUP
    with tab1:
        st.markdown("**📅 Exam Date**")
        exam_date = st.date_input("Exam", value=subj.get("exam_date"),
                                  key=f"exam_{sid}", label_visibility="collapsed")
        if exam_date: subj["exam_date"] = exam_date

        st.markdown("**⚡ Difficulty**")
        diff = st.select_slider("Diff", options=["Easy","Medium","Hard"],
                                value=subj.get("difficulty","Medium"),
                                key=f"diff_{sid}", label_visibility="collapsed")
        subj["difficulty"] = diff
        dc2 = DIFF_COLORS[diff]
        mood = "🟢 Manageable!" if diff=="Easy" else "🟡 Challenge mode!" if diff=="Medium" else "🔴 Beast mode!"
        st.markdown(f"<span style='color:{dc2};font-weight:700;font-size:14px;'>{mood}</span>", unsafe_allow_html=True)

        st.write("")
        st.markdown("**⏱ Hours per day**")
        hours = st.select_slider("Hours", options=["1","1.5","2","3","4","5"],
                                 value=subj.get("hours_per_day","2"),
                                 key=f"hours_{sid}", label_visibility="collapsed")
        subj["hours_per_day"] = hours

        st.write("")
        st.markdown("**🧠 Your Prior Knowledge**")
        st.caption("Tell the AI what you already know so it can build the perfect plan for you!")
        prior = st.text_area("Prior", value=subj.get("prior_knowledge",""),
                             placeholder="e.g. I know basic linear algebra but haven't touched ML yet.",
                             key=f"prior_{sid}", label_visibility="collapsed", height=90)
        subj["prior_knowledge"] = prior

        st.write("")
        st.markdown("**📄 Course Material (PDFs)**")
        existing = subj.get("pdf_files", [])

        # Show already uploaded files
        if existing:
            st.caption(f"{len(existing)} file(s) uploaded:")
            for i, f in enumerate(existing):
                col_f, col_x = st.columns([5, 1])
                with col_f:
                    st.success(f"✓ {f['name']}")
                with col_x:
                    if st.button("✕", key=f"rm_{sid}_{i}"):
                        subj["pdf_files"].pop(i)
                        if subj["pdf_files"]:
                            subj["pdf_base64"] = subj["pdf_files"][0]["data"]
                            subj["pdf_name"]   = subj["pdf_files"][0]["name"]
                        else:
                            subj["pdf_base64"] = None
                            subj["pdf_name"]   = ""
                        save_to_db(st.session_state.subjects)
                        st.rerun()

        # Always show uploader to add more
        st.caption("Add a PDF (upload one at a time to add multiple):")
        up = st.file_uploader(
            "Add PDF", type=["pdf"],
            key=f"pdf_{sid}_{len(existing)}",
        )
        if up is not None:
            names = [f["name"] for f in existing]
            if up.name not in names:
                data = base64.b64encode(up.read()).decode()
                subj["pdf_files"] = existing + [{"name": up.name, "data": data}]
                subj["pdf_base64"] = subj["pdf_files"][0]["data"]
                subj["pdf_name"]   = subj["pdf_files"][0]["name"]
                save_to_db(st.session_state.subjects)
                st.rerun()

        st.divider()
        lbl = "✨ Generate My Study Plan!" if not subj.get("plan_generated") else "🔄 Regenerate Study Plan"
        if st.button(lbl, type="primary", use_container_width=True, key=f"gen_{sid}"):
            if not subj.get("exam_date"):
                st.error("Please set an exam date first! 📅")
            else:
                generate_plan(sid)

    # PLAN
    with tab2:
        if not subj.get("plan_generated"):
            st.markdown("""
            <div style="text-align:center;padding:60px 0;">
                <div style="font-size:48px;margin-bottom:16px;">🗓</div>
                <p style="font-family:'Quicksand',sans-serif;font-size:18px;font-weight:700;color:#9d75c2;">No plan yet!</p>
                <p style="color:#c4a8e0;font-size:14px;">Go to Setup and hit Generate ✨</p>
            </div>""", unsafe_allow_html=True)
        else:
            tasks     = subj.get("tasks", [])
            today_str = date.today().isoformat()
            today_tasks = [t for t in tasks if t.get("date") == today_str]

            if today_tasks:
                st.markdown("""<div style="background:linear-gradient(135deg,#fdf4ff,#faf5ff);
                    border:2px solid #e9d5ff;border-radius:20px;padding:20px;margin-bottom:20px;">
                    <div style="font-family:'Quicksand',sans-serif;font-weight:800;font-size:18px;
                    color:#7c3aed;margin-bottom:12px;">📌 Today's Tasks</div>""", unsafe_allow_html=True)
                for t in today_tasks:
                    render_task(sid, t)
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()

            days_map = {}
            for t in tasks:
                d = t.get("day", 1)
                if d not in days_map:
                    days_map[d] = {"day": d, "date": t.get("date",""), "tasks": []}
                days_map[d]["tasks"].append(t)

            for day_num in sorted(days_map.keys()):
                dg          = days_map[day_num]
                is_today    = dg["date"] == today_str
                is_past     = dg["date"] < today_str if dg["date"] else False
                done_count  = sum(1 for t in dg["tasks"] if t.get("done"))
                total_count = len(dg["tasks"])
                tag = "  🌸 TODAY" if is_today else ("  (past)" if is_past else "")
                label = f"Day {day_num} · {dg['date']}{tag}  —  {done_count}/{total_count} done"
                with st.expander(label, expanded=is_today):
                    for t in dg["tasks"]:
                        render_task(sid, t)

    # CHAT
    with tab3:
        chat_messages = subj.get("chat_messages", [])

        if not chat_messages:
            st.markdown(f"""
            <div style="text-align:center;padding:40px 20px;background:white;
                        border:2px solid #f0d6f5;border-radius:20px;margin-bottom:20px;">
                <div style="font-size:40px;margin-bottom:12px;">🤖✨</div>
                <p style="font-family:'Quicksand',sans-serif;font-weight:800;font-size:18px;
                           color:#7c3aed;margin-bottom:8px;">Your AI Tutor is ready!</p>
                <p style="color:#9d75c2;font-size:14px;max-width:340px;margin:0 auto;">
                    Ask me anything about {subj['name']} 🌸
                </p>
            </div>""", unsafe_allow_html=True)
            st.markdown("**Quick start 🚀**")
            qs_cols = st.columns(2)
            prompts = ["Give me a quick quiz 🎯","Explain a key concept 💡",
                       "What to focus on for exam? 📝","Give me a practice exercise ✏️"]
            for j, p in enumerate(prompts):
                with qs_cols[j % 2]:
                    if st.button(p, key=f"qs_{sid}_{j}", use_container_width=True):
                        send_chat(sid, p)
                        st.rerun()

        for msg in chat_messages:
            safe = msg["content"].replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")
            if msg["role"] == "user":
                st.markdown(f'<div class="user-bubble">{safe}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-bubble">{safe}</div>', unsafe_allow_html=True)

        st.divider()
        with st.form(key=f"chat_form_{sid}", clear_on_submit=True):
            col_in, col_btn = st.columns([5, 1])
            with col_in:
                user_input = st.text_input("msg", placeholder=f"Ask about {subj['name']} 🌸",
                                           label_visibility="collapsed", key=f"ci_{sid}")
            with col_btn:
                submitted = st.form_submit_button("Send ✨", use_container_width=True)
            if submitted and user_input.strip():
                send_chat(sid, user_input.strip())
                st.rerun()

# ── Task row ───────────────────────────────────────────────────────────────────
def render_task(sid, task):
    tasks   = st.session_state.subjects[sid]["tasks"]
    task_id = task["id"]
    icon    = TYPE_ICONS.get(task.get("type",""), "▸")
    label   = f"{icon} {task['text']}"
    if task.get("duration"):
        label += f"  ·  {task['duration']}"
    checked = st.checkbox(label, value=task.get("done", False), key=f"task_{sid}_{task_id}")
    for t in tasks:
        if t["id"] == task_id:
            if t["done"] != checked:
                t["done"] = checked
                save_to_db(st.session_state.subjects)
            break

# ── Generate plan ──────────────────────────────────────────────────────────────
def generate_plan(sid):
    subj = st.session_state.subjects[sid]
    days = days_until(subj["exam_date"])
    pdf_files = subj.get("pdf_files", [])
    has_pdfs = len(pdf_files) > 0
    pdf_names = ", ".join(f["name"] for f in pdf_files) if has_pdfs else ""
    with st.spinner("🌸 Reading your material and building your study plan…"):
        prompt = f"""You are an expert study planner. The student has {days} days until their {subj['name']} exam.
Difficulty: {subj.get('difficulty','Medium')}. Hours per day: {subj.get('hours_per_day','2')}h.
Prior knowledge: {subj.get('prior_knowledge') or 'some basics'}.
{"Uploaded PDFs: " + pdf_names + ". All PDFs are attached. Read them carefully and:" if has_pdfs else "No material uploaded — create well-structured tasks."}
{"- Reference specific content (e.g. 'Read slides 12-20 on Gradient Descent', 'Solve exercise 3.2 page 45')" if has_pdfs else ""}
{"- If any PDF mentions exam topics, exam format, or past exam questions — prioritise those in the plan" if has_pdfs else ""}
{"- If a PDF is a general intro/overview lecture, use it to understand the subject structure" if has_pdfs else ""}
{"- Spread the lectures/topics logically across days" if has_pdfs else ""}

Return ONLY a valid JSON array (no markdown, no backticks) like:
[
  {{"day": 1, "date": "YYYY-MM-DD", "tasks": [{{"id": "t1", "text": "Read lecture 1: Intro (slides 1-15)", "type": "read", "duration": "30min"}}, ...]}},
  ...
]
Create {min(days, 30)} day entries starting from today ({date.today().isoformat()}).
Each day: 2-4 tasks for {subj.get('hours_per_day','2')}h. Mix of read/exercise/review/practice/quiz. Be very specific, name the actual topics and page/slide numbers."""
        try:
            # Send all PDFs to Claude
            if has_pdfs:
                user_content = []
                for f in pdf_files:
                    user_content.append({"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": f["data"]}})
                user_content.append({"type": "text", "text": prompt})
                msgs = [{"role": "user", "content": user_content}]
            else:
                msgs = [{"role": "user", "content": prompt}]
            text  = call_claude(msgs)
            clean = text.strip().replace("```json","").replace("```","").strip()
            plan  = json.loads(clean)
            flat  = []
            for d in plan:
                for t in d["tasks"]:
                    flat.append({
                        "id": f"{d['day']}_{t['id']}", "day": d["day"],
                        "date": d["date"], "text": t["text"],
                        "type": t.get("type","read"), "duration": t.get("duration",""), "done": False,
                    })
            subj["tasks"]          = flat
            subj["plan_generated"] = True
            save_to_db(st.session_state.subjects)
            st.success(f"🎉 Done! {len(flat)} tasks across {len(plan)} days!")
            st.rerun()
        except Exception as e:
            st.error(f"Oops! Something went wrong: {e}")

# ── Send chat ──────────────────────────────────────────────────────────────────
def send_chat(sid, user_input):
    subj = st.session_state.subjects[sid]
    msgs = subj.setdefault("chat_messages", [])
    pdf_files = subj.get("pdf_files", [])
    has_pdfs = len(pdf_files) > 0
    system = f"""You are a friendly, encouraging study tutor for "{subj['name']}".
{("The student uploaded " + str(len(pdf_files)) + " PDF file(s) with their course material. Use them for specific, accurate answers. Reference slide numbers, page numbers, or exercise numbers where relevant. If the PDFs mention exam format or exam topics, highlight those when relevant.") if has_pdfs else "No material uploaded."}
Help with concepts, exercises, quizzes, exam tips. Be warm, clear and supportive. Use examples."""
    # On first message, attach all PDFs
    is_first = len(msgs) == 0
    msgs.append({"role":"user","content":user_input})
    with st.spinner("🤔 Thinking…"):
        try:
            if is_first and has_pdfs:
                user_content = []
                for f in pdf_files:
                    user_content.append({"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": f["data"]}})
                user_content.append({"type": "text", "text": user_input})
                api_msgs = [{"role": "user", "content": user_content}]
            else:
                api_msgs = msgs
            reply = call_claude(api_msgs, system=system)
            msgs.append({"role":"assistant","content":reply})
            save_to_db(st.session_state.subjects)
        except Exception as e:
            msgs.append({"role":"assistant","content":f"Something went wrong: {e}"})

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    render_sidebar()
    if st.session_state.current_subject and st.session_state.current_subject in st.session_state.subjects:
        render_subject(st.session_state.current_subject)
    else:
        render_landing()

if __name__ == "__main__":
    main()