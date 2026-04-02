"""
Gap Sense — Streamlit Frontend
Calls FastAPI backend for skill gap analysis and skill trend prediction.
"""

import os

import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv

# ─── Load .env ────────────────────────────────────────────────────────────────
load_dotenv()
API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

TREND_ROLE_BLOCKLISTS = {
    "frontend": {
        "python", "java", "php", "c#", "c++", "go", "r", "numpy", "pandas",
        "scikit-learn", "tensorflow", "pytorch", "django", "flask", "laravel",
        "docker", "kubernetes", "mysql", "postgresql", "mongodb", "redis", "oracle",
    },
    "backend": {
        "html", "css", "jquery", "sass", "tailwind css", "bootstrap",
        "figma", "photoshop", "illustrator", "numpy", "pandas",
        "scikit-learn", "tensorflow", "pytorch", "tableau", "power bi", "excel", "r",
    },
    "data analyst": {
        "html", "css", "javascript", "typescript", "react", "angular", "vue",
        "node.js", "webpack", "vite", "next", "express", "nestjs",
    },
}

DISPLAY_SKILL_ALIASES = {
    "power_bi": "Power BI",
    "google_analytics": "Google Analytics",
    "data_visualization": "Data Visualization",
    "data_analysis": "Data Analysis",
    "machine_learning": "Machine Learning",
    "business_intelligence": "Business Intelligence",
    "google_cloud": "Google Cloud",
    "google_sheets": "Google Sheets",
    "sql_server": "SQL Server",
    "django_rest_framework": "Django REST Framework",
    "node.js": "Node.js",
    "next.js": "Next.js",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "react": "React",
    "vue": "Vue",
    "jquery": "jQuery",
    "aws": "AWS",
    "excel": "Excel",
    "sql": "SQL",
    "r": "R",
    "sas": "SAS",
    "api": "API",
    "jwt": "JWT",
    "ci/cd": "CI/CD",
    ".net": ".NET",
}

FRONTEND_SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "golang": "go",
    "go lang": "go",
    "nodejs": "node.js",
    "node js": "node.js",
    "reactjs": "react",
    "react js": "react",
    "vuejs": "vue",
    "vue js": "vue",
    "nextjs": "next.js",
    "next js": "next.js",
    "power bi": "power_bi",
    "powerbi": "power_bi",
    "google analytics": "google_analytics",
    "data visualization": "data_visualization",
    "data visualisation": "data_visualization",
    "data viz": "data_visualization",
    "data analysis": "data_analysis",
    "data analytics": "data_analysis",
}


def format_skill_label(skill: str) -> str:
    """Convert canonical skill names into user-facing labels."""
    normalized = str(skill).strip().lower()
    if normalized in DISPLAY_SKILL_ALIASES:
        return DISPLAY_SKILL_ALIASES[normalized]
    return normalized.replace("_", " ").title()


def normalize_skill_input(skill: str) -> str:
    """Apply lightweight client-side normalization for common aliases/slang."""
    normalized = str(skill).strip().lower()
    normalized = normalized.replace("-", " ")
    normalized = normalized.replace("_", " ")
    normalized = " ".join(normalized.split())
    normalized = FRONTEND_SKILL_ALIASES.get(normalized, normalized)
    return normalized

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GapSense - Career Skill Gap Analysis",
    page_icon="🎯",
    layout="wide",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  .stApp {
    background: #0d0d0d;
    color: #e8e8e0;
  }

  /* ── Hero header ── */
  .hero {
    text-align: center;
    padding: 3rem 0 2rem;
  }
  .hero h1 {
    font-family: 'Space Mono', monospace;
    font-size: 2.8rem;
    letter-spacing: -1px;
    color: #f0e040;
    margin-bottom: 0.3rem;
  }
  .hero p {
    color: #888;
    font-size: 1.05rem;
  }

  /* ── Cards ── */
  .card {
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
  }
  .card-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 2px;
    color: #f0e040;
    text-transform: uppercase;
    margin-bottom: 1rem;
  }

  /* ── Skill tag ── */
  .skill-tag {
    display: inline-block;
    background: #1e1e1e;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 4px 12px;
    margin: 3px;
    font-size: 0.85rem;
    color: #e8e8e0;
    transition: all 0.2s ease;
  }
  .skill-tag:hover {
    background: #2a2a2a;
    border-color: #f0e040;
    color: #f0e040;
  }

  /* ── Score badge ── */
  .score-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    font-family: 'Space Mono', monospace;
  }
  .score-high   { background: #1a3a1a; color: #4caf50; border: 1px solid #4caf50; }
  .score-medium { background: #3a2e00; color: #f0e040; border: 1px solid #f0e040; }
  .score-low    { background: #3a1a1a; color: #ef5350; border: 1px solid #ef5350; }

  /* ── Risk banner ── */
  .risk-banner {
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
    font-family: 'Space Mono', monospace;
  }
  .risk-low    { background: #0f2010; border-left: 4px solid #4caf50; }
  .risk-medium { background: #201800; border-left: 4px solid #f0e040; }
  .risk-high   { background: #200a0a; border-left: 4px solid #ef5350; }

  /* ── Recommendation row with progress bar ── */
  .rec-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.7rem 0;
    border-bottom: 1px solid #1e1e1e;
  }
  .rec-row:last-child { border-bottom: none; }
  .rec-skill-name {
    font-size: 0.9rem;
    color: #e8e8e0;
    min-width: 140px;
    flex-shrink: 0;
  }
  .rec-bar-track {
    flex-grow: 1;
    height: 8px;
    background: #1e1e1e;
    border-radius: 4px;
    overflow: hidden;
  }
  .rec-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.6s ease;
  }
  .rec-pct {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    font-weight: 600;
    min-width: 48px;
    text-align: right;
  }

  /* ── Progress bar override ── */
  .stProgress > div > div > div > div {
    background: linear-gradient(90deg, #f0e040, #ffe680) !important;
  }

  /* ── Buttons ── */
  .stButton > button {
    background: #f0e040;
    color: #0d0d0d;
    border: none;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 0.55rem 1.4rem;
    transition: all 0.2s;
  }
  .stButton > button:hover {
    background: #ffe000;
    transform: translateY(-1px);
  }

  /* ── Radio ── */
  .stRadio > label { color: #aaa !important; font-size: 0.85rem; }
  .stRadio [data-baseweb="radio"] label { color: #e8e8e0 !important; }

  /* ── Text input ── */
  .stTextInput > div > div > input {
    background: #161616 !important;
    border: 1px solid #2a2a2a !important;
    color: #e8e8e0 !important;
    border-radius: 8px;
  }

  /* ── Select box dark style ── */
  .stSelectbox [data-baseweb="select"] {
    background: #161616 !important;
  }

  /* ── Score interpretation label ── */
  .score-interp {
    font-size: 0.82rem;
    margin-top: 0.5rem;
    padding: 0.5rem 0.8rem;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
  }

  /* ── Divider ── */
  hr { border-color: #222; }

  /* ── Professional Footer Override ── */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}

  .custom-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: rgba(13, 13, 13, 0.9);
    backdrop-filter: blur(4px);
    border-top: 1px solid #1e1e1e;
    color: #666;
    text-align: center;
    padding: 0.6rem 0;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    z-index: 9999;
  }
  .custom-footer span.highlight {
    color: #f0e040;
    font-weight: 700;
  }
</style>
""", unsafe_allow_html=True)


# ─── Helper: Call API ─────────────────────────────────────────────────────────
def call_gap_sense_api(
    role: str,
    skills: list[str],
    top_k: int = 10,
    experience_level: str = "fresh_graduate",
    learning_background: str = "self_taught",
    target_timeline: str = "flexible",
) -> dict | None:
    """Call backend /api/gap-sense endpoint with user context."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/api/gap-sense",
            json={
                "role": role,
                "skills": skills,
                "top_k": top_k,
                "experience_level": experience_level,
                "learning_background": learning_background,
                "target_timeline": target_timeline,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling API: {e}")
        return None


def call_skill_trend_api(skills: list[str]) -> dict | None:
    """Call backend /api/skill-trend endpoint."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/api/skill-trend",
            json={"skills": skills},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling Trend API: {e}")
        return None


def filter_trends_for_role(trend_data: dict | None, role: str) -> dict | None:
    """Keep only trend items that are still relevant to the selected role."""
    if not trend_data or not trend_data.get("trends"):
        return trend_data

    blocked = TREND_ROLE_BLOCKLISTS.get(role, set())
    filtered = [
        trend for trend in trend_data["trends"]
        if trend.get("skill", "").lower() not in blocked
    ]
    return {
        **trend_data,
        "trends": filtered,
    }


# ─── Score Interpretation ─────────────────────────────────────────────────────
_SCORE_INTERPRETATION = [
    (25, "🌱", "Tahap Awal", "Normal untuk pemula — fokus pada skill fondasi terlebih dahulu.", "#0f2010"),
    (50, "🚀", "Berkembang", "Sudah cukup untuk mulai melamar posisi entry-level/junior.", "#201800"),
    (75, "⚡", "Kompetitif", "Skill Anda sudah kuat untuk posisi junior, mendekati mid-level.", "#1a2a3a"),
    (100, "🏆", "Expert-Ready", "Siap bersaing di level senior — tinggal poles pengalaman proyek.", "#1a3a1a"),
]


def _get_score_interpretation(score: int) -> tuple:
    """Return (icon, label, description, bg_color) for the given score."""
    for threshold, icon, label, desc, bg in _SCORE_INTERPRETATION:
        if score <= threshold:
            return icon, label, desc, bg
    return _SCORE_INTERPRETATION[-1][1:]


# ─── Session State Init ──────────────────────────────────────────────────────
if "skills_list" not in st.session_state:
    st.session_state.skills_list = []
if "page" not in st.session_state:
    st.session_state.page = "home"
if "results" not in st.session_state:
    st.session_state.results = None
if "trends" not in st.session_state:
    st.session_state.trends = None


# ═════════════════════════════════════════════════════════════════════════════
#  HOME PAGE
# ═════════════════════════════════════════════════════════════════════════════
def home_page() -> None:
    """Renders the home page view for role selection, skill input, and user context."""
    st.markdown("""
    <div class="hero">
      <h1>🎯 Gap Sense</h1>
      <p>Identify missing skills and bridge the gap to your target career role.</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 1], gap="large")

    # ── LEFT: All Form Inputs (Role, Profile, Skills) ─────────────────────────
    with col_left:
        # 1. Role Selection
        st.markdown('<div class="card-title">1. Select Target Profession</div>', unsafe_allow_html=True)
        role_map = {
            "Front End": "frontend",
            "Back End": "backend",
            "Data Analyst": "data analyst",
        }
        selected_label = st.radio(
            "Select your target profession",
            list(role_map.keys()),
            label_visibility="collapsed",
            horizontal=True,
        )
        selected_role = role_map[selected_label]

        st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)

        # 2. User Profile / Context
        st.markdown('<div class="card-title">2. Tell Us About You</div>', unsafe_allow_html=True)
        col_prof1, col_prof2 = st.columns(2)
        with col_prof1:
            experience_level = st.selectbox(
                "Tingkat Pengalaman",
                options=["Fresh Graduate (< 1 tahun)", "Junior (1-2 tahun)", "Mid-Level (3+ tahun)"],
                index=0,
                key="experience_select",
            )
        with col_prof2:
            learning_background = st.multiselect(
                "Latar Belakang Belajar",
                options=["Otodidak / Self-taught", "Lulusan Bootcamp", "Pendidikan Formal IT/CS"],
                default=["Otodidak / Self-taught"],
                key="background_select",
            )
        target_timeline = st.selectbox(
            "Target Waktu",
            options=["Aktif Mencari Kerja (3 bulan)", "Transisi Karier (1 tahun)", "Fleksibel / Eksplorasi"],
            index=0,
            key="timeline_select",
        )

        st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)

        # 3. Add Skills
        st.markdown('<div class="card-title">3. Add Your Current Skills</div>', unsafe_allow_html=True)
        col_skill_input, col_skill_btn = st.columns([3, 1])
        with col_skill_input:
            new_skill = st.text_input(
                "Add skill",
                placeholder="e.g. HTML, React, Python, SQL...",
                label_visibility="collapsed",
                key="skill_input",
            )
        with col_skill_btn:
            # A little CSS trick to align the button with the input
            st.markdown("<style>div.stButton > button:first-child { width: 100%; }</style>", unsafe_allow_html=True)
            if st.button("Add ➕"):
                skill_clean = normalize_skill_input(new_skill)
                if skill_clean and skill_clean not in st.session_state.skills_list:
                    st.session_state.skills_list.append(skill_clean)
                    st.rerun()
                elif not skill_clean:
                    st.warning("Type a skill first.")
                else:
                    st.info("Already added.")

    # ── RIGHT: Preview & Actions ──────────────────────────────────────────────
    with col_right:
        st.markdown("""
        <div style="background: #111; border: 1px solid #222; border-radius: 12px; padding: 2rem; height: 100%; display: flex; flex-direction: column;">
          <div class="card-title" style="text-align: center; margin-bottom: 2rem;">Your Skill Arsenal</div>
        """, unsafe_allow_html=True)

        if st.session_state.skills_list:
            def _sync_skills():
                st.session_state.skills_list = st.session_state.skill_chip_editor.copy()

            if "skill_chip_editor" not in st.session_state or st.session_state.skill_chip_editor != st.session_state.skills_list:
                st.session_state.skill_chip_editor = st.session_state.skills_list.copy()

            st.multiselect(
                "Your current skills",
                options=st.session_state.skills_list,
                format_func=format_skill_label,
                label_visibility="collapsed",
                key="skill_chip_editor",
                on_change=_sync_skills
            )
        else:
            st.markdown(
                '<div style="text-align: center; color: #555; padding: 2rem 0; font-family: \'Space Mono\', monospace;">'
                '[ No skills added yet ]'
                '</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='flex-grow: 1;'></div><br><br>", unsafe_allow_html=True)
        
        col_clear, col_run = st.columns([1, 2])
        with col_clear:
            if st.session_state.skills_list:
                if st.button("🗑 Clear All", use_container_width=True):
                    st.session_state.skills_list = []
                    st.rerun()

        with col_run:
            # Map display values to API values
            exp_map = {
                "Fresh Graduate (< 1 tahun)": "fresh_graduate",
                "Junior (1-2 tahun)": "junior",
                "Mid-Level (3+ tahun)": "mid_level",
            }
            bg_map = {
                "Otodidak / Self-taught": "self_taught",
                "Lulusan Bootcamp": "bootcamp",
                "Pendidikan Formal IT/CS": "formal_degree",
            }
            tl_map = {
                "Aktif Mencari Kerja (3 bulan)": "3_months",
                "Transisi Karier (1 tahun)": "1_year",
                "Fleksibel / Eksplorasi": "flexible",
            }

            if st.button("🚀 PREDICT GAP", use_container_width=True):
                if not st.session_state.skills_list:
                    st.error("Please add skills first.")
                elif not learning_background:
                    st.error("Pilih minimal 1 Latar Belakang Belajar.")
                else:
                    with st.spinner("Analyzing your profile..."):
                        gap_result = call_gap_sense_api(
                            selected_role,
                            st.session_state.skills_list,
                            experience_level=exp_map[experience_level],
                            learning_background=",".join([bg_map[bg] for bg in learning_background]),
                            target_timeline=tl_map[target_timeline],
                        )

                    if gap_result:
                        rec_skills = list(dict.fromkeys(
                            r["skill"] for r in gap_result.get("recommendations", [])
                        ))[:4]

                        trend_result = None
                        if rec_skills:
                            with st.spinner("Fetching market trends..."):
                                trend_result = call_skill_trend_api(rec_skills)
                                trend_result = filter_trends_for_role(trend_result, selected_role)

                        st.session_state.results = gap_result
                        st.session_state.trends = trend_result
                        st.session_state.page = "results"
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
#  RESULTS PAGE
# ═════════════════════════════════════════════════════════════════════════════
def results_page() -> None:
    """Renders the analysis results, skill recommendations, and trend charts."""
    r = st.session_state.results
    score = r["score"]
    recommendations = sorted(
        r.get("recommendations", []),
        key=lambda rec: (
            rec.get("final_score", 0),
            rec.get("importance", 0),
            rec.get("similarity", 0),
        ),
        reverse=True,
    )
    explanation = r["explanation"]
    user_skills = r["user_skills"]
    role = r["role"]

    # Risk level
    if score >= 25:
        risk_level, risk_cls, risk_icon = "Low", "risk-low", "🟢"
    elif score >= 5:
        risk_level, risk_cls, risk_icon = "Medium", "risk-medium", "🟡"
    else:
        risk_level, risk_cls, risk_icon = "High", "risk-high", "🔴"

    # Score interpretation
    interp_icon, interp_label, interp_desc, interp_bg = _get_score_interpretation(score)

    st.markdown("""
    <div class="hero">
      <h1>📊 Analysis Results</h1>
      <p>Here's your personalized skill gap report.</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    # ── LEFT ──────────────────────────────────────────────────────────────────
    with col_left:
        st.markdown('<div class="card-title">Your Skill Score</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="risk-banner {risk_cls}">
          <div style="font-size:2rem;font-weight:700;color:#e8e8e0;">{score}<span style="font-size:1rem;color:#888;">%</span></div>
          <div style="font-size:0.85rem;color:#aaa;">Role: <strong style="color:#e8e8e0;">{role.title()}</strong></div>
          <div style="margin-top:0.4rem;">Risk Level: <strong>{risk_icon} {risk_level}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(score / 100)

        # Score interpretation card
        st.markdown(f"""
        <div class="score-interp" style="background:{interp_bg};border:1px solid #333;">
          {interp_icon} <strong>{interp_label}</strong> — {interp_desc}
        </div>
        """, unsafe_allow_html=True)

        # What's Missing
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="card-title">What\'s Missing</div>', unsafe_allow_html=True)
        if not recommendations:
            st.success("🎉 You have all the essential skills for this role!")
        else:
            for rec in recommendations:
                pct = rec["final_score"]
                if pct >= 70:
                    bar_color = "#4caf50"
                    pct_color = "#4caf50"
                elif pct >= 40:
                    bar_color = "#f0e040"
                    pct_color = "#f0e040"
                else:
                    bar_color = "#ef5350"
                    pct_color = "#ef5350"

                st.markdown(f"""
                <div class="rec-row">
                  <span class="rec-skill-name">{format_skill_label(rec['skill'])}</span>
                  <div class="rec-bar-track">
                    <div class="rec-bar-fill" style="width:{pct}%;background:{bar_color};"></div>
                  </div>
                  <span class="rec-pct" style="color:{pct_color};">{pct}%</span>
                </div>
                """, unsafe_allow_html=True)

    # ── RIGHT ─────────────────────────────────────────────────────────────────
    with col_right:
        st.markdown('<div class="card-title">Your Current Skills</div>', unsafe_allow_html=True)
        tags_html = "".join(f'<span class="skill-tag">{format_skill_label(s)}</span>' for s in user_skills)
        st.markdown(tags_html, unsafe_allow_html=True)

        # ── User Profile Summary Card ─────────────────────────────────────
        ctx = r.get("user_context", {})
        if ctx:
            # Label mappings for display
            exp_labels = {
                "fresh_graduate": "🎓 Fresh Graduate",
                "junior": "💼 Junior (1-2 tahun)",
                "mid_level": "⚡ Mid-Level (3+ tahun)",
            }
            bg_labels = {
                "self_taught": "📚 Otodidak",
                "bootcamp": "🏕️ Bootcamp",
                "formal_degree": "🎓 Pendidikan Formal IT/CS",
            }
            tl_labels = {
                "3_months": "⏱️ 3 Bulan (Aktif Cari Kerja)",
                "1_year": "📅 1 Tahun (Transisi Karier)",
                "flexible": "🌊 Fleksibel / Eksplorasi",
            }

            exp_display = exp_labels.get(ctx.get("experience_level", ""), ctx.get("experience_level", "-"))
            
            bg_raw = ctx.get("learning_background", "")
            bg_keys = [k.strip() for k in bg_raw.split(",") if k.strip()]
            bg_display = " + ".join(bg_labels.get(k, k) for k in bg_keys) if bg_keys else "-"
            
            tl_display = tl_labels.get(ctx.get("target_timeline", ""), ctx.get("target_timeline", "-"))

            st.markdown(f"""
            <div style="background: #111; border: 1px solid #222; border-radius: 10px; padding: 1.2rem; margin-top: 1.2rem;">
              <div class="card-title" style="margin-bottom: 0.8rem;">📋 Analysis Profile</div>
              <div style="font-size: 0.85rem; color: #ccc; line-height: 1.8;">
                <div>{exp_display}</div>
                <div>{bg_display}</div>
                <div>{tl_display}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Trend Chart (Dropdown + Single Chart) ─────────────────────────
        trend_data = st.session_state.trends
        if trend_data and trend_data.get("trends"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div class="card-title">📈 Skill Demand Trend</div>',
                unsafe_allow_html=True,
            )
            trends = trend_data["trends"]
            skill_names = [format_skill_label(t["skill"]) for t in trends]
            selected_skill = st.selectbox(
                "Select skill to view trend",
                skill_names,
                label_visibility="collapsed",
                key="trend_selector",
            )
            # Find and render the selected trend
            sel_idx = skill_names.index(selected_skill) if selected_skill in skill_names else 0
            render_trend_chart(trends[sel_idx], sel_idx)
        elif recommendations:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div class="card-title">ðŸ“ˆ Skill Demand Trend</div>',
                unsafe_allow_html=True,
            )
            st.caption("No role-relevant trend data available for the current top recommendations.")

    # ── Full-width: AI Explanation (Accordion) ────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="card-title">AI Career Consultant Explanation</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#888;font-size:0.85rem;margin-bottom:1rem;">'
        'Klik setiap skill untuk melihat penjelasan detail.</p>',
        unsafe_allow_html=True,
    )

    # Parse the numbered explanation into per-skill expanders
    _render_explanation_accordion(explanation, recommendations)

    # ── Recommended Projects Card ─────────────────────────────────────────
    rec_projects = r.get("recommended_projects", [])
    if rec_projects:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="card-title">💻 Referensi Proyek Portofolio</div>', unsafe_allow_html=True)
        st.markdown(
            '<p style="color:#888;font-size:0.85rem;margin-bottom:1rem;">'
            'Tingkatkan portofolio Anda dengan mengerjakan proyek-proyek di bawah ini '
            'yang direkomendasikan karena paling cocok dengan <b>skill Anda saat ini</b>!</p>',
            unsafe_allow_html=True,
        )

        project_columns = st.columns(2, gap="large") if len(rec_projects) > 3 else [st.container()]

        for idx, p in enumerate(rec_projects):
            score = p.get("score", 0)
            if score >= 0.8:
                score_color = "#4caf50" # Green
                match_text = "Sangat Cocok"
            elif score >= 0.5:
                score_color = "#ffb300" # Orange-Yellow
                match_text = "Menengah"
            else:
                score_color = "#ef5350" # Red
                match_text = "Menantang"
                
            diff_colors = {
                "beginner": "#4caf50",
                "intermediate": "#2196f3",
                "advanced": "#9c27b0"
            }
            diff_color = diff_colors.get(p.get("difficulty", "beginner"), "#888")
            
            # Highlight matched skills
            matched_set = set(p.get("skills_matched", []))
            skills_req_html = ""
            for s in p.get("skills_required", []):
                if s in matched_set:
                    # Highlight green if user has it
                    skills_req_html += f'<span style="background: #1b3320; border: 1px solid #4caf50; color: #4caf50; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-right: 4px; display: inline-block; margin-bottom: 4px;">{format_skill_label(s)} ✓</span>'
                else:
                    # Grey out if user doesn't have it
                    skills_req_html += f'<span style="background: #222; border: 1px solid #444; color: #888; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-right: 4px; display: inline-block; margin-bottom: 4px;">{format_skill_label(s)}</span>'

            category_label = p.get("category", "").replace("_", " ").title()
            matched_count = p.get("match_count", len(matched_set))
            target_column = project_columns[idx % len(project_columns)]
            with target_column:
                st.markdown(f"""
                <div style="background: #111; border: 1px solid #333; border-radius: 10px; padding: 1.05rem; margin-bottom: 1rem; border-left: 4px solid {score_color}; min-height: 230px;" class="hover-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.8rem; margin-bottom: 0.7rem;">
                        <div>
                            <div style="font-weight: 600; font-size: 1.05rem; color: #fff; margin-bottom: 0.35rem;">{p.get('name', 'Project').title()}</div>
                            <div style="display: flex; gap: 0.4rem; flex-wrap: wrap;">
                                <span style="background:#181818;border:1px solid #2e2e2e;color:#b8b8b8;padding:2px 8px;border-radius:999px;font-size:0.68rem;text-transform:uppercase;">{category_label}</span>
                                <span style="background:#181818;border:1px solid #2e2e2e;color:#b8b8b8;padding:2px 8px;border-radius:999px;font-size:0.68rem;">{matched_count} skill match</span>
                            </div>
                        </div>
                        <div style="background: {diff_color}22; color: {diff_color}; border: 1px solid {diff_color}; padding: 3px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; text-transform: uppercase; white-space: nowrap;">{p.get('difficulty', '')}</div>
                    </div>
                    <div style="color: #aaa; font-size: 0.9rem; margin-bottom: 0.9rem; line-height: 1.55;">
                        {p.get('description', '')}
                    </div>
                    <div style="font-size: 0.78rem; color: #888; margin-bottom: 0.55rem; font-weight: bold;">
                        Match score: <span style="color: {score_color};">{int(score*100)}% ({match_text})</span>
                    </div>
                    <div>{skills_req_html}</div>
                </div>
                """, unsafe_allow_html=True)


    # ── Conclusion / Roadmap Card ─────────────────────────────────────────
    conclusion = r.get("conclusion", "")
    if conclusion:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="card-title">🎯 Ringkasan & Roadmap Karier</div>', unsafe_allow_html=True)
        st.info(conclusion.replace("**", ""), icon="💡")

    # ── Disclaimer ────────────────────────────────────────────────────────
    st.markdown(
        '<p style="color:#555;font-size:0.75rem;text-align:center;margin-top:2rem;">'
        '⚠️ Skor ini dihitung berdasarkan data real job postings. '
        'Untuk fresh graduate, skor 25–50% sudah menunjukkan kesiapan melamar posisi junior. '
        'Hasil analisis bersifat informatif dan bukan penilaian absolut.</p>',
        unsafe_allow_html=True,
    )

    # ── Back button ───────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()


def _render_explanation_accordion(explanation: str, recommendations: list) -> None:
    """Parse the LLM explanation and render it as accordion expanders per skill."""
    import re as _re

    # Clean any bolding
    explanation = explanation.replace("**", "")

    # Try splitting by numbered list pattern (e.g. "1.", "2.", etc.)
    sections = _re.split(r'\n(?=\d+[\.\)])', explanation.strip())

    if len(sections) > 1:
        # Successfully parsed numbered sections
        skill_idx = 0
        for section in sections:
            section = section.strip()
            # Skip introductory text blocks
            if not section or not section[0].isdigit():
                if len(section) > 10 and "berikut adalah" not in section.lower():
                    st.markdown(section)
                continue

            # Extract skill name from first line
            first_line = section.split('\n')[0]
            match = _re.match(r'\d+[\.\)]\s*(.+?)\s*[-–:—→]', first_line)
            if match:
                skill_label = format_skill_label(match.group(1).strip())
                # Remove the "1. SkillName:" prefix from the body text
                prefix_to_remove = match.group(0)
                if section.startswith(prefix_to_remove):
                    section = section[len(prefix_to_remove):].strip()
            else:
                skill_label = format_skill_label(first_line[:60].strip())
            with st.expander(f"📌 {skill_label}", expanded=False):
                if skill_idx < len(recommendations):
                    st.caption(_build_score_reason_text(recommendations[skill_idx]))
                st.markdown(section, unsafe_allow_html=True)
            skill_idx += 1
    else:
        # Fallback: render each recommendation as a separate expander
        paragraphs = [p.strip() for p in explanation.split('\n\n') if p.strip()]
        for i, para in enumerate(paragraphs):
            skill_name = format_skill_label(recommendations[i]["skill"]) if i < len(recommendations) else f"Skill {i+1}"
            with st.expander(f"📌 {skill_name}", expanded=False):
                if i < len(recommendations):
                    st.caption(_build_score_reason_text(recommendations[i]))
                st.markdown(para, unsafe_allow_html=True)


def _build_score_reason_text(rec: dict) -> str:
    """Explain the missing-score in user-facing language."""
    score = int(rec.get("final_score", 0))
    if score >= 60:
        return (
            f"Skor {score}% menunjukkan bahwa skill ini termasuk kebutuhan yang cukup kuat "
            "untuk role target dan layak diprioritaskan lebih awal."
        )
    if score >= 45:
        return (
            f"Skor {score}% menunjukkan bahwa skill ini cukup penting untuk memperkuat profil Anda, "
            "meski masih ada beberapa skill yang lebih mendesak untuk didahulukan."
        )
    if score >= 30:
        return (
            f"Skor {score}% menunjukkan bahwa skill ini bersifat pendukung. Skill ini tetap berguna, "
            "tetapi tidak perlu menjadi fokus pertama jika fondasi utama Anda belum lengkap."
        )
    return (
        f"Skor {score}% menunjukkan bahwa skill ini lebih cocok dianggap sebagai pelengkap. "
        "Fokus utama sebaiknya tetap pada skill dengan prioritas yang lebih tinggi."
    )


def render_trend_chart(trend: dict, idx: int):
    """Render a single skill trend chart using Plotly."""
    skill = trend["skill"]
    months = trend["months"]
    counts = trend["counts"]
    pred_month = trend["predicted_month"]
    pred_value = trend["predicted_value"]

    # Split historical vs prediction
    hist_months = [m for m in months if m != pred_month]
    hist_counts = counts[:len(hist_months)]

    fig = go.Figure()

    # Historical line
    fig.add_trace(go.Scatter(
        x=hist_months,
        y=hist_counts,
        mode="lines+markers",
        name="Historical",
        line=dict(color="#f0e040", width=2),
        marker=dict(size=5, color="#f0e040"),
    ))

    # Prediction point + dashed connection
    if hist_months:
        fig.add_trace(go.Scatter(
            x=[hist_months[-1], pred_month],
            y=[hist_counts[-1], pred_value],
            mode="lines+markers",
            name="Prediction",
            line=dict(color="#4caf50", width=2, dash="dash"),
            marker=dict(size=8, color="#4caf50", symbol="star"),
        ))

    fig.update_layout(
        title=dict(
            text=f"{format_skill_label(skill)}<br><sup>Historical data through {hist_months[-1] if hist_months else pred_month}, forecast for {pred_month}</sup>",
            font=dict(family="Space Mono, monospace", size=14, color="#e8e8e0"),
        ),
        plot_bgcolor="#161616",
        paper_bgcolor="#0d0d0d",
        font=dict(color="#888"),
        xaxis=dict(
            showgrid=False,
            tickangle=-45,
            tickfont=dict(size=9),
        ),
        yaxis=dict(
            title="Job Demand",
            gridcolor="#2a2a2a",
            gridwidth=0.5,
        ),
        legend=dict(
            font=dict(size=10),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=40, r=20, t=40, b=60),
        height=300,
    )

    st.plotly_chart(fig, use_container_width=True, key=f"chart_{skill}_{idx}")


# ─── Router ──────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    home_page()
else:
    results_page()

# ─── Inject Custom Professional Footer ───────────────────────────────────────
st.markdown("""
<div class="custom-footer">
  Gap Sense Platform &bull; Developed by <span class="highlight">Capstone Team DB10-G002</span> (Dicoding)
</div>
""", unsafe_allow_html=True)
