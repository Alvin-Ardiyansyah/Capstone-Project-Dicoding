"""
Skill Gap Analysis Module.

Calculates the gap between user skills and required role skills
using semantic embeddings and cosine similarity.
"""

import os
from typing import List, Dict, Any
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


ROLE_BLACKLISTS = {
    "frontend": {
        "python", "java", "php", "c#", "c++", "ruby", "go", "rust", "kotlin",
        "r", "numpy", "pandas", "scikit-learn", "tensorflow", "pytorch",
        "django", "flask", "spring", "laravel", "docker", "kubernetes",
        "mysql", "postgresql", "mongodb", "redis", "oracle",
    },
    "data analyst": {
        "react", "angular", "vue", "css", "html", "node.js",
        "webpack", "vite", "next", "nuxt", "svelte", "typescript",
        "sass", "tailwind css", "bootstrap", "jquery", "express", "nestjs",
    },
    "backend": {
        "figma", "photoshop", "illustrator", "sass",
        "tailwind css", "bootstrap", "jquery", "gatsby",
    },
    "machine learning": {
        "react", "angular", "vue", "css", "html", "figma",
        "webpack", "vite", "next", "nuxt", "svelte", "jquery",
    },
}

ROLE_BOOST_SKILLS = {
    "frontend": {
        "html", "css", "javascript", "typescript", "react", "node.js",
        "webpack", "vite", "next", "vue", "angular", "npm", "yarn",
    },
    "backend": {
        "python", "java", "php", "laravel", "flask", "fastapi", "django",
        "node.js", "express", "nestjs", "sql", "postgresql", "mysql",
        "docker", "kubernetes", "bash", "api", "microservices", "redis",
        "mongodb", "authentication", "jwt", "security", "go", "c#",
    },
    "data analyst": {
        "sql", "python", "excel", "tableau", "power_bi", "r",
        "data_analysis", "data_visualization", "statistics", "snowflake",
        "aws", "azure", "looker", "business intelligence",
    },
}

ROLE_PENALTY_SKILLS = {
    "frontend": {
        "sql", "mysql", "postgresql", "mongodb", "redis", "oracle",
        "docker", "kubernetes", "numpy", "pandas", "scikit-learn",
        "tensorflow", "pytorch", "django", "flask", "spring", "laravel",
    },
    "backend": {
        "html", "css", "jquery", "sass", "tailwind css", "bootstrap",
        "figma", "photoshop", "illustrator", "numpy", "pandas",
        "scikit-learn", "tensorflow", "pytorch", "data_analysis",
        "data_visualization", "tableau", "power_bi", "excel", "r",
    },
    "data analyst": {
        "html", "css", "javascript", "typescript", "react", "angular",
        "vue", "node.js", "webpack", "vite", "next", "express", "nestjs",
    },
}

ROLE_STRONG_PENALTIES = {
    "frontend": {
        "react native": 0.38,
        "jquery": 0.28,
        "wordpress": 0.18,
    },
    "backend": {
        "jquery": 0.22,
        "wordpress": 0.18,
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


def env_flag(name: str, default: bool = False) -> bool:
    """Parse a boolean-like environment variable."""
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def env_float(name: str, default: float) -> float:
    """Parse a float environment variable with a safe fallback."""
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    try:
        return float(raw_value)
    except ValueError:
        return default


def format_skill_label(skill: str) -> str:
    """Convert canonical skill names into human-readable labels."""
    normalized = str(skill).strip().lower()
    if normalized in DISPLAY_SKILL_ALIASES:
        return DISPLAY_SKILL_ALIASES[normalized]
    return normalized.replace("_", " ").title()


class GapSenseAnalyzer:
    """
    Analyzes the semantic gap between a user's skillset and role requirements.
    
    Attributes:
        embed_model (SentenceTransformer): Model to compute embeddings.
        role_skill_freq (pd.DataFrame): Frequency data for skills per role.
        skill_embeddings (pd.DataFrame): Pre-calculated embeddings for all known skills.
        all_skills (dict): Vocabulary of all available skills.
        target_role (str): The target job role.
        user_skills (List[str]): List of normalized skills the user possesses.
        top_k (int): Number of missing skills to recommend.
        user_emb (np.ndarray): The computed embeddings of the user skills.
        role_df (pd.DataFrame): Filtered DataFrame containing skills for the target role.
        recomendations_df (pd.DataFrame): The final selected recommendations.
    """

    def __init__(
        self,
        model: SentenceTransformer,
        role_skill_freq: pd.DataFrame,
        skill_embeddings: pd.DataFrame,
        all_skills: dict,
        target_role: str,
        user_skills: List[str],
        top_k: int = 10,
    ):
        """Initialize the GapSenseAnalyzer with necessary models and data."""
        self.model = model
        self.role_skill_freq = role_skill_freq
        self.skill_embeddings = skill_embeddings
        self.all_skills = all_skills
        self.target_role = target_role
        self.user_skills = user_skills
        self.top_k = top_k
        self.user_emb = None
        self.role_df = None
        self.recomendations_df = None
        self.result_in_text: str = ""

    def filter_role(self) -> pd.DataFrame:
        """Filter the skill frequency dataset for the target role."""
        self.role_df = self.role_skill_freq[self.role_skill_freq["role"] == self.target_role].copy()
        return self.role_df

    def encode_user_skills(self) -> Any:
        """Compute semantic embeddings for the user's provided skills."""
        self.user_emb = self.model.encode(self.user_skills, normalize_embeddings=True)
        return self.user_emb

    def similarity(self) -> pd.DataFrame:
        """Calculate cosine similarity between user skills and all role skills."""
        sim_matrix = cosine_similarity(self.user_emb, self.skill_embeddings)
        skill_sim_scores = sim_matrix.max(axis=0)
        skill_sim_map = dict(zip(self.all_skills, skill_sim_scores))
        
        self.role_df["similarity"] = (self.role_df["clean_skills"]
                                     .map(skill_sim_map)
                                     .fillna(0))
        return self.role_df

    def importance(self) -> pd.DataFrame:
        """Normalize the importance of skills relative to the role's distribution."""
        self.role_df["importance"] = (
            self.role_df.groupby("role")["count"]
            .transform(lambda x: x / x.max())
        )
        return self.role_df

    def mark_user_skills(self) -> pd.DataFrame:
        """Identify which recommended skills the user already possesses.
        
        Uses both exact string matching AND semantic similarity (cosine >= 0.85)
        to handle cases where normalized names differ slightly.
        """
        user_skills_lower = set(s.lower().strip() for s in self.user_skills)
        
        # Exact match first
        self.role_df["has_skill"] = self.role_df["clean_skills"].str.lower().isin(user_skills_lower)
        
        # Semantic match: mark as owned if cosine similarity >= 0.85
        if self.user_emb is not None:
            for idx, row in self.role_df.iterrows():
                if row["has_skill"]:
                    continue
                skill_emb = self.model.encode([row["clean_skills"]], normalize_embeddings=True)
                sim = cosine_similarity(self.user_emb, skill_emb).max()
                if sim >= 0.85:
                    self.role_df.at[idx, "has_skill"] = True
        
        return self.role_df

    def final_score(self) -> pd.DataFrame:
        """Compute final recommendation scores using a weighted sum of similarity and importance."""
        w_sim = 0.8
        w_imp = 0.2
        self.role_df["final_score"] = (
            w_sim * self.role_df["similarity"] + 
            w_imp * self.role_df["importance"]
        )
        return self.role_df

    def recomendations(self) -> pd.DataFrame:
        """Sort and slice top recommendations that the user does not possess.
        
        Filters out very low-importance skills and applies a compact
        role-mismatch blacklist as a final safety net.
        """
        candidates = self.role_df[~self.role_df["has_skill"]].copy()
        min_importance = env_float("GAPSENSE_MIN_IMPORTANCE", 0.10)
        candidates = candidates[candidates["importance"] >= min_importance]

        target_role_lower = self.target_role.lower()
        use_role_blacklist = env_flag("GAPSENSE_USE_ROLE_BLACKLIST", True)
        forbidden_keywords = set()
        if use_role_blacklist:
            if target_role_lower in ROLE_BLACKLISTS:
                forbidden_keywords = ROLE_BLACKLISTS[target_role_lower]
            elif "machine learning" in target_role_lower:
                forbidden_keywords = ROLE_BLACKLISTS["machine learning"]

        if forbidden_keywords:
            candidates = candidates[~candidates["clean_skills"].str.lower().isin(forbidden_keywords)]

        boost_skills = ROLE_BOOST_SKILLS.get(target_role_lower, set())
        penalty_skills = ROLE_PENALTY_SKILLS.get(target_role_lower, set())
        candidates["role_adjustment"] = 0.0
        if boost_skills:
            candidates.loc[
                candidates["clean_skills"].str.lower().isin(boost_skills),
                "role_adjustment",
            ] += 0.12
        if penalty_skills:
            candidates.loc[
                candidates["clean_skills"].str.lower().isin(penalty_skills),
                "role_adjustment",
            ] -= 0.18

        strong_penalties = ROLE_STRONG_PENALTIES.get(target_role_lower, {})
        if strong_penalties:
            for skill_name, penalty_value in strong_penalties.items():
                candidates.loc[
                    candidates["clean_skills"].str.lower() == skill_name,
                    "role_adjustment",
                ] -= penalty_value

        candidates["rank_score"] = candidates["final_score"] + candidates["role_adjustment"]

        self.recomendations_df = (
            candidates
            .sort_values(["rank_score", "final_score", "importance"], ascending=False)
            .head(self.top_k)
            .reset_index(drop=True)
        )
        return self.recomendations_df

    def diversify_recommendation(self, threshold: float = 0.85) -> pd.DataFrame:
        """
        Filter out overly similar recommendations to provide diverse skill suggestions.
        
        Args:
            threshold (float): Maximum cosine similarity allowed between any two recommended skills.
            
        Returns:
            pd.DataFrame: A diversified slice of the top recommendations.
        """
        selected = []
        for _, row in self.recomendations_df.iterrows():
            skill = row["clean_skills"]
            skill_emb = self.model.encode([skill], normalize_embeddings=True)

            if not selected:
                selected.append(row)
                continue
            
            selected_skills = [r["clean_skills"] for r in selected]
            selected_emb = self.model.encode(selected_skills, normalize_embeddings=True)

            sim = cosine_similarity(skill_emb, selected_emb)
            if sim.max() < threshold:
                selected.append(row)

            if len(selected) >= self.top_k:
                break

        self.recomendations_df = pd.DataFrame(selected)
        return self.recomendations_df

    def result_summary(self) -> str:
        """Format recommendations as a text string (for legacy explanations)."""
        result = []
        for _, row in self.recomendations_df.iterrows():
            skill = format_skill_label(row["clean_skills"])
            pct = round(row["final_score"] * 100)
            sim_pct = round(float(row.get("similarity", 0)) * 100)
            imp_pct = round(float(row.get("importance", 0)) * 100)
            result.append(
                f"{skill} -> score {pct}% | similarity {sim_pct}% | importance {imp_pct}%"
            )
        self.result_in_text = '\n'.join(result)
        return self.result_in_text

    def output_gap(self) -> str:
        """Run the full gap analysis pipeline sequentially."""
        self.filter_role()
        self.encode_user_skills()
        self.similarity()
        self.importance()
        self.mark_user_skills()
        self.final_score()
        self.recomendations()
        self.diversify_recommendation()
        # Deduplicate: ensure no repeated skill names in the final output
        self.recomendations_df = self.recomendations_df.drop_duplicates(
            subset="clean_skills"
        ).sort_values(
            ["final_score", "importance", "similarity"],
            ascending=False,
        ).reset_index(drop=True)
        return self.result_summary()
