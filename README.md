# GapSense Frontend

Frontend Streamlit untuk menampilkan hasil analisis GapSense dari backend FastAPI.

## Fitur Utama

- Form analisis role, profil, dan daftar skill
- Skill chip editor yang lebih mudah diubah
- Visualisasi hasil skill gap dan trend skill
- AI explanation, roadmap karier, dan rekomendasi proyek portofolio

## Kebutuhan

Frontend membutuhkan backend aktif dan dapat diakses melalui `BACKEND_API_URL`.

## Setup Lokal

Install dependency:

```bash
pip install -r requirements.txt
```

Buat file `.env` di root frontend:

```env
BACKEND_API_URL=http://localhost:8000
```

## Menjalankan Frontend

```bash
streamlit run app_streamlit.py
```

Frontend aktif di:

```text
http://localhost:8501
```

## Catatan

- Repo frontend ini dipisah dari backend agar deployment Streamlit Community Cloud tetap sederhana
- Pastikan backend berjalan dulu sebelum melakukan analisis dari UI
