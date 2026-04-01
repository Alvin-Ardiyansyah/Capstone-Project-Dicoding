"""
Skill Trend Predictor Module
Menggunakan model Keras (Dense NN) untuk memprediksi tren demand skill
berdasarkan data historis job postings.
"""

import os
import pickle
import numpy as np
import pandas as pd
from rapidfuzz import process
from sklearn.preprocessing import MinMaxScaler


class SkillTrendPredictor:
    """Memprediksi tren demand skill menggunakan model time-series sederhana."""

    def __init__(self, model_path: str, dataset_path: str):
        """
        Args:
            model_path: Path ke file model Keras (.keras)
            dataset_path: Path ke file CSV dataset skill trend
        """
        self.model = self._load_model(model_path)
        self.model_path = model_path
        self.scaler = MinMaxScaler()

        # Load & preprocess dataset
        df = pd.read_csv(dataset_path)
        df = df.rename(columns={"posted_date": "posting_date"}) if "posted_date" in df.columns else df
        df["posting_date"] = pd.to_datetime(df.get("posting_date", df.get("posted_date", "")))

        # Clean skills_required
        df["skills_required"] = df["skills_required"].astype(str).str.lower()
        df = df.drop_duplicates()
        df["skills_required"] = df["skills_required"].str.split(",")
        df = df.explode("skills_required")
        df["skills_required"] = df["skills_required"].apply(self._clean_skill)

        # Drop non-essential columns
        cols_to_drop = [
            "company_name", "industry", "experience_level",
            "employment_type", "location", "salary_range_usd",
            "company_size", "tools_preferred", "year"
        ]
        existing_cols = [c for c in cols_to_drop if c in df.columns]
        df = df.drop(columns=existing_cols, errors="ignore")

        # Remove unnamed index column if exists
        unnamed_cols = [c for c in df.columns if "unnamed" in c.lower()]
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)

        # Create month column & pivot
        df["month"] = df["posting_date"].dt.to_period("M")
        skill_trend = df.groupby(["month", "skills_required"]).size().reset_index(name="count")
        self.pivot = skill_trend.pivot(
            index="month", columns="skills_required", values="count"
        ).fillna(0)

        # Fit scaler
        self.scaler.fit(self.pivot.values)

        # Skill list for fuzzy matching
        self.skills = self.pivot.columns.tolist()

    @staticmethod
    def _load_model(model_path: str):
        """Load either a legacy Keras model or an sklearn pickle model."""
        suffix = os.path.splitext(model_path)[1].lower()
        if suffix == ".pkl":
            with open(model_path, "rb") as handle:
                return pickle.load(handle)

        from tensorflow.keras.models import load_model

        return load_model(model_path)

    @staticmethod
    def _clean_skill(skill: str) -> str:
        """Membersihkan string skill dari karakter yang tidak diinginkan."""
        return skill.replace("[", "").replace("]", "").replace("'", "").strip()

    def find_skill(self, query: str) -> str | None:
        """
        Fuzzy match query user ke skill yang tersedia.

        Returns:
            Nama skill yang cocok, atau None jika tidak ditemukan.
        """
        query = query.lower().strip()
        best_match = process.extractOne(query, self.skills)
        if best_match and best_match[1] > 85:
            return best_match[0]
        return None

    def get_historical_trend(self, skill_query: str) -> dict | None:
        """
        Mendapatkan data historis demand per bulan untuk skill tertentu.

        Returns:
            Dict dengan keys: skill, months, counts. Atau None jika skill tidak ditemukan.
        """
        skill = self.find_skill(skill_query)
        if skill is None:
            return None

        series = self.pivot[skill]
        months = [str(p) for p in series.index]
        counts = series.values.tolist()

        return {
            "skill": skill,
            "months": months,
            "counts": counts
        }

    def predict_next_month(self) -> dict:
        """
        Prediksi demand semua skill untuk bulan berikutnya.

        Returns:
            Dict dengan keys: skill names, values: predicted demand (float).
        """
        data_scaled = self.scaler.transform(self.pivot.values)
        last_month_scaled = data_scaled[-1].reshape(1, -1)
        if hasattr(self.model, "predict"):
            if self.model_path.lower().endswith(".pkl"):
                prediction_scaled = self.model.predict(last_month_scaled)
            else:
                prediction_scaled = self.model.predict(last_month_scaled, verbose=0)
        else:
            raise ValueError("Loaded trend model does not support predict().")
        prediction = self.scaler.inverse_transform(prediction_scaled).flatten()

        result = {}
        for skill, value in zip(self.pivot.columns, prediction):
            result[skill] = round(float(value), 2)

        return result

    def get_trend_with_prediction(self, skill_query: str) -> dict | None:
        """
        Gabungan data historis + prediksi bulan depan untuk satu skill.

        Returns:
            Dict lengkap atau None jika skill tidak ditemukan.
        """
        historical = self.get_historical_trend(skill_query)
        if historical is None:
            return None

        predictions = self.predict_next_month()
        skill = historical["skill"]
        predicted_value = predictions.get(skill, 0.0)

        # Hitung next month label
        last_period = self.pivot.index[-1]
        next_period = last_period + 1

        return {
            "skill": skill,
            "months": historical["months"] + [str(next_period)],
            "counts": historical["counts"] + [predicted_value],
            "predicted_month": str(next_period),
            "predicted_value": predicted_value
        }

    def get_available_skills(self) -> list[str]:
        """Return daftar semua skill yang tersedia di dataset."""
        return self.skills
