import difflib


PROJECTS = [
    # DATA ANALYST / ANALYTICS
    {"name": "Sales Analytics Dashboard", "category": "data analytics", "roles": ["data analyst"], "skills": ["sql", "python", "pandas", "data visualization", "powerbi"], "difficulty": "beginner", "impact": "high", "description": "Analyze sales data and present business insights in an interactive dashboard."},
    {"name": "Customer Segmentation Analysis", "category": "data analytics", "roles": ["data analyst"], "skills": ["python", "pandas", "clustering", "data visualization"], "difficulty": "intermediate", "impact": "high", "description": "Segment customers and explain which groups deserve the highest business focus."},
    {"name": "Marketing Campaign Performance Analysis", "category": "data analytics", "roles": ["data analyst"], "skills": ["sql", "python", "statistics", "data visualization"], "difficulty": "intermediate", "impact": "high", "description": "Evaluate campaign performance and show which channels produce the best ROI."},
    {"name": "Website Traffic Analytics", "category": "data analytics", "roles": ["data analyst"], "skills": ["python", "pandas", "data visualization"], "difficulty": "beginner", "impact": "medium", "description": "Analyze traffic patterns and user behavior from website data."},
    {"name": "Executive KPI Dashboard", "category": "data analytics", "roles": ["data analyst"], "skills": ["sql", "excel", "tableau", "business intelligence"], "difficulty": "intermediate", "impact": "high", "description": "Build an executive dashboard that summarizes core business KPIs."},
    {"name": "Forecasting Demand Report", "category": "data analytics", "roles": ["data analyst"], "skills": ["python", "excel", "statistics", "data visualization"], "difficulty": "intermediate", "impact": "high", "description": "Create a forecasting report to estimate future demand trends."},
    {"name": "Operations Performance Dashboard", "category": "data analytics", "roles": ["data analyst"], "skills": ["sql", "powerbi", "excel", "data visualization"], "difficulty": "beginner", "impact": "medium", "description": "Track operational bottlenecks and highlight improvement opportunities."},
    {"name": "Retention Cohort Analysis", "category": "data analytics", "roles": ["data analyst"], "skills": ["sql", "python", "pandas", "statistics"], "difficulty": "intermediate", "impact": "high", "description": "Analyze user retention patterns and identify drop-off stages."},

    # DATA SCIENCE / ML
    {"name": "Customer Churn Prediction", "category": "data science", "roles": ["data analyst"], "skills": ["python", "machine learning", "pandas", "scikit-learn"], "difficulty": "intermediate", "impact": "high", "description": "Build a model to predict which customers are at risk of leaving."},
    {"name": "Fraud Detection System", "category": "data science", "roles": ["data analyst"], "skills": ["python", "machine learning", "anomaly detection"], "difficulty": "advanced", "impact": "high", "description": "Detect suspicious transactions using anomaly detection techniques."},
    {"name": "Recommendation System", "category": "data science", "roles": ["data analyst", "backend"], "skills": ["python", "machine learning", "recommender system"], "difficulty": "advanced", "impact": "high", "description": "Build a recommendation engine for products or content."},

    # BACKEND
    {"name": "REST API for E-commerce", "category": "backend", "roles": ["backend"], "skills": ["python", "fastapi", "api", "database"], "difficulty": "intermediate", "impact": "high", "description": "Design a production-style REST API for an e-commerce platform."},
    {"name": "Authentication System", "category": "backend", "roles": ["backend"], "skills": ["python", "jwt", "api", "security"], "difficulty": "intermediate", "impact": "high", "description": "Implement authentication, authorization, and secure session handling."},
    {"name": "Microservices Architecture Demo", "category": "backend", "roles": ["backend"], "skills": ["docker", "api", "microservices"], "difficulty": "advanced", "impact": "high", "description": "Build a small microservices system with service-to-service communication."},
    {"name": "Inventory Management API", "category": "backend", "roles": ["backend"], "skills": ["node.js", "sql", "api", "docker"], "difficulty": "intermediate", "impact": "high", "description": "Build an inventory backend with CRUD, validation, and deployment-ready structure."},
    {"name": "Task Queue Notification Service", "category": "backend", "roles": ["backend"], "skills": ["node.js", "redis", "api", "docker"], "difficulty": "advanced", "impact": "high", "description": "Build a background job service for notifications and async workloads."},
    {"name": "Payment Service Sandbox", "category": "backend", "roles": ["backend"], "skills": ["node.js", "security", "api", "sql"], "difficulty": "advanced", "impact": "high", "description": "Simulate a payment service with logging, validation, and transaction flow."},
    {"name": "Spring Boot REST API", "category": "backend", "roles": ["backend"], "skills": ["java", "spring boot", "api", "database"], "difficulty": "intermediate", "impact": "high", "description": "Build a robust REST API using Java Spring Boot."},
    {"name": "Java Banking System", "category": "backend", "roles": ["backend"], "skills": ["java", "oop", "database"], "difficulty": "beginner", "impact": "medium", "description": "Create a simple banking management system with core business logic."},
    {"name": "Distributed Microservices with Spring", "category": "backend", "roles": ["backend"], "skills": ["java", "spring boot", "microservices", "docker"], "difficulty": "advanced", "impact": "high", "description": "Build distributed services using Spring and containerized deployment."},
    {"name": "ASP.NET Web API", "category": "backend", "roles": ["backend"], "skills": ["c#", ".net", "api", "database"], "difficulty": "intermediate", "impact": "high", "description": "Build a REST API with ASP.NET and structured data access."},
    {"name": "High Performance REST API", "category": "backend", "roles": ["backend"], "skills": ["go", "api", "database"], "difficulty": "intermediate", "impact": "high", "description": "Create a high-performance API service using Go."},
    {"name": "Laravel Blog Platform", "category": "backend", "roles": ["backend"], "skills": ["php", "laravel", "database"], "difficulty": "intermediate", "impact": "high", "description": "Build a blogging platform with Laravel and database integration."},
    {"name": "Backend Log Monitoring Tool", "category": "backend", "roles": ["backend"], "skills": ["python", "bash", "docker", "monitoring"], "difficulty": "intermediate", "impact": "medium", "description": "Create a tool to collect and inspect backend logs for debugging and monitoring."},

    # FRONTEND
    {"name": "Personal Portfolio Website", "category": "frontend", "roles": ["frontend"], "skills": ["html", "css", "javascript"], "difficulty": "beginner", "impact": "medium", "description": "Build a polished personal portfolio website to present projects and skills."},
    {"name": "Interactive Data Dashboard", "category": "frontend", "roles": ["frontend"], "skills": ["javascript", "react", "data visualization"], "difficulty": "intermediate", "impact": "high", "description": "Create an interactive dashboard with charts and rich front-end behavior."},
    {"name": "Task Management App UI", "category": "frontend", "roles": ["frontend"], "skills": ["react", "ui design", "javascript"], "difficulty": "intermediate", "impact": "high", "description": "Design and build a usable task management interface."},
    {"name": "Landing Page Optimization Project", "category": "frontend", "roles": ["frontend"], "skills": ["html", "css", "javascript", "webpack"], "difficulty": "beginner", "impact": "medium", "description": "Build and optimize a fast marketing landing page."},
    {"name": "React TypeScript Dashboard", "category": "frontend", "roles": ["frontend"], "skills": ["typescript", "react", "dashboard"], "difficulty": "intermediate", "impact": "high", "description": "Build a scalable dashboard using React and TypeScript."},
    {"name": "Vue Commerce Frontend", "category": "frontend", "roles": ["frontend"], "skills": ["vue", "javascript", "css", "api"], "difficulty": "intermediate", "impact": "high", "description": "Create a responsive storefront frontend powered by API data."},
    {"name": "Design System Starter", "category": "frontend", "roles": ["frontend"], "skills": ["typescript", "css", "storybook", "react"], "difficulty": "advanced", "impact": "high", "description": "Build a reusable design system with documented UI components."},
    {"name": "Frontend Performance Audit", "category": "frontend", "roles": ["frontend"], "skills": ["javascript", "webpack", "vite", "performance"], "difficulty": "intermediate", "impact": "medium", "description": "Improve loading performance and bundle efficiency on a real-style frontend app."},

    # FULLSTACK / DEVOPS / CLOUD
    {"name": "Fullstack Blog Platform", "category": "fullstack", "roles": ["frontend", "backend"], "skills": ["react", "nodejs", "database", "api"], "difficulty": "intermediate", "impact": "high", "description": "Build a fullstack blog platform with content workflows."},
    {"name": "E-commerce Website", "category": "fullstack", "roles": ["frontend", "backend"], "skills": ["react", "nodejs", "database"], "difficulty": "advanced", "impact": "high", "description": "Build an e-commerce application with product, cart, and checkout flows."},
    {"name": "CI/CD Pipeline Project", "category": "devops", "roles": ["backend"], "skills": ["docker", "github actions", "ci/cd"], "difficulty": "advanced", "impact": "high", "description": "Automate testing and deployment with a CI/CD pipeline."},
    {"name": "Dockerized Web Application", "category": "devops", "roles": ["backend", "frontend"], "skills": ["docker", "deployment"], "difficulty": "intermediate", "impact": "high", "description": "Containerize a web application and prepare it for deployment."},
    {"name": "Serverless API", "category": "cloud", "roles": ["backend"], "skills": ["aws", "serverless", "api"], "difficulty": "intermediate", "impact": "high", "description": "Build a serverless API with scalable cloud infrastructure."},
]


ROLE_CATEGORY_BOOSTS = {
    "frontend": {"frontend": 0.25, "fullstack": 0.1, "devops": 0.05},
    "backend": {"backend": 0.25, "fullstack": 0.1, "devops": 0.08, "cloud": 0.08},
    "data analyst": {"data analytics": 0.25, "data science": 0.12},
}


def get_all_skills():
    skill_set = set()
    for project in PROJECTS:
        for skill in project["skills"]:
            skill_set.add(skill.lower())
    return list(skill_set)


def correct_skill(skill, skill_list):
    skill = skill.lower().strip()
    match = difflib.get_close_matches(skill, skill_list, n=1, cutoff=0.6)
    if match:
        return match[0]
    return skill


def normalize_user_skills(user_skills):
    all_skills = get_all_skills()
    corrected = []
    for skill in user_skills:
        corrected.append(correct_skill(skill, all_skills))
    return corrected


def recommend_projects(user_skills, target_role=None, limit=6):
    """Return portfolio project references ranked by skill overlap and role fit."""
    user_skills_normalized = normalize_user_skills(user_skills)
    user_skill_set = set(user_skills_normalized)
    role_key = (target_role or "").lower().strip()
    category_boosts = ROLE_CATEGORY_BOOSTS.get(role_key, {})

    results = []
    for project in PROJECTS:
        project_skills = [s.lower() for s in project["skills"]]
        project_skill_set = set(project_skills)
        matched = sorted(user_skill_set & project_skill_set)
        match_count = len(matched)
        if match_count == 0:
            continue

        base_score = match_count / len(project_skills)
        role_bonus = category_boosts.get(project["category"], 0.0)
        impact_bonus = 0.05 if project.get("impact") == "high" else 0.0
        score = min(1.0, round(base_score + role_bonus + impact_bonus, 2))

        results.append(
            {
                "name": project["name"],
                "category": project["category"],
                "difficulty": project["difficulty"],
                "description": project["description"],
                "score": score,
                "match_count": match_count,
                "skills_matched": matched,
                "skills_required": project_skills,
            }
        )

    results.sort(
        key=lambda item: (
            item["score"],
            item["match_count"],
            len(item["skills_matched"]),
        ),
        reverse=True,
    )
    return results[:limit]
