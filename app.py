
import html
import time
import streamlit as st

from pipeline import run_research_pipeline


st.set_page_config(
    page_title="ResearchMind - Multi-Agent System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ── CSS ──────────────────────────────────────────────────────────────

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}

.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,.12), transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,80,30,.08), transparent 55%);
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    padding: 2rem 3rem 4rem;
    max-width: 1200px;
}

.hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
}

.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: .7rem;
    letter-spacing: .25em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
}

.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 800;
    line-height: 1;
    color: #f0ebe0;
    margin: 0 0 1rem;
}

.hero h1 span {
    color: #ff8c32;
}

.hero-sub {
    font-size: 1.05rem;
    color: #a09890;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.65;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,140,50,.3), transparent);
    margin: 2rem 0;
}

.input-card {
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,140,50,.15);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
}

.stTextInput input {
    background: rgba(255,255,255,.05) !important;
    border: 1px solid rgba(255,140,50,.25) !important;
    border-radius: 10px !important;
    color: #f0ebe0 !important;
}

.stTextInput label {
    color: #ff8c32 !important;
    font-family: 'DM Mono', monospace !important;
}

.stButton button {
    background: linear-gradient(135deg, #ff8c32, #ff5a1a) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    width: 100%;
}

.step-card {
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
}

.step-card.active {
    border-color: rgba(255,140,50,.5);
    background: rgba(255,140,50,.04);
}

.step-card.done {
    border-color: rgba(80,200,120,.3);
    background: rgba(80,200,120,.03);
}

.step-card.failed {
    border-color: rgba(255,80,80,.5);
}

.step-header {
    display: flex;
    align-items: center;
    gap: .8rem;
}

.step-num {
    font-family: 'DM Mono', monospace;
    color: #ff8c32;
    font-size: .7rem;
}

.step-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    color: #f0ebe0;
}

.step-status {
    margin-left: auto;
    font-family: 'DM Mono', monospace;
    font-size: .68rem;
}

.status-waiting { color: #777; }
.status-running { color: #ff8c32; }
.status-done { color: #50c878; }
.status-failed { color: #ff6666; }

.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #f0ebe0;
    margin: 2rem 0 1rem;
}

.report-panel, .feedback-panel, .result-panel {
    background: rgba(255,255,255,.025);
    border: 1px solid rgba(255,140,50,.2);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin: 1rem 0;
}

.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: .7rem;
    letter-spacing: .2em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    padding-bottom: .7rem;
    border-bottom: 1px solid rgba(255,140,50,.15);
    color: #ff8c32;
}

.feedback-panel {
    border-color: rgba(80,200,120,.2);
}

.feedback-panel .panel-label {
    color: #50c878;
    border-bottom-color: rgba(80,200,120,.15);
}

.notice {
    font-family: 'DM Mono', monospace;
    font-size: .72rem;
    color: #605850;
    text-align: center;
    margin-top: 3rem;
}

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #ff8c32, #ff5a1a) !important;
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────

STEPS = [
    ("search", "01", "Search Agent", "Gathers recent web information"),
    ("reader", "02", "Reader Agent", "Scrapes and extracts detailed content"),
    ("writer", "03", "Writer Chain", "Creates the research report"),
    ("critic", "04", "Critic Chain", "Reviews and scores the report"),
]


def render_step(container, step, number, title, description, status):
    labels = {
        "waiting": ("WAITING", "status-waiting", ""),
        "running": ("● RUNNING", "status-running", "active"),
        "done": ("✓ DONE", "status-done", "done"),
        "failed": ("✕ FAILED", "status-failed", "failed"),
    }

    label, status_class, card_class = labels[status]

    container.markdown(
        f"""
        <div class="step-card {card_class}">
            <div class="step-header">
                <span class="step-num">{number}</span>
                <span class="step-title">{title}</span>
                <span class="step-status {status_class}">{label}</span>
            </div>
            <div style="font-size:.82rem;color:#888;margin-top:.4rem;">
                {description}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pipeline(statuses, containers):
    for step, number, title, description in STEPS:
        render_step(
            containers[step],
            step,
            number,
            title,
            description,
            statuses.get(step, "waiting"),
        )


# ── Session State ─────────────────────────────────────────────────────

if "results" not in st.session_state:
    st.session_state.results = {}

if "statuses" not in st.session_state:
    st.session_state.statuses = {
        step: "waiting" for step, *_ in STEPS
    }

if "error" not in st.session_state:
    st.session_state.error = None


# ── Hero ──────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">Multi-Agent AI System</div>
        <h1>Research<span>Mind</span></h1>
        <p class="hero-sub">
            Four specialized AI agents collaborate — searching, scraping,
            writing, and critiquing — to deliver a polished research report.
        </p>
    </div>
    <div class="divider"></div>
    """,
    unsafe_allow_html=True,
)


# ── Main Layout ───────────────────────────────────────────────────────

col_input, _, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)

    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs",
        key="topic_input",
    )

    run_btn = st.button(
        "⚡ Run Research Pipeline",
        use_container_width=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1.5rem;">
            <span style="color:#605850;font-size:.7rem;">TRY →</span>
            <span style="color:#a09890;font-size:.75rem;">LLM agents</span>
            <span style="color:#a09890;font-size:.75rem;">CRISPR gene editing</span>
            <span style="color:#a09890;font-size:.75rem;">Fusion energy progress</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

    step_containers = {}
    for step, *_ in STEPS:
        step_containers[step] = st.empty()

    render_pipeline(
        st.session_state.statuses,
        step_containers,
    )


# ── Run Pipeline ──────────────────────────────────────────────────────

if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")

    else:
        st.session_state.results = {}
        st.session_state.error = None
        st.session_state.statuses = {
            step: "waiting" for step, *_ in STEPS
        }

        render_pipeline(
            st.session_state.statuses,
            step_containers,
        )

        progress = st.progress(0, text="Starting ResearchMind...")
        stage_progress = {
            "search": 10,
            "reader": 35,
            "writer": 65,
            "critic": 85,
        }

        def on_stage_update(stage, status, result=None):
            st.session_state.statuses[stage] = status

            if status == "done" and result is not None:
                st.session_state.results[stage] = result

            if status == "failed":
                st.session_state.error = result

            render_pipeline(
                st.session_state.statuses,
                step_containers,
            )

            if status == "running":
                progress.progress(
                    stage_progress[stage],
                    text=f"{stage.title()} is running...",
                )

            elif status == "done":
                progress.progress(
                    stage_progress[stage] + 15,
                    text=f"{stage.title()} completed",
                )

        try:
            with st.spinner("ResearchMind agents are working..."):
                results = run_research_pipeline(
                    topic.strip(),
                    on_stage_update=on_stage_update,
                )

            st.session_state.results = results
            progress.progress(100, text="Research pipeline completed!")
            st.success("Research report generated successfully!")
            st.balloons()

        except Exception as exc:
            st.session_state.error = str(exc)
            st.error(f"Pipeline stopped: {exc}")

        render_pipeline(
            st.session_state.statuses,
            step_containers,
        )


# ── Error Display ─────────────────────────────────────────────────────

if st.session_state.error:
    st.error(st.session_state.error)


# ── Results ───────────────────────────────────────────────────────────

results = st.session_state.results

if results:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Research Results</div>', unsafe_allow_html=True)

    if results.get("search"):
        with st.expander("🔍 Search Agent Results"):
            st.text(results["search"])

    if results.get("reader"):
        with st.expander("📄 Reader Agent Results"):
            st.text(results["reader"])

    if results.get("writer"):
        st.markdown(
            '<div class="report-panel">'
            '<div class="panel-label">Final Research Report</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(results["writer"])

        topic_slug = (
            results.get("topic", "research")
            .replace(" ", "_")[:40]
        )

        st.download_button(
            label="Download Report (.md)",
            data=results["writer"],
            file_name=f"research_{topic_slug}_{int(time.time())}.md",
            mime="text/markdown",
        )

    if results.get("critic"):
        st.markdown(
            '<div class="feedback-panel">'
            '<div class="panel-label">Critic Feedback</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(results["critic"])


# ── Footer ────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="notice">
        ResearchMind · Powered by LangChain Multi-Agent Pipeline · Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
