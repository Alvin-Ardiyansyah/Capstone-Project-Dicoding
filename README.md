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

- **Trend Dataset**: Generated using an Ornstein-Uhlenbeck process with trend-aware drift (NAIK/STABIL/TURUN), inspired by team ARIMA research in `fitur_tambahan/`.
- **Prediction Model**: Ridge regression trained on MinMax-scaled monthly pivot data. Predictions are clamped to non-negative values.
- **EWM Smoothing**: Exponential Weighted Moving Average (span=4) is applied to historical counts for smooth visualization.
- **Input Normalization**: Supports 100+ aliases (e.g., `js` → `javascript`, `golang` → `go`, `power bi` → `power_bi`).

## License

This project is part of the Dicoding Bootcamp Capstone Program (DB10-G002).
