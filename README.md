# GapSense Frontend

> Streamlit-based web interface for the GapSense career skill gap analysis platform.

**Capstone Project DB10-G002** · Dicoding Bootcamp — Artificial Intelligence

🌐 **Live**: [gapsense.streamlit.app](https://gapsense.streamlit.app)

## Features

| Feature | Description |
|---|---|
| **Role Selection** | Choose between Front End, Back End, and Data Analyst career paths |
| **Skill Input** | Add skills with alias normalization (e.g., `js` → JavaScript) |
| **User Profile** | Experience level, learning background, and target timeline context |
| **Gap Analysis** | Visual skill score with progress bar and risk level indicator |
| **Missing Skills** | Ranked recommendations with priority percentages |
| **Demand Trends** | Interactive Plotly charts with EWM-smoothed historical data and forecast |
| **AI Explanation** | Per-skill career consultation in expandable accordion cards |
| **Project Recommendations** | Portfolio project suggestions with skill-match highlighting |
| **Career Roadmap** | AI-generated personalized conclusion and next steps |

## Architecture

```
Capstone-Frontend/
├── app_streamlit.py       # Main application (single-file Streamlit app)
├── requirements.txt       # Python dependencies
├── .env                   # Backend API URL configuration
└── .streamlit/
    └── config.toml        # Streamlit theme configuration
```

## Prerequisites

- Python 3.10+
- A running GapSense backend (see [Backend README](../Capstone-AI%20Model/README.md))

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure backend URL
echo "BACKEND_API_URL=http://localhost:8000" > .env

# Run the app
streamlit run app_streamlit.py
```

The app starts at `http://localhost:8501`.

## Deployment

This application is deployed on **Streamlit Community Cloud** from the `front-end` branch.

### Secrets (Streamlit Cloud)

| Variable | Description |
|---|---|
| `BACKEND_API_URL` | Full URL to the GapSense backend API |

## Design

- **Theme**: Dark mode with `#0d0d0d` background and `#f0e040` accent
- **Typography**: Space Mono (headings) + DM Sans (body)
- **Charts**: Plotly with spline curves, gradient fill, and prediction annotations
- **Layout**: Two-column responsive design with card-based components

## Technical Notes

- The frontend is intentionally decoupled from the backend to enable independent deployment on free-tier platforms (Streamlit Cloud + Hugging Face Spaces).
- Skill input normalization runs both client-side (frontend aliases) and server-side (backend `Normalize_Input`) to maximize accuracy.
- The `st.multiselect` skill editor uses `on_change` callbacks to prevent Streamlit's widget state synchronization issues.

## License

This project is part of the Dicoding Bootcamp Capstone Program (DB10-G002).
