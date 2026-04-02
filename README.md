---
Title: GapSense API
emoji: 🎯
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# GapSense API — Backend

> FastAPI backend powering skill gap analysis, skill demand forecasting,
> and portfolio project recommendations for the GapSense platform.

**Capstone Project DB10-G002** · Dicoding Bootcamp — Artificial Intelligence

## Features

| Feature | Description |
|---|---|
| **Skill Gap Analysis** | Semantic similarity–based matching between user skills and role requirements |
| **Skill Demand Trend** | Time-series forecasting with EWM-smoothed historical data and next-month prediction |
| **AI Explanation** | Per-skill career consultation powered by Groq API (LLaMA 3.3 70B) |
| **Career Roadmap** | Personalized conclusion and roadmap based on user profile |
| **Project Recommender** | Content-based portfolio project suggestions matched to user skills |

## Architecture

```
Capstone-AI Model/
├── Dockerfile                    # Docker config for Hugging Face Spaces
├── requirements.txt              # Python dependencies
├── modeling/
│   ├── main.py                   # FastAPI application entry point
│   ├── data/
│   │   ├── skill_trend_dataset_combined.csv  # Augmented trend dataset
│   │   └── time_series_combined.pkl          # Trained prediction model
│   └── services/
│       ├── __init__.py           # Service exports
│       ├── model_gap.py          # Skill gap analyzer (cosine similarity)
│       ├── norm_input.py         # Input normalization and alias mapping
│       ├── explanation.py        # LLM explanation and conclusion generator
│       ├── project_recommender.py # Portfolio project recommendation engine
│       └── trend_model.py        # Skill trend predictor with EWM smoothing
├── Preprocessing data/           # Jupyter notebooks and preprocessed artifacts
│   ├── skill_vocab.pkl           # Canonical skill vocabulary
│   ├── skill_embeddings.pkl      # Precomputed sentence embeddings
│   └── role_skill_freq.csv       # Role–skill frequency matrix
├── fitur_tambahan/               # Teammate's ARIMA experiments (reference)
└── generate_trend_dataset.py     # Dataset generation script (reproducibility)
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check and model status |
| `POST` | `/api/gap-sense` | Analyze skill gap for a given role |
| `POST` | `/api/skill-trend` | Get historical trend and forecast for skills |

## Local Development

### Prerequisites

- Python 3.10+
- A valid [Groq API key](https://console.groq.com/)

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create environment file
echo "GROQ_API_KEY=your_key_here" > modeling/.env
```

### Run

```bash
cd modeling
python main.py
```

The server starts at `http://localhost:8000` with interactive docs at `/docs`.

## Deployment

This repository is deployed to **Hugging Face Spaces** via GitHub Actions.
The `skill_gap_model` branch is the source of truth for deployment.

### Environment Variables (Hugging Face Secrets)

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key for Groq LLM service |

## Technical Notes

### Skill Gap Analysis (Core Engine)
- Uses **SentenceTransformer** (`all-MiniLM-L6-v2`) to compute semantic embeddings for both user skills and role requirements.
- Calculates **cosine similarity** between user skill vectors and the canonical skill vocabulary to find the closest matches.
- Final recommendation score = weighted sum of similarity (80%) and role importance (20%), with role-specific boosting and penalty adjustments.
- Applies a **diversification filter** (cosine threshold 0.85) to prevent semantically duplicate recommendations in the output.
- Role-specific **blacklists** and **boost lists** ensure recommendations stay relevant (e.g., Python is not recommended for a Frontend role).

### LLM Explanation & Career Roadmap
- Powered by **Groq API** with the `llama-3.3-70b-versatile` model.
- Generates per-skill career consultation paragraphs tailored to the user's experience level, learning background, and target timeline.
- Uses **strict prompt isolation** to prevent the LLM from mixing existing user skills into missing skill explanations.
- Produces a separate **career roadmap conclusion** that references the top-3 priority skills from the backend ranking.

### Skill Demand Trend Forecasting
- **Dataset**: Generated using an Ornstein-Uhlenbeck process with trend-aware drift (NAIK/STABIL/TURUN), inspired by team ARIMA research in `fitur_tambahan/`.
- **Prediction Model**: Ridge regression trained on MinMax-scaled monthly pivot data. Predictions are clamped to non-negative values.
- **EWM Smoothing**: Exponential Weighted Moving Average (span=4) is applied to historical counts for smooth, realistic chart visualization.
- **Fuzzy Matching**: Uses `rapidfuzz` (threshold 85%) to match user skill queries to the closest available skill in the dataset.

### Portfolio Project Recommender
- Content-based recommendation engine with a curated catalog of 50+ portfolio projects across 6 categories (frontend, backend, data analytics, data science, DevOps, cloud).
- Projects are scored by skill overlap ratio with role-category boosting and impact weighting.
- Uses `difflib` fuzzy matching to tolerate minor skill name variations in user input.

### Input Normalization
- Supports **100+ aliases** (e.g., `js` → `javascript`, `golang` → `go`, `power bi` → `power_bi`).
- Automatically splits combined skills (e.g., `html css` → `["html", "css"]`).
- Filters out soft skills, seniority keywords, and experience phrases to isolate technical skills only.
- Applies regex-based noise removal for patterns like "years of experience" or degree mentions.

## License

This project is part of the Dicoding Bootcamp Capstone Program (DB10-G002).
