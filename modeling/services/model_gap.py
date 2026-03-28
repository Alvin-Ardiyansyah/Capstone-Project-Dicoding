"""
Skill Gap Analysis Module.

Calculates the gap between user skills and required role skills
using semantic embeddings and cosine similarity.
"""

from typing import List, Dict, Any
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


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
        
        Filters out skills with very low importance (< 0.25) to the target
        role, preventing irrelevant suggestions. Also applies hard-filtering
        of forbidden keywords based on the role to eliminate dataset noise.
        """
        candidates = self.role_df[~self.role_df["has_skill"]].copy()
        # Remove skills barely relevant to the role
        candidates = candidates[candidates["importance"] >= 0.15]
        
        # Hard filter anomalous skills that appear due to noisy dataset entries
        target_role_lower = self.target_role.lower()
        forbidden_keywords = []
        if target_role_lower == "frontend":
            forbidden_keywords = [
                # Backend / Server-side languages
                'python', 'java', 'php', 'c#', 'c++', 'c', 'ruby', 'go', 'rust', 'kotlin',
                'swift', 'dart', 'scala', 'perl', 'r',
                # Data Science / ML
                'numpy', 'pandas', 'matplotlib', 'scikit-learn', 'tensorflow', 'pytorch',
                'jupyter', 'scipy', 'seaborn',
                # Backend frameworks
                'django', 'flask', 'spring', 'laravel', 'rails', 'asp', 'net', 'net 5+',
                'net core',
                # DevOps / Infra
                'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins',
                # Databases
                'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle',
                # Package managers / Tools not frontend-specific
                'homebrew', 'chocolatey', 'pip', 'maven', 'gradle', 'nuget', 'composer',
                'powershell', 'bash',
                # Mobile
                'flutter', 'react native',
                # CMS / Legacy
                'wordpress',
                # Misc
                'visual studio solution', 'pnpm',
            ]
        elif target_role_lower == "data analyst":
            forbidden_keywords = [
                'react', 'angular', 'vue', 'css', 'html', 'node.js', 'figma', 'spring',
                'webpack', 'vite', 'next', 'nuxt', 'svelte', 'typescript', 'sass',
                'tailwind css', 'bootstrap', 'jquery', 'express', 'nestjs',
            ]
        elif target_role_lower == "backend":
            forbidden_keywords = [
                'react', 'angular', 'vue', 'css', 'html', 'figma', 'photoshop',
                'illustrator', 'webpack', 'vite', 'sass', 'tailwind css', 'bootstrap',
                'jquery', 'svelte', 'nuxt', 'next', 'gatsby',
            ]
        elif "machine learning" in target_role_lower:
            forbidden_keywords = [
                'react', 'angular', 'vue', 'css', 'html', 'figma', 'webpack', 'vite',
                'next', 'nuxt', 'svelte', 'sass', 'tailwind css', 'bootstrap', 'jquery',
                'express', 'nestjs', 'wordpress', 'php', 'laravel',
            ]
            
        if forbidden_keywords:
            candidates = candidates[~candidates["clean_skills"].str.lower().isin(forbidden_keywords)]

        self.recomendations_df = (
            candidates
            .sort_values("final_score", ascending=False)
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
            skill = row["clean_skills"]
            pct = round(row["final_score"] * 100)    
            result.append(f"{skill} -> {pct}%")
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
        ).reset_index(drop=True)
        return self.result_summary()