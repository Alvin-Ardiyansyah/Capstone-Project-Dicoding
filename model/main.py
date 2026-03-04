from groq import Groq
import os
import pickle
from sentence_transformers import SentenceTransformer
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')
client = Groq(
    api_key = os.environ.get("GROQ_API_KEY")
)


with open("./skill_vocab.pkl", 'rb') as f:
    all_skills = pickle.load(f)

with open("skill_embeddings.pkl", "rb") as f:
    skill_embeddings = pickle.load(f)

role_skill_freq = pd.read_csv("./role_skill_freq.csv")

role_skill_freq["importance"] = (
    role_skill_freq.groupby("role")["count"]
    .transform(lambda x: x / x.max())
)


class Inference():
    model = None
    role_skill_freq = None
    skill_embeddings = None
    all_skills = None
    client = None
    
    def __init__(self, target_role, user_skills, top_k=10):
        self.target_role = target_role
        self.user_skills = user_skills
        self.top_k = top_k
    
    def filter_role(self):
        self.role_df = self.role_skill_freq[self.role_skill_freq["role"] == self.target_role].copy()
        return self.role_df
    
    def encode_user_skills(self):
        self.user_emb = self.model.encode(self.user_skills, normalize_embeddings=True)
        return self.user_emb
    
    def similarity(self):
        sim_matrix = cosine_similarity(self.user_emb, self.skill_embeddings)
        skill_sim_scores = sim_matrix.max(axis=0)
        skill_sim_map = dict(zip(self.all_skills, skill_sim_scores))
        
        self.role_df["similarity"] = (self.role_df["clean_skills"]
                                     .map(skill_sim_map)
                                     .fillna(0))
        return self.role_df
    
    def importance(self):
        self.role_df["importance"] = (self.role_df.groupby("role")["count"]
                                      .transform(lambda x: x / x.max())
                                     )
        return self.role_df
    
    def mark_user_skills(self):
        user_skills_set = set(self.user_skills)
        self.role_df["has_skill"] = self.role_df["clean_skills"].isin(user_skills_set)
        return self.role_df
    
    def final_score(self):
        w_sim = 0.8
        w_imp = 0.2
        
        self.role_df["final_score"] = (
            w_sim * self.role_df["similarity"] + 
            w_imp * self.role_df["importance"]
        )
        return self.role_df
    
    def recomendations(self):
        self.recomendations_df = (
            self.role_df[~self.role_df["has_skill"]]
            .sort_values("final_score", ascending=False)
            .head(self.top_k)
            .reset_index(drop=True)
        )
        return self.recomendations_df
    
    def result_skill_gap(self):
        result = []
        for _, row in self.recomendations_df.iterrows():
            skill = row["clean_skills"]
            pct = round(row["final_score"] * 100)    # tingkat kecocokan
            result.append(f"{skill} -> {pct}%")
        self.result_in_text = '\n'.join(result)
        return self.result_in_text

    def generate_explanation(self):
        prompt = f"""
Anda adalah konsultan karier profesional di bidang teknologi.

Target role: {self.target_role}
Skill user: {', '.join(self.user_skills)}

Berikut adalah daftar skill yang direkomendasikan beserta skor relevansinya terhadap target role:
{self.result_in_text}

Skor persentase mencerminkan tingkat relevansi strategis skill berdasarkan kombinasi tingkat penguasaan user dan kebutuhan industri.
Bahas ke{self.top_k} skill yang tercantum di atas tanpa melewatkan satu pun.
- Jelaskan kenapa role tersebut penting
- Hubungan dengan skill user
- Berikan contoh implementasi nyata dalam pekerjaan
- Berikan saran singkat bagaimana cara mulai mempelajarinya

Gunakan Bahasa Indonesia formal, jelas, dan ringkas
Tuliskan jawaban dalam bentuk daftar bernomor sesuai urutan skill di atas..
"""
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Anda adalah AI konsultan karier profesional."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            # max_tokens=300
        )
        
        return response.choices[0].message.content
    
    def show_output(self):
        self.filter_role()
        self.encode_user_skills()
        self.similarity()
        self.importance()
        self.mark_user_skills()
        self.final_score()
        self.recomendations()
        self.result_skill_gap()
        # return self.result_skill_gap()
        return self.generate_explanation()
    
Inference.model = model
Inference.role_skill_freq = role_skill_freq
Inference.skill_embeddings = skill_embeddings
Inference.all_skills = all_skills
Inference.client = client

role = "backend"
skill = ["python", "flask"]

inf = Inference(role, skill)
print(inf.show_output())    # skill -> tingkat kecocokan