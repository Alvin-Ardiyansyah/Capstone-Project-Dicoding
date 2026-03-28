"""
FastAPI Backend — Gap Sense API
Provides endpoints for skill gap analysis and skill trend prediction.
"""

import os
# Fix for network timeouts connecting to HuggingFace from local ISP
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# Force TensorFlow >= 2.16 to use Keras 3 (native format for our time_series_2.keras)
os.environ["TF_USE_LEGACY_KERAS"] = "0"

# Fix for Windows DLL conflicts between PyTorch and TensorFlow
import torch
import sentence_transformers

import pickle
from contextlib import asynccontextmanager

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from services import Normalize_Input, generate_explanation, GapSenseAnalyzer, generate_conclusion
from services.trend_model import SkillTrendPredictor

# ─── Load environment variables ───────────────────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable is not set!")


# ─── Global resources (loaded once at startup) ────────────────────────────────
class AppResources:
    """Container for shared ML resources."""
    embed_model = None
    all_skills = None
    skill_embeddings = None
    role_skill_freq = None
    groq_client = None
    trend_predictor = None


resources = AppResources()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML models and resources at startup."""
    # Load embedding model
    resources.embed_model = SentenceTransformer("all-MiniLM-L6-v2")

    # Load skill vocab & embeddings
    base_dir = os.path.dirname(os.path.abspath(__file__))
    preprocessing_dir = os.path.join(base_dir, "..", "Preprocessing data")

    with open(os.path.join(preprocessing_dir, "skill_vocab.pkl"), "rb") as f:
        resources.all_skills = pickle.load(f)

    with open(os.path.join(preprocessing_dir, "skill_embeddings.pkl"), "rb") as f:
        resources.skill_embeddings = pickle.load(f)

    # Load role-skill frequency data
    resources.role_skill_freq = pd.read_csv(
        os.path.join(preprocessing_dir, "role_skill_freq.csv")
    )
    resources.role_skill_freq["importance"] = (
        resources.role_skill_freq.groupby("role")["count"]
        .transform(lambda x: x / x.max())
    )

    # Initialize Groq client
    resources.groq_client = Groq(api_key=GROQ_API_KEY)

    # Load trend predictor
    model_path = os.path.join(base_dir, "data", "time_series_2.keras")
    dataset_path = os.path.join(base_dir, "data", "skill_trend_dataset_2.csv")

    if os.path.exists(model_path) and os.path.exists(dataset_path):
        resources.trend_predictor = SkillTrendPredictor(model_path, dataset_path)

    yield  # App runs here

    # Cleanup (if needed)


# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Gap Sense API",
    description="API for career skill gap analysis and skill trend prediction.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Streamlit frontend to call
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Pydantic Models ─────────────────────────────────────────────────────────
class GapSenseRequest(BaseModel):
    """Request body for skill gap analysis."""
    role: str
    skills: list[str]
    top_k: int = 10
    experience_level: str = "fresh_graduate"
    learning_background: str = "self_taught"
    target_timeline: str = "flexible"


class SkillRecommendation(BaseModel):
    skill: str
    final_score: float
    similarity: float
    importance: float


class GapSenseResponse(BaseModel):
    role: str
    user_skills: list[str]
    score: int
    recommendations: list[SkillRecommendation]
    explanation: str
    conclusion: str
    user_context: dict = {}


class SkillTrendRequest(BaseModel):
    skills: list[str]


class SkillTrendItem(BaseModel):
    skill: str
    months: list[str]
    counts: list[float]
    predicted_month: str
    predicted_value: float


class SkillTrendResponse(BaseModel):
    trends: list[SkillTrendItem]
    available_skills: list[str]


# ─── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "trend_model_loaded": resources.trend_predictor is not None,
    }


@app.post("/api/gap-sense", response_model=GapSenseResponse)
async def analyze_gap_sense(request: GapSenseRequest):
    """
    Analyze skill gap for a given role and user skills.

    - Normalizes user input
    - Computes cosine similarity between user skills and role requirements
    - Generates AI explanation via Groq LLM
    """
    try:
        # Normalize input skills
        raw_skills = ", ".join(request.skills)
        normalizer = Normalize_Input(raw_skills)
        normalized_skills = normalizer.run_Class()

        if not normalized_skills:
            raise HTTPException(
                status_code=400,
                detail="No valid skills found after normalization."
            )

        # Run skill gap pipeline
        gap_model = GapSenseAnalyzer(
            resources.embed_model,
            resources.role_skill_freq,
            resources.skill_embeddings,
            resources.all_skills,
            request.role,
            normalized_skills,
            top_k=request.top_k,
        )
        gap_result = gap_model.output_gap()

        # Calculate overall score
        matched = gap_model.role_df[gap_model.role_df["has_skill"]]["importance"].sum()
        total = gap_model.role_df["importance"].sum()
        score = round((matched / total) * 100) if total > 0 else 0

        # Build recommendations list (deduplicated)
        recommendations = []
        seen_skills = set()
        for _, row in gap_model.recomendations_df.iterrows():
            skill_name = row["clean_skills"]
            if skill_name in seen_skills:
                continue
            seen_skills.add(skill_name)
            recommendations.append(SkillRecommendation(
                skill=skill_name,
                final_score=round(float(row["final_score"]) * 100),
                similarity=round(float(row.get("similarity", 0)) * 100),
                importance=round(float(row.get("importance", 0)) * 100),
            ))

        # Build user context for personalized LLM output
        user_context = {
            "experience_level": request.experience_level,
            "learning_background": request.learning_background,
            "target_timeline": request.target_timeline,
        }

        # Generate AI explanation
        explanation = generate_explanation(
            resources.groq_client,
            request.role,
            normalized_skills,
            gap_result,
            user_context=user_context,
        )

        # Generate career roadmap conclusion
        conclusion = generate_conclusion(
            resources.groq_client,
            request.role,
            gap_result,
            score,
            user_context=user_context,
        )

        return GapSenseResponse(
            role=request.role,
            user_skills=normalized_skills,
            score=score,
            recommendations=recommendations,
            explanation=explanation,
            conclusion=conclusion,
            user_context=user_context,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/skill-trend", response_model=SkillTrendResponse)
async def get_skill_trends(request: SkillTrendRequest):
    """
    Get historical trend and next-month prediction for given skills.
    Uses fuzzy matching to find the closest skill in the dataset.
    """
    if resources.trend_predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Trend prediction model is not loaded."
        )

    trends = []
    for skill_query in request.skills:
        result = resources.trend_predictor.get_trend_with_prediction(skill_query)
        if result:
            trends.append(SkillTrendItem(
                skill=result["skill"],
                months=result["months"],
                counts=result["counts"],
                predicted_month=result["predicted_month"],
                predicted_value=result["predicted_value"],
            ))

    return SkillTrendResponse(
        trends=trends,
        available_skills=resources.trend_predictor.get_available_skills(),
    )


# ─── Run server ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)