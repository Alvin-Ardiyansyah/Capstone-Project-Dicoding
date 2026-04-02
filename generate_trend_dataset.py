"""
Generate a clean, evenly-distributed skill trend dataset
using the Ornstein-Uhlenbeck process from the ARIMA team's approach.
Each skill gets a consistent number of job postings per month,
following realistic trend directions (NAIK/STABIL/TURUN).
"""
import pandas as pd
import numpy as np

# Trend map from teammate's ARIMA research
TREND_MAP = {
    'pytorch': 'NAIK', 'tensorflow': 'STABIL', 'aws': 'TURUN', 'c++': 'STABIL',
    'gcp': 'STABIL', 'cuda': 'NAIK', 'r': 'STABIL', 'hugging face': 'NAIK',
    'flask': 'NAIK', 'scikit-learn': 'STABIL', 'fastapi': 'NAIK', 'pandas': 'STABIL',
    'azure': 'STABIL', 'numpy': 'STABIL', 'excel': 'STABIL', 'keras': 'STABIL',
    'python': 'NAIK', 'power bi': 'NAIK', 'mlflow': 'NAIK', 'langchain': 'NAIK',
    'reinforcement learning': 'NAIK', 'sql': 'STABIL', 'angular': 'TURUN',
    'javascript': 'STABIL', 'jquery': 'STABIL', 'react': 'NAIK',
    'typescript': 'NAIK', 'postgresql': 'STABIL', 'html': 'STABIL',
    'css': 'STABIL', 'webpack': 'STABIL', 'go': 'NAIK', 'java': 'STABIL',
    'vue': 'NAIK', 'kubernetes': 'NAIK', 'node.js': 'NAIK', 'tableau': 'STABIL',
    'spring boot': 'NAIK', 'php': 'STABIL', 'graphql': 'NAIK',
    # Additional skills from our existing vocab
    'docker': 'NAIK', 'mongodb': 'STABIL', 'redis': 'NAIK',
    'sass': 'STABIL', 'tailwind css': 'NAIK', 'bootstrap': 'STABIL',
    'figma': 'NAIK', 'git': 'STABIL', 'linux': 'STABIL',
    'express': 'STABIL', 'nestjs': 'NAIK', 'next': 'NAIK',
    'mysql': 'STABIL', 'oracle': 'STABIL',
}

SKILLS = list(TREND_MAP.keys())
MONTHS = pd.date_range(start='2023-09-01', end='2026-04-01', freq='MS')

np.random.seed(42)
rows = []

for skill in SKILLS:
    direction = TREND_MAP.get(skill, 'STABIL')
    base = np.random.uniform(8, 18)  # higher base for more realistic counts
    current = base

    for month in MONTHS:
        # Drift based on trend direction
        if direction == 'NAIK':
            drift = 0.15
        elif direction == 'TURUN':
            drift = -0.12
        else:
            drift = 0

        # Mean-reversion + noise (Ornstein-Uhlenbeck)
        reversion = -0.05 * (current - base)
        noise = np.random.normal(0, 0.3)
        current = current + drift + reversion + noise
        current = max(1, current)  # floor at 1, never zero

        count = np.random.poisson(lam=max(1, current))

        for _ in range(count):
            day = np.random.randint(1, 28)
            rows.append({
                'posting_date': month + pd.Timedelta(days=day),
                'skills_required': skill,
            })

df = pd.DataFrame(rows)
df = df.sort_values('posting_date').reset_index(drop=True)

# Save
output_path = 'modeling/data/skill_trend_dataset_combined.csv'
df.to_csv(output_path, index=False)

# Verification
df['month'] = df['posting_date'].dt.to_period('M')
monthly = df.groupby('month').size()
per_skill = df.groupby(['month', 'skills_required']).size().reset_index(name='count')

print(f"Total rows: {len(df)}")
print(f"Unique skills: {df['skills_required'].nunique()}")
print(f"Date range: {df['posting_date'].min()} to {df['posting_date'].max()}")
print(f"\nMonthly totals (first 5 / last 5):")
for p in list(monthly.index[:5]) + ['...'] + list(monthly.index[-5:]):
    if p == '...':
        print('  ...')
    else:
        print(f"  {p}: {monthly[p]}")

# Check a few skills
for check_skill in ['react', 'jquery', 'node.js', 'java', 'css']:
    s = per_skill[per_skill['skills_required'] == check_skill]
    print(f"\n{check_skill}: min={s['count'].min()}, max={s['count'].max()}, mean={s['count'].mean():.1f}")

print(f"\nSaved to {output_path}")
