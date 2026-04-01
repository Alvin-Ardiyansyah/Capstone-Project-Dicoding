---
title: GapSense API
emoji: 🎯
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# GapSense API

FastAPI backend untuk analisis skill gap, forecasting tren skill, dan rekomendasi proyek portofolio pada project GapSense.

## Fitur Utama

- Analisis skill gap berbasis semantic similarity
- Forecasting tren skill dengan dataset gabungan sampai `2026-04`
- AI explanation dan roadmap karier dengan Groq
- Ranking recommendation yang lebih role-aware
- Project recommendation yang lebih banyak dan relevan per role

## Runtime Default

Backend default sekarang memakai artefak trend berikut:

- `modeling/data/skill_trend_dataset_combined.csv`
- `modeling/data/time_series_combined.pkl`

Backend tetap mendukung override via environment variable jika nanti dibutuhkan.

## Setup Lokal

Install dependency:

```bash
pip install -r requirements.txt
```

Buat file `.env` di folder `modeling/`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## Menjalankan Backend

Masuk ke folder `modeling`, lalu jalankan:

```bash
python main.py
```

Server aktif di:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

## Endpoint

- `GET /api/health`
- `POST /api/gap-sense`
- `POST /api/skill-trend`

## Catatan

- Input skill sudah lebih toleran untuk alias umum seperti `js`, `golang`, `power bi`, dan `data visualisation`
- Runtime forecasting default sekarang menggunakan model `.pkl`
- README ini tetap diperlukan karena repo ini menjadi source deploy untuk Hugging Face Space
