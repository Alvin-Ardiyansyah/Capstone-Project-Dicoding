"""
Skill Trend Predictor Module.

Forecasts skill demand trends using a trained regression model (pkl)
on historical job posting data. Applies EWM smoothing for realistic
chart visualization. The smoothing approach is inspired by the team's
ARIMA analysis (see fitur_tambahan/).
"""

import os
import pickle
import numpy as np
import pandas as pd
from rapidfuzz import process
from sklearn.preprocessing import MinMaxScaler


class SkillTrendPredictor:
    """Predicts skill demand trends using a time-series regression model."""

    def __init__(self, model_path: str, dataset_path: str):
        """
        Args:
            model_path: Path to the trained model file (.pkl or .keras).
            dataset_path: Path to the CSV dataset with historical skill trends.
        """
        self.model = self._load_model(model_path)
        self.model_path = model_path
        self.scaler = MinMaxScaler()

        # Load & preprocess dataset
        df = pd.read_csv(dataset_path)
        df = df.rename(columns={"posted_date": "posting_date"}) if "posted_date" in df.columns else df
        df["posting_date"] = pd.to_datetime(df.get("posting_date", df.get("posted_date", "")))

        # Normalize skill names to lowercase
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

        # Remove unnamed index columns if present
        unnamed_cols = [c for c in df.columns if "unnamed" in c.lower()]
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)

        # Create monthly pivot table (rows=months, cols=skills, values=count)
        df["month"] = df["posting_date"].dt.to_period("M")
        skill_trend = df.groupby(["month", "skills_required"]).size().reset_index(name="count")
        self.pivot = skill_trend.pivot(
            index="month", columns="skills_required", values="count"
        ).fillna(0)

        # Fit MinMax scaler for model input normalization
        self.scaler.fit(self.pivot.values)

        # Build skill list for fuzzy matching
        self.skills = self.pivot.columns.tolist()

    @staticmethod
    def _load_model(model_path: str):
        """Load a pickled sklearn model or a Keras model based on file extension."""
        suffix = os.path.splitext(model_path)[1].lower()
        if suffix == ".pkl":
            with open(model_path, "rb") as handle:
                return pickle.load(handle)

        from tensorflow.keras.models import load_model
        return load_model(model_path)

    @staticmethod
    def _clean_skill(skill: str) -> str:
        """Remove stray brackets and quotes from skill strings."""
        return skill.replace("[", "").replace("]", "").replace("'", "").strip()

    def find_skill(self, query: str) -> str | None:
        """
        Fuzzy-match a user query to the closest available skill.

        Returns:
            The matched skill name, or None if no match scores above 85%.
        """
        query = query.lower().strip()
        best_match = process.extractOne(query, self.skills)
        if best_match and best_match[1] > 85:
            return best_match[0]
        return None

    def get_historical_trend(self, skill_query: str) -> dict | None:
        """
        Retrieve monthly demand data for a skill with EWM smoothing applied.

        Uses Exponential Weighted Moving Average (span=4) to produce smooth,
        realistic curves. This approach is inspired by the ARIMA team analysis.

        Returns:
            Dict with keys: skill, months, counts, counts_raw.
            Returns None if the skill is not found.
        """
        skill = self.find_skill(skill_query)
        if skill is None:
            return None

        raw_series = self.pivot[skill]

        # Apply EWM smoothing (span=4) for clean visualization
        smoothed = raw_series.ewm(span=4, adjust=False).mean()

        months = [str(p) for p in smoothed.index]
        counts = [round(float(v), 2) for v in smoothed.values]

        return {
            "skill": skill,
            "months": months,
            "counts": counts,
            "counts_raw": raw_series.values.tolist(),
        }

    def predict_next_month(self) -> dict:
        """
        Predict demand for all skills for the next month.

        Returns:
            Dict mapping skill names to predicted demand values (float).
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
        # Clamp to non-negative — job demand can never be below zero
        prediction = np.clip(prediction, 0, None)

        result = {}
        for skill, value in zip(self.pivot.columns, prediction):
            result[skill] = round(float(value), 2)

        return result

    def get_trend_with_prediction(self, skill_query: str) -> dict | None:
        """
        Combine smoothed historical data with next-month prediction for a skill.

        Returns:
            Complete trend dict, or None if the skill is not found.
        """
        historical = self.get_historical_trend(skill_query)
        if historical is None:
            return None

        predictions = self.predict_next_month()
        skill = historical["skill"]
        predicted_value = predictions.get(skill, 0.0)

        # Compute next month label
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
        """Return list of all skills available in the dataset."""
        return self.skills
