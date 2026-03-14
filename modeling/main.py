from groq import Groq
import os
from sentence_transformers import SentenceTransformer
from model import Normalize_Input, Skills_Gap, generate_explanation
import pandas as pd
import pickle

model = SentenceTransformer('all-MiniLM-L6-v2')
client = Groq(
    api_key = os.environ.get("GROQ_API_KEY") # Isi API key grok di bash 
)

with open("../Preprocessing data/skill_vocab.pkl", 'rb') as f:
    all_skills = pickle.load(f)


with open("../Preprocessing data/skill_embeddings.pkl", "rb") as f:
    skill_embeddings = pickle.load(f)

role_skill_freq = pd.read_csv("../Preprocessing data/role_skill_freq.csv")

role_skill_freq["importance"] = (
    role_skill_freq.groupby("role")["count"]
    .transform(lambda x: x / x.max())
)

def run_skill_gap_pipeline(role, skills, model, role_skill_freq, skill_embeddings, all_skills, client):
    
    # normalize input
    skill_norm = Normalize_Input(skills)
    skill_norm = skill_norm.run_Class()
    
    # hitung skill gap
    gap_model = Skills_Gap(
        model,
        role_skill_freq,
        skill_embeddings,
        all_skills,
        role,
        skill_norm
    )
    
    gap_result = gap_model.output_gap()
    
    # generate explanation
    explanation = generate_explanation(
        client,
        role,
        skill_norm,
        gap_result
    )
    
    return explanation



# role = 'backend'
# skills = 'python, flask'

# print(run_skill_gap_pipeline(role, skills, model, role_skill_freq, skill_embeddings, all_skills, client))