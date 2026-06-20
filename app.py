import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*allowed_objects.*")

import streamlit as st
import time

st.set_page_config(
    page_title="ResearchMind - Multi-Agent System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS (single assignment, no triple-quoted markdown blocks) ─────────────────
CSS = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');"
    "html,body,[class*='css']{font-family:'DM Sans',sans-serif;color:#e8e4dc;}"
    ".stApp{background:#0a0a0f;background-image:radial-gradient(ellipse 80% 50% at 20% -10%,rgba(255,140,50,.12) 0%,transparent 60%),radial-gradient(ellipse 60% 40% at 80% 110%,rgba(255,80,30,.08) 0%,transparent 55%);}"
    "#MainMenu,footer,header{visibility:hidden;}"
    ".block-container{padding:2rem 3rem 4rem;max-width:1200px;}"
    ".hero{text-align:center;padding:3.5rem 0 2.5rem;}"
    ".hero-eyebrow{font-family:'DM Mono',monospace;font-size:.7rem;font-weight:500;letter-spacing:.25em;text-transform:uppercase;color:#ff8c32;margin-bottom:1rem;}"
    ".hero h1{font-family:'Syne',sans-serif;font-size:clamp(2.8rem,6vw,5rem);font-weight:800;line-height:1.0;letter-spacing:-.03em;color:#f0ebe0;margin:0 0 1rem;}"
    ".hero h1 span{color:#ff8c32;}"
    ".hero-sub{font-size:1.05rem;font-weight:300;color:#a09890;max-width:520px;margin:0 auto;line-height:1.65;}"
    ".divider{height:1px;background:linear-gradient(90deg,transparent,rgba(255,140,50,.3),transparent);margin:2rem 0;}"
    ".input-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,140,50,.15);border-radius:16px;padding:2rem 2.5rem;margin-bottom:2rem;backdrop-filter:blur(8px);}"
    ".stTextInput>div>div>input{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,140,50,.25)!important;border-radius:10px!important;color:#f0ebe0!important;font-family:'DM Sans',sans-serif!important;font-size:1rem!important;padding:.75rem 1rem!important;}"
    ".stTextInput>div>div>input:focus{border-color:#ff8c32!important;box-shadow:0 0 0 3px rgba(255,140,50,.12)!important;}"
    ".stTextInput>label{font-family:'DM Mono',monospace!important;font-size:.72rem!important;letter-spacing:.15em!important;text-transform:uppercase!important;color:#ff8c32!important;font-weight:500!important;}"
    ".stButton>button{background:linear-gradient(135deg,#ff8c32 0%,#ff5a1a 100%)!important;color:#0a0a0f!important;font-family:'Syne',sans-serif!important;font-weight:700!important;font-size:.95rem!important;letter-spacing:.04em!important;border:none!important;border-radius:10px!important;padding:.7rem 2.2rem!important;width:100%;box-shadow:0 4px 20px rgba(255,140,50,.3)!important;}"
    ".stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 28px rgba(255,140,50,.4)!important;}"
    ".step-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:1.5rem 1.8rem;margin-bottom:1.2rem;position:relative;overflow:hidden;transition:border-color .3s;}"
    ".step-card.active{border-color:rgba(255,140,50,.4);background:rgba(255,140,50,.04);}"
    ".step-card.done{border-color:rgba(80,200,120,.3);background:rgba(80,200,120,.03);}"
    ".step-card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;border-radius:14px 0 0 14px;background:rgba(255,255,255,.05);transition:background .3s;}"
    ".step-card.active::before{background:#ff8c32;}"
    ".step-card.done::before{background:#50c878;}"
    ".step-header{display:flex;align-items:center;gap:.8rem;margin-bottom:.3rem;}"
    ".step-num{font-family:'DM Mono',monospace;font-size:.68rem;font-weight:500;letter-spacing:.15em;color:#ff8c32;opacity:.7;}"
    ".step-title{font-family:'Syne',sans-serif;font-size:.95rem;font-weight:700;color:#f0ebe0;}"
    ".step-status{margin-left:auto;font-family:'DM Mono',monospace;font-size:.68rem;letter-spacing:.1em;}"
    ".status-waiting{color:#555;}.status-running{color:#ff8c32;}.status-done{color:#50c878;}"
    ".result-panel{background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:1.8rem 2rem;margin-top:1rem;margin-bottom:1.5rem;}"
    ".result-panel-title{font-family:'DM Mono',monospace;font-size:.7rem;font-weight:500;letter-spacing:.2em;text-transform:uppercase;color:#ff8c32;margin-bottom:1rem;padding-bottom:.7rem;border-bottom:1px solid rgba(255,140,50,.15);}"
    ".result-content{font-size:.92rem;line-height:1.8;color:#cdc8bf;white-space:pre-wrap;font-family:'DM Sans',sans-serif;}"
    ".report-panel{background:rgba(255,255,255,.025);border:1px solid rgba(255,140,50,.2);border-radius:16px;padding:2rem 2.5rem;margin-top:1rem;}"
    ".feedback-panel{background:rgba(255,255,255,.025);border:1px solid rgba(80,200,120,.2);border-radius:16px;padding:2rem 2.5rem;margin-top:1rem;}"
    ".panel-label{font-family:'DM Mono',monospace;font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;margin-bottom:1.2rem;padding-bottom:.7rem;}"
    ".panel-label.orange{color:#ff8c32;border-bottom:1px solid rgba(255,140,50,.15);}"
    ".panel-label.green{color:#50c878;border-bottom:1px solid rgba(80,200,120,.15);}"
    ".section-heading{font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:700;color:#f0ebe0;margin:2rem 0 1rem;}"
    ".notice{font-family:'DM Mono',monospace;font-size:.72rem;color:#605850;text-align:center;margin-top:3rem;letter-spacing:.08em;}"
    "::-webkit-scrollbar{width:4px;}"
    "::-webkit-scrollbar-track{background:#0a0a0f;}"
    "::-webkit-scrollbar-thumb{background:#3a2a1a;border-radius:4px;}"
    ".stProgress>div>div>div>div{background:linear-gradient(90deg,#ff8c32,#ff5a1a)!important;border-radius:100px!important;}"
    ".stProgress>div>div{background:#1e1a14!important;border-radius:100px!important;}"
    "</style>"
)
st.markdown(CSS, unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def step_card(num, title, state, desc=""):
    status_map = {
        "waiting": ("WAITING",   "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",    "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    desc_html = (
        "<div style='font-size:.82rem;color:#706860;margin-top:.3rem;'>" + desc + "</div>"
        if desc else ""
    )
    html = (
        '<div class="step-card ' + card_cls + '">'
        '<div class="step-header">'
        '<span class="step-num">' + num + '</span>'
        '<span class="step-title">' + title + '</span>'
        '<span class="step-status ' + cls + '">' + label + '</span>'
        '</div>'
        + desc_html +
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def get_step_state(step, results, running):
    steps = ["search", "reader", "writer", "critic"]
    if step in results:
        return "done"
    if running:
        for k in steps:
            if k not in results:
                return "running" if k == step else "waiting"
    return "waiting"


# ── Session state ─────────────────────────────────────────────────────────────
for k, default in [("results", {}), ("running", False), ("done", False)]:
    if k not in st.session_state:
        st.session_state[k] = default


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero">'
    '<div class="hero-eyebrow">Multi-Agent AI System</div>'
    '<h1>Research<span>Mind</span></h1>'
    '<p class="hero-sub">Four specialized AI agents collaborate — searching, scraping, writing,'
    ' and critiquing — to deliver a polished research report on any topic.</p>'
    '</div>'
    '<div class="divider"></div>',
    unsafe_allow_html=True,
)


# ── Layout ────────────────────────────────────────────────────────────────────
col_input, _, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='display:flex;gap:.5rem;flex-wrap:wrap;align-items:center;margin-bottom:1.5rem;'>"
        "<span style='font-family:DM Mono,monospace;font-size:.68rem;color:#605850;letter-spacing:.1em;'>TRY →</span>"
        "<span style='background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:6px;padding:.25rem .7rem;font-size:.75rem;color:#a09890;'>LLM agents 2025</span>"
        "<span style='background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:6px;padding:.25rem .7rem;font-size:.75rem;color:#a09890;'>CRISPR gene editing</span>"
        "<span style='background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:6px;padding:.25rem .7rem;font-size:.75rem;color:#a09890;'>Fusion energy progress</span>"
        "</div>",
        unsafe_allow_html=True,
    )

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)
    r = st.session_state.results
    running = st.session_state.running
    step_card("01", "Search Agent",  get_step_state("search", r, running), "Gathers recent web information")
    step_card("02", "Reader Agent",  get_step_state("reader", r, running), "Scrapes & extracts deep content")
    step_card("03", "Writer Chain",  get_step_state("writer", r, running), "Drafts the full research report")
    step_card("04", "Critic Chain",  get_step_state("critic", r, running), "Reviews & scores the report")


# ── Trigger rerun to start pipeline ──────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()


# ── Execute pipeline (runs after rerun sets running=True) ────────────────────
if st.session_state.running and not st.session_state.done:
    try:
        from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain
    except ImportError as e:
        st.error(
            "Could not import agents.py: " + str(e) +
            "\n\nMake sure agents.py, tools.py are in the same folder as app.py."
        )
        st.session_state.running = False
        st.stop()

    topic_val = st.session_state.topic_input
    results = {}

    progress = st.progress(0, text="Initialising pipeline...")

    # Step 1 — Search
    with st.spinner("🔍  Search Agent is working..."):
        try:
            agent = build_search_agent()
            sr = agent.invoke({
                "messages": [{"role": "user", "content": "Find recent, reliable and detailed information about: " + topic_val}]
            })
            results["search"] = sr["messages"][-1].content
            st.session_state.results = dict(results)
            progress.progress(25, text="📄 Reader Agent is scraping content...")
        except Exception as e:
            st.error("Search Agent failed: " + str(e))
            st.session_state.running = False
            st.stop()

    # Step 2 — Reader
    with st.spinner("📄  Reader Agent is scraping top resources..."):
        try:
            agent = build_reader_agent()
            rr = agent.invoke({
                "messages": [{"role": "user", "content": (
                    "Based on the following search results about '" + topic_val + "', "
                    "pick the most relevant URL and scrape it for deeper content.\n\n"
                    "Search Results:\n" + results["search"][:800]
                )}]
            })
            results["reader"] = rr["messages"][-1].content
            st.session_state.results = dict(results)
            progress.progress(50, text="✍️ Writer is drafting the report...")
        except Exception as e:
            st.error("Reader Agent failed: " + str(e))
            st.session_state.running = False
            st.stop()

    # Step 3 — Writer
    with st.spinner("✍️  Writer is drafting the report..."):
        try:
            research_combined = (
                "SEARCH RESULTS:\n" + results["search"] +
                "\n\nDETAILED SCRAPED CONTENT:\n" + results["reader"]
            )
            results["writer"] = writer_chain.invoke({
                "topic": topic_val,
                "research": research_combined,
            })
            st.session_state.results = dict(results)
            progress.progress(75, text="🎯 Critic is reviewing the report...")
        except Exception as e:
            st.error("Writer failed: " + str(e))
            st.session_state.running = False
            st.stop()

    # Step 4 — Critic
    with st.spinner("🎯  Critic is reviewing the report..."):
        try:
            results["critic"] = critic_chain.invoke({"report": results["writer"]})
            st.session_state.results = dict(results)
            progress.progress(100, text="Pipeline complete!")
        except Exception as e:
            st.error("Critic failed: " + str(e))
            st.session_state.running = False
            st.stop()

    st.session_state.running = False
    st.session_state.done = True
    st.balloons()
    st.rerun()


# ── Results ───────────────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            safe = r["search"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(
                '<div class="result-panel">'
                '<div class="result-panel-title">Search Agent Output</div>'
                '<div class="result-content">' + safe + '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            safe = r["reader"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(
                '<div class="result-panel">'
                '<div class="result-panel-title">Reader Agent Output</div>'
                '<div class="result-content">' + safe + '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

    if "writer" in r:
        st.markdown(
            '<div class="report-panel">'
            '<div class="panel-label orange">Final Research Report</div>',
            unsafe_allow_html=True,
        )
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        topic_slug = st.session_state.get("topic_input", "report").replace(" ", "_")[:30]
        st.download_button(
            label="Download Report (.md)",
            data=r["writer"],
            file_name="research_" + topic_slug + "_" + str(int(time.time())) + ".md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown(
            '<div class="feedback-panel">'
            '<div class="panel-label green">Critic Feedback</div>',
            unsafe_allow_html=True,
        )
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="notice">ResearchMind &middot; Powered by LangChain multi-agent pipeline &middot; Built with Streamlit</div>',
    unsafe_allow_html=True,
)