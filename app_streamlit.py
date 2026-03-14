import os
import pickle

import pandas as pd
import streamlit as st
from groq import Groq
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GapSense - Career Skill Gap Analysis",
    page_icon="🎯",
    layout="wide",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
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

  /* ── Recommendation row ── */
  .rec-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 0;
    border-bottom: 1px solid #1e1e1e;
  }
  .rec-row:last-child { border-bottom: none; }
  .rec-skill-name { font-size: 0.95rem; color: #e8e8e0; }

  /* ── Progress bar override ── */
  .stProgress > div > div > div > div {
    background: #f0e040 !important;
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

  /* ── Divider ── */
  hr { border-color: #222; }
</style>
""", unsafe_allow_html=True)


# ─── Model Loading ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_resources():
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    with open("skill_vocab.pkl", "rb") as f:
        all_skills = pickle.load(f)
    with open("skill_embeddings.pkl", "rb") as f:
        skill_embeddings = pickle.load(f)
    role_skill_freq = pd.read_csv("role_skill_freq.csv")
    role_skill_freq["importance"] = (
        role_skill_freq.groupby("role")["count"]
        .transform(lambda x: x / x.max())
    )
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY")) # remove hardcoded key for security, set it in your environment variables as GROQ_API_KEY
    # groq_client = Groq(api_key="gsk_eNFMWRQ8IZx669k4PyLVWGdyb3FYzQ1HapB3eb4wnLIAKB941VA") for direct tings
    return embed_model, all_skills, skill_embeddings, role_skill_freq, groq_client


# ─── Inference Class (mirrors main.py) ────────────────────────────────────────
class Inference:
    model = None
    role_skill_freq = None
    skill_embeddings = None
    all_skills = None
    client = None

    def __init__(self, target_role, user_skills, top_k=10):
        self.target_role = target_role
        self.user_skills = user_skills
        self.top_k = top_k

    def filter_role(self):
        self.role_df = self.role_skill_freq[
            self.role_skill_freq["role"] == self.target_role
        ].copy()

    def encode_user_skills(self):
        self.user_emb = self.model.encode(self.user_skills, normalize_embeddings=True)

    def similarity(self):
        sim_matrix = cosine_similarity(self.user_emb, self.skill_embeddings)
        skill_sim_scores = sim_matrix.max(axis=0)
        skill_sim_map = dict(zip(self.all_skills, skill_sim_scores))
        self.role_df["similarity"] = (
            self.role_df["clean_skills"].map(skill_sim_map).fillna(0)
        )

    def importance(self):
        self.role_df["importance"] = (
            self.role_df.groupby("role")["count"]
            .transform(lambda x: x / x.max())
        )

    def mark_user_skills(self):
        user_skills_set = set(self.user_skills)
        self.role_df["has_skill"] = self.role_df["clean_skills"].isin(user_skills_set)

    def final_score(self):
        w_sim, w_imp = 0.8, 0.2
        self.role_df["final_score"] = (
            w_sim * self.role_df["similarity"] +
            w_imp * self.role_df["importance"]
        )

    def recommendations(self):
        self.recommendations_df = (
            self.role_df[~self.role_df["has_skill"]]
            .sort_values("final_score", ascending=False)
            .head(self.top_k)
            .reset_index(drop=True)
        )

    def result_skill_gap(self):
        result = []
        for _, row in self.recommendations_df.iterrows():
            skill = row["clean_skills"]
            pct = round(row["final_score"] * 100)
            result.append(f"{skill} -> {pct}%")
        self.result_in_text = "\n".join(result)

    def overall_score(self):
        """Compute coverage score: how many role skills user already has (weighted by importance)."""
        matched = self.role_df[self.role_df["has_skill"]]["importance"].sum()
        total   = self.role_df["importance"].sum()
        return round((matched / total) * 100) if total > 0 else 0

    def generate_explanation(self):
        prompt = f"""
Anda adalah konsultan karier profesional di bidang teknologi.

Target role: {self.target_role}
Skill user: {', '.join(self.user_skills)}

Berikut adalah daftar skill yang direkomendasikan beserta skor relevansinya:
{self.result_in_text}

Skor persentase mencerminkan tingkat relevansi strategis skill berdasarkan kombinasi tingkat penguasaan user dan kebutuhan industri.
Bahas ke{self.top_k} skill yang tercantum di atas tanpa melewatkan satu pun.
- Jelaskan kenapa skill tersebut penting
- Hubungan dengan skill user
- Berikan contoh implementasi nyata dalam pekerjaan
- Berikan saran singkat bagaimana cara mulai mempelajarinya

Gunakan Bahasa Indonesia formal, jelas, dan ringkas.
Tuliskan jawaban dalam bentuk daftar bernomor sesuai urutan skill di atas.
"""
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Anda adalah AI konsultan karier profesional."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content

    def run(self):
        self.filter_role()
        self.encode_user_skills()
        self.similarity()
        self.importance()
        self.mark_user_skills()
        self.final_score()
        self.recommendations()
        self.result_skill_gap()
        score   = self.overall_score()
        explanation = self.generate_explanation()
        return score, self.recommendations_df, explanation


# ─── Session State Init ────────────────────────────────────────────────────────
if "skills_list" not in st.session_state:
    st.session_state.skills_list = []
if "page" not in st.session_state:
    st.session_state.page = "home"
if "results" not in st.session_state:
    st.session_state.results = None


# ═══════════════════════════════════════════════════════════════════════════════
#  HOME PAGE
# ═══════════════════════════════════════════════════════════════════════════════
# if 'something' not in st.session_state:
#     st.session_state.skill_input = ""

# def clear_text():
#     st.session_state.something = st.session_state.skill_input
#     st.session_state.skill_input = ""

def home_page():
    st.markdown("""
    <div class="hero">
      <h1>🎯 SkillGap Analyzer</h1>
      <p>Identify missing skills and bridge the gap to your target career role.</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    # ── LEFT: Role + Skill Input ───────────────────────────────────────────────
    with col_left:
        st.markdown('<div class="card-title">Select Profession</div>', unsafe_allow_html=True)
        role_map = {
            "Front End": "frontend",
            "Back End":  "backend",
            "Data Analyst": "data analyst",
        }
        selected_label = st.radio(
            "",
            list(role_map.keys()),
            label_visibility="collapsed",
        )
        selected_role = role_map[selected_label]
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card-title">Add Your Skills</div>', unsafe_allow_html=True, )
        new_skill = st.text_input(
            "something",
            placeholder="e.g. Python, React, SQL …",
            label_visibility="collapsed",
            key="skill_input",
            # on_change=clear_text,

        )
        if st.button("Insert Skill"):
            skill_clean = new_skill.strip().lower()
            if skill_clean and skill_clean not in st.session_state.skills_list:
                st.session_state.skills_list.append(skill_clean)
                st.rerun()
                st.text_input

            elif not skill_clean:
                st.warning("Please type a skill first.")
            else:
                st.info(f"'{skill_clean}' is already in your list.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── RIGHT: Skills Preview ──────────────────────────────────────────────────
    with col_right:
        # st.markdown('<div class="card" style="min-height:220px">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Your Skills</div>', unsafe_allow_html=True)

        if st.session_state.skills_list:
            tags_html = "".join(
                f'<span class="skill-tag">{s}</span>'
                for s in st.session_state.skills_list
            )
            st.markdown(tags_html, unsafe_allow_html=True)
        else:
            st.markdown('<span style="color:#555;font-size:0.9rem;">No skills added yet.</span>', unsafe_allow_html=True)

        if st.session_state.skills_list:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑 Clear All"):
                st.session_state.skills_list = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Predict Button ─────────────────────────────────────────────────────────
    _, mid, _ = st.columns([2, 1, 2])
    with mid:
        if st.button("🚀 Predict", use_container_width=True):
            if not st.session_state.skills_list:
                st.error("Please add at least one skill before predicting.")
            else:
                try:
                    embed_model, all_skills, skill_embeddings, role_skill_freq, groq_client = load_resources()
                    Inference.model           = embed_model
                    Inference.all_skills      = all_skills
                    Inference.skill_embeddings = skill_embeddings
                    Inference.role_skill_freq = role_skill_freq
                    Inference.client          = groq_client

                    with st.spinner("Analyzing your skill profile …"):
                        inf = Inference(selected_role, st.session_state.skills_list)
                        score, recs_df, explanation = inf.run()

                    st.session_state.results = {
                        "role":        selected_role,
                        "user_skills": list(st.session_state.skills_list),
                        "score":       score,
                        "recs_df":     recs_df,
                        "explanation": explanation,
                    }
                    st.session_state.page = "results"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
#  RESULTS PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def results_page():
    r = st.session_state.results
    score       = r["score"]
    recs_df     = r["recs_df"]
    explanation = r["explanation"]
    user_skills = r["user_skills"]
    role        = r["role"]

    # Derive risk level (high score 70, medium 40, low <40) subject to change based on distribution of scores in real usage
    if score >= 25:
        risk_level, risk_cls, risk_icon = "Low",    "risk-low",    "🟢"
    elif score >= 5:
        risk_level, risk_cls, risk_icon = "Medium", "risk-medium", "🟡"
    else:
        risk_level, risk_cls, risk_icon = "High",   "risk-high",   "🔴"

    st.markdown("""
    <div class="hero">
      <h1>📊 Analysis Results</h1>
      <p>Here's your personalized skill gap report.</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    # ── LEFT ──────────────────────────────────────────────────────────────────
    with col_left:
        # Score + Risk
        # st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Your Skill Score</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="risk-banner {risk_cls}">
          <div style="font-size:2rem;font-weight:700;color:#e8e8e0;">{score}<span style="font-size:1rem;color:#888;">%</span></div>
          <div style="font-size:0.85rem;color:#aaa;">Role: <strong style="color:#e8e8e0;">{role.title()}</strong></div>
          <div style="margin-top:0.4rem;">Risk Level: <strong>{risk_icon} {risk_level}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(score / 100)
        st.markdown('</div>', unsafe_allow_html=True)

        # What's missing
        # st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">What\'s Missing</div>', unsafe_allow_html=True)
        if recs_df.empty:
            st.success("🎉 You have all the essential skills for this role!")
        else:
            for _, row in recs_df.iterrows():
                pct = round(row["final_score"] * 100)
                if pct >= 70:
                    badge_cls = "score-high"
                elif pct >= 40:
                    badge_cls = "score-medium"
                else:
                    badge_cls = "score-low"

                st.markdown(f"""
                <div class="rec-row">
                  <span class="rec-skill-name">{row['clean_skills']}</span>
                  <span class="score-badge {badge_cls}">{pct}%</span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── RIGHT ─────────────────────────────────────────────────────────────────
    with col_right:
        # User skills recap
        # st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Your Current Skills</div>', unsafe_allow_html=True)
        tags_html = "".join(f'<span class="skill-tag">{s}</span>' for s in user_skills)
        st.markdown(tags_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Full-width: AI Explanation ────────────────────────────────────────────
    # st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">AI Career Consultant Explanation</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="line-height:1.75;color:#c8c8c0;white-space:pre-wrap;">{explanation}</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Back button ───────────────────────────────────────────────────────────
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()


# ─── Router ───────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    home_page()
else:
    results_page()