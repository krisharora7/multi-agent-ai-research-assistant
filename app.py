"""
Research Multi-Agent System - Streamlit UI
Backend: agents.py + tools.py + pipeline.py (LangChain)

Run:  streamlit run app.py
"""

import re
import sys
import time
from datetime import datetime

import streamlit as st

# ----------------------------------------------------------------------------
# Page config (must be the first Streamlit call)
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Research Agents | Multi-Agent AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load .env (API keys) if python-dotenv is available
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

# Backend imports (same ones pipeline.py uses)
IMPORT_ERROR = None
try:
    from agents import (
        build_search_agent,
        build_reader_agent,
        writer_chain,
        critic_chain,
    )
except Exception as e:  # shown nicely in the UI instead of crashing
    IMPORT_ERROR = e

# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background:
        radial-gradient(1200px 600px at 10% -10%, rgba(99,102,241,0.18), transparent 60%),
        radial-gradient(900px 500px at 100% 0%, rgba(236,72,153,0.14), transparent 55%),
        radial-gradient(900px 600px at 50% 110%, rgba(34,211,238,0.10), transparent 60%),
        #0b0d17;
    color: #e5e7eb;
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1200px; }

/* Hero */
.hero {
    position: relative;
    padding: 2.4rem 2.2rem;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(99,102,241,0.20), rgba(236,72,153,0.12));
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(14px);
    overflow: hidden;
    margin-bottom: 1.6rem;
}
.hero::after {
    content: ""; position: absolute; inset: -40% -10% auto auto;
    width: 420px; height: 420px; border-radius: 50%;
    background: radial-gradient(circle, rgba(139,92,246,0.35), transparent 65%);
    filter: blur(20px); pointer-events: none;
}
.hero-badge {
    display: inline-block; padding: 0.28rem 0.8rem; border-radius: 999px;
    font-size: 0.75rem; font-weight: 600; letter-spacing: .06em; text-transform: uppercase;
    background: rgba(99,102,241,0.18); border: 1px solid rgba(129,140,248,0.4); color: #c7d2fe;
}
.hero h1 {
    margin: 0.9rem 0 0.4rem 0; font-size: 2.7rem; font-weight: 800; line-height: 1.1;
    background: linear-gradient(90deg, #a5b4fc, #f0abfc, #67e8f9);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero p { margin: 0; color: #9ca3af; font-size: 1.05rem; max-width: 720px; }

/* Agent pills */
.agent-row { display: flex; gap: .6rem; flex-wrap: wrap; margin-top: 1.2rem; }
.agent-pill {
    padding: .35rem .8rem; border-radius: 999px; font-size: .8rem; font-weight: 500;
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #d1d5db;
}

/* Stepper */
.stepper { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1.2rem 0 1.4rem 0; }
@media (max-width: 900px) { .stepper { grid-template-columns: repeat(2, 1fr); } }
.step {
    padding: 1.1rem 1rem; border-radius: 18px; text-align: left;
    background: rgba(255,255,255,0.035); border: 1px solid rgba(255,255,255,0.08);
    transition: all .3s ease;
}
.step .icon { font-size: 1.6rem; }
.step .name { font-weight: 700; margin-top: .35rem; color: #f3f4f6; }
.step .desc { font-size: .78rem; color: #9ca3af; margin-top: .15rem; min-height: 2.1em; }
.step .status { margin-top: .6rem; font-size: .75rem; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; }
.step.pending .status { color: #6b7280; }
.step.running {
    border-color: rgba(129,140,248,0.8);
    background: linear-gradient(135deg, rgba(99,102,241,0.22), rgba(236,72,153,0.12));
    box-shadow: 0 0 0 1px rgba(129,140,248,0.4), 0 10px 40px -10px rgba(99,102,241,0.6);
    animation: pulse 1.6s ease-in-out infinite;
}
.step.running .status { color: #c7d2fe; }
.step.done { border-color: rgba(52,211,153,0.5); background: rgba(16,185,129,0.08); }
.step.done .status { color: #6ee7b7; }
.step.error { border-color: rgba(248,113,113,0.6); background: rgba(239,68,68,0.10); }
.step.error .status { color: #fca5a5; }
@keyframes pulse { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-3px); } }

/* Metric cards */
.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1rem 0 1.4rem 0; }
@media (max-width: 900px) { .metric-grid { grid-template-columns: repeat(2, 1fr); } }
.metric {
    padding: 1rem 1.1rem; border-radius: 16px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
}
.metric .v { font-size: 1.7rem; font-weight: 800; color: #fff; }
.metric .l { font-size: .75rem; color: #9ca3af; text-transform: uppercase; letter-spacing: .06em; }

/* Report card */
.report-card {
    padding: 1.6rem 1.8rem; border-radius: 20px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.09);
}
.feedback-card {
    padding: 1.4rem 1.6rem; border-radius: 20px;
    background: linear-gradient(135deg, rgba(245,158,11,0.10), rgba(236,72,153,0.07));
    border: 1px solid rgba(251,191,36,0.3);
}

/* Inputs */
.stTextInput input {
    background: rgba(255,255,255,0.05) !important; color: #f9fafb !important;
    border: 1px solid rgba(255,255,255,0.14) !important; border-radius: 14px !important;
    padding: 0.95rem 1.1rem !important; font-size: 1.05rem !important;
}
.stTextInput input:focus { border-color: #818cf8 !important; box-shadow: 0 0 0 3px rgba(129,140,248,0.25) !important; }

.stButton > button, .stDownloadButton > button {
    border-radius: 14px; font-weight: 600; border: 1px solid rgba(255,255,255,0.14);
    background: rgba(255,255,255,0.05); color: #e5e7eb; transition: all .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: #818cf8; color: #fff; transform: translateY(-1px);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899); border: none; color: #fff;
    box-shadow: 0 10px 30px -10px rgba(168,85,247,0.7);
}
.stButton > button[kind="primary"]:hover { filter: brightness(1.1); transform: translateY(-2px); }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: .4rem; }
.stTabs [data-baseweb="tab"] {
    border-radius: 12px 12px 0 0; padding: .6rem 1.1rem; background: rgba(255,255,255,0.03);
}
.stTabs [aria-selected="true"] { background: rgba(99,102,241,0.18) !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(10,12,22,0.92); border-right: 1px solid rgba(255,255,255,0.07);
}
.side-title { font-weight: 700; font-size: .8rem; letter-spacing: .08em; text-transform: uppercase; color: #9ca3af; margin: 1rem 0 .4rem 0; }
.footer-note { text-align: center; color: #6b7280; font-size: .8rem; margin-top: 3rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
STEPS = [
    {"icon": "🔎", "name": "Search Agent", "desc": "Finds recent, reliable sources on the web"},
    {"icon": "📖", "name": "Reader Agent", "desc": "Scrapes the best URLs for deep content"},
    {"icon": "✍️", "name": "Writer Chain", "desc": "Drafts a structured research report"},
    {"icon": "🧐", "name": "Critic Chain", "desc": "Reviews the report and gives feedback"},
]

EXAMPLE_TOPICS = [
    "Latest advancements in Retrieval-Augmented Generation (RAG)",
    "Impact of AI agents on software engineering jobs",
    "Quantum computing breakthroughs in 2026",
    "State of open-source LLMs vs proprietary models",
]


def to_text(content) -> str:
    """Normalise LangChain message content (str or list of blocks) to plain text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                parts.append(block.get("text", "") or "")
            else:
                parts.append(getattr(block, "text", "") or str(block))
        return "\n".join(p for p in parts if p)
    # AIMessage or similar object
    if hasattr(content, "content"):
        return to_text(content.content)
    return str(content)


def render_stepper(statuses, timings):
    labels = {"pending": "Waiting", "running": "Working...", "done": "Completed", "error": "Failed"}
    cards = []
    for i, step in enumerate(STEPS):
        s = statuses[i]
        t = f" &middot; {timings[i]:.1f}s" if timings[i] is not None and s in ("done", "error") else ""
        cards.append(
            f'<div class="step {s}">'
            f'<div class="icon">{step["icon"]}</div>'
            f'<div class="name">{i + 1}. {step["name"]}</div>'
            f'<div class="desc">{step["desc"]}</div>'
            f'<div class="status">{labels[s]}{t}</div>'
            f"</div>"
        )
    return '<div class="stepper">' + "".join(cards) + "</div>"


def count_sources(text: str) -> int:
    return len(set(re.findall(r"https?://[^\s)\]>\"']+", text or "")))


def build_markdown(result: dict) -> str:
    return (
        f"# Research Report: {result['topic']}\n\n"
        f"_Generated on {result['timestamp']}_\n\n"
        f"{result['report']}\n\n---\n\n"
        f"## Critic Feedback\n\n{result['feedback']}\n"
    )


def run_pipeline(topic: str, stepper_slot) -> dict:
    """Same 4-step logic as pipeline.py, with live progress updates for the UI."""
    statuses = ["pending"] * 4
    timings = [None] * 4
    state = {}

    def update(i, status, started=None):
        statuses[i] = status
        if started is not None:
            timings[i] = time.time() - started
        stepper_slot.markdown(render_stepper(statuses, timings), unsafe_allow_html=True)

    update(0, "pending")
    current = 0
    start = time.time()
    try:
        # Step 1: search agent
        current = 0
        t0 = time.time()
        update(0, "running")
        search_agent = build_search_agent()
        search_results = search_agent.invoke(
            {"messages": [("user", f"find recent, reliable and detailed information about: {topic}")]}
        )
        state["search_results"] = to_text(search_results["messages"][-1].content)
        update(0, "done", t0)

        # Step 2: reader agent
        current = 1
        t0 = time.time()
        update(1, "running")
        reader_agent = build_reader_agent()
        reader_results = reader_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"based on the following search results about {topic}\n\n"
                        f"pick the most relevant urls and scrape it for deeper content using the available scrape_url tool. \n\n"
                        f"search results : \n {state['search_results'][-800:]}",
                    )
                ]
            }
        )
        state["scraped_content"] = to_text(reader_results["messages"][-1].content)
        update(1, "done", t0)

        # Step 3: writer chain
        current = 2
        t0 = time.time()
        update(2, "running")
        research_combined = (
            f"SEARCH RESULTS: \n {state['search_results']} \n\n"
            f"DETAILED SCRAPED RESULTS: \n {state['scraped_content']}"
        )
        state["report"] = to_text(writer_chain.invoke({"topic": topic, "research": research_combined}))
        update(2, "done", t0)

        # Step 4: critic chain
        current = 3
        t0 = time.time()
        update(3, "running")
        state["feedback"] = to_text(critic_chain.invoke({"report": state["report"]}))
        update(3, "done", t0)

    except Exception:
        update(current, "error", t0)
        raise

    state["topic"] = topic
    state["elapsed"] = time.time() - start
    state["timestamp"] = datetime.now().strftime("%d %b %Y, %H:%M")
    return state


def set_topic(value: str):
    st.session_state["topic_input"] = value


def load_history(idx: int):
    st.session_state["current"] = st.session_state["history"][idx]
    st.session_state["topic_input"] = st.session_state["history"][idx]["topic"]


# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------
st.session_state.setdefault("history", [])
st.session_state.setdefault("current", None)
st.session_state.setdefault("topic_input", "")

# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🧠 Research Agents")
    st.caption("A LangChain multi-agent research system")

    st.markdown('<div class="side-title">Try an example</div>', unsafe_allow_html=True)
    for i, ex in enumerate(EXAMPLE_TOPICS):
        st.button(ex, key=f"ex_{i}", use_container_width=True, on_click=set_topic, args=(ex,))

    st.markdown('<div class="side-title">History</div>', unsafe_allow_html=True)
    if st.session_state["history"]:
        for idx in range(len(st.session_state["history"]) - 1, -1, -1):
            item = st.session_state["history"][idx]
            label = item["topic"] if len(item["topic"]) <= 38 else item["topic"][:35] + "..."
            st.button(f"🕘 {label}", key=f"hist_{idx}", use_container_width=True, on_click=load_history, args=(idx,))
        if st.button("🗑️ Clear history", use_container_width=True):
            st.session_state["history"] = []
            st.session_state["current"] = None
            st.rerun()
    else:
        st.caption("Your past research runs will appear here.")

    st.markdown('<div class="side-title">How it works</div>', unsafe_allow_html=True)
    st.markdown(
        "1. **Search** finds sources\n"
        "2. **Reader** scrapes the best ones\n"
        "3. **Writer** drafts the report\n"
        "4. **Critic** reviews it"
    )

# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
st.markdown(
    """
<div class="hero">
    <span class="hero-badge">Multi-Agent AI &middot; LangChain</span>
    <h1>Research anything. Automatically.</h1>
    <p>Four specialised AI agents search the web, read the best sources, write a structured report
    and critiques it, all from a single topic.</p>
    <div class="agent-row">
        <span class="agent-pill">🔎 Search Agent</span>
        <span class="agent-pill">📖 Reader Agent</span>
        <span class="agent-pill">✍️ Writer Chain</span>
        <span class="agent-pill">🧐 Critic Chain</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

if IMPORT_ERROR is not None:
    st.error(
        "Could not import the backend. Check the error below and install the project "
        "dependencies into the same Python environment used to launch Streamlit."
    )
    st.caption(f"Python interpreter running this app: `{sys.executable}`")
    st.caption(
        "From the project folder, run "
        "`python -m pip install -r requirements.txt`, then "
        "`python -m streamlit run app.py` using that same Python."
    )
    st.code(repr(IMPORT_ERROR))
    st.stop()

# ----------------------------------------------------------------------------
# Input
# ----------------------------------------------------------------------------
col_in, col_btn = st.columns([5, 1.2], vertical_alignment="bottom")
with col_in:
    topic = st.text_input(
        "Research topic",
        key="topic_input",
        placeholder="e.g. Latest advancements in Retrieval-Augmented Generation (RAG)",
        label_visibility="collapsed",
    )
with col_btn:
    run_clicked = st.button("🚀 Start Research", type="primary", use_container_width=True)

stepper_slot = st.empty()

# ----------------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------------
if run_clicked:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        try:
            result = run_pipeline(topic.strip(), stepper_slot)
            st.session_state["current"] = result
            st.session_state["history"].append(result)
            st.toast("Research complete!", icon="✅")
            st.balloons()
        except Exception as e:
            st.error(f"The pipeline failed: {e}")
            with st.expander("Error details"):
                st.exception(e)
elif st.session_state["current"] is None:
    stepper_slot.markdown(render_stepper(["pending"] * 4, [None] * 4), unsafe_allow_html=True)
else:
    stepper_slot.markdown(render_stepper(["done"] * 4, [None] * 4), unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------------
res = st.session_state["current"]
if res:
    words = len(res["report"].split())

    st.markdown(
        f"""
<div class="metric-grid">
    <div class="metric"><div class="v">{res['elapsed']:.0f}s</div><div class="l">Total time</div></div>
    <div class="metric"><div class="v">{words:,}</div><div class="l">Report words</div></div>
    <div class="metric"><div class="v">4</div><div class="l">Agents used</div></div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(f"#### Results for: *{res['topic']}*")
    tab_report, tab_feedback, tab_search, tab_scrape = st.tabs(
        ["📄 Final Report", "🧐 Critic Feedback", "🔎 Search Results", "📖 Scraped Content"]
    )

    with tab_report:
        with st.container(border=True):
            st.markdown(res["report"])

    with tab_feedback:
        with st.container(border=True):
            st.markdown(res["feedback"])

    with tab_search:
        with st.container(border=True):
            st.markdown(res["search_results"])

    with tab_scrape:
        with st.container(border=True):
            st.markdown(res["scraped_content"])

    st.markdown("&nbsp;")
    d1, d2, _ = st.columns([1.2, 1.2, 3])
    safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", res["topic"]).strip("_")[:50] or "research"
    with d1:
        st.download_button(
            "⬇️ Report (.md)",
            data=res["report"],
            file_name=f"{safe_name}_report.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "⬇️ Full bundle (.md)",
            data=build_markdown(res),
            file_name=f"{safe_name}_full.md",
            mime="text/markdown",
            use_container_width=True,
        )

st.markdown(
    '<div class="footer-note">Built with LangChain &amp; Streamlit</div>',
    unsafe_allow_html=True,
)