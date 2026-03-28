import difflib

projects = [
    # DATA ANALYTICS
    {"name":"Sales Analytics Dashboard","category":"data analytics","skills":["sql","python","pandas","data visualization","powerbi"],"difficulty":"beginner","impact":"high","description":"Analyze company sales data and build an interactive dashboard."},
    {"name":"Customer Segmentation Analysis","category":"data analytics","skills":["python","pandas","clustering","data visualization"],"difficulty":"intermediate","impact":"high","description":"Segment customers using clustering algorithms."},
    {"name":"Marketing Campaign Performance Analysis","category":"data analytics","skills":["sql","python","statistics","data visualization"],"difficulty":"intermediate","impact":"high","description":"Analyze marketing campaign performance and ROI."},
    {"name":"Website Traffic Analytics","category":"data analytics","skills":["python","pandas","data visualization"],"difficulty":"beginner","impact":"medium","description":"Analyze website traffic data to understand user behavior."},
    
    # DATA SCIENCE
    {"name":"Customer Churn Prediction","category":"data science","skills":["python","machine learning","pandas","scikit-learn"],"difficulty":"intermediate","impact":"high","description":"Predict customers likely to leave a service."},
    {"name":"Fraud Detection System","category":"data science","skills":["python","machine learning","anomaly detection"],"difficulty":"advanced","impact":"high","description":"Detect fraudulent transactions using ML."},
    {"name":"Credit Risk Prediction","category":"data science","skills":["python","machine learning","statistics"],"difficulty":"advanced","impact":"high","description":"Predict credit risk for loan approval."},
    {"name":"Recommendation System","category":"data science","skills":["python","machine learning","recommender system"],"difficulty":"advanced","impact":"high","description":"Build a collaborative filtering recommendation engine."},
    
    # MACHINE LEARNING / AI
    {"name":"Image Classification CNN","category":"machine learning","skills":["python","deep learning","pytorch","cnn"],"difficulty":"advanced","impact":"high","description":"Build CNN models to classify images."},
    {"name":"Object Detection System","category":"machine learning","skills":["python","computer vision","deep learning"],"difficulty":"advanced","impact":"high","description":"Detect objects in images using YOLO."},
    {"name":"Sentiment Analysis NLP","category":"machine learning","skills":["python","nlp","machine learning"],"difficulty":"intermediate","impact":"high","description":"Analyze sentiment from social media data."},
    {"name":"AI Chatbot with LLM","category":"ai","skills":["python","nlp","llm"],"difficulty":"intermediate","impact":"high","description":"Build an AI chatbot using LLM."},
    {"name":"RAG Document Search System","category":"ai","skills":["python","rag","vector database"],"difficulty":"advanced","impact":"high","description":"Build a retrieval augmented generation system."},
    
    # BACKEND DEVELOPMENT
    {"name":"REST API for E-commerce","category":"backend","skills":["python","fastapi","api","database"],"difficulty":"intermediate","impact":"high","description":"Build a REST API for an e-commerce platform."},
    {"name":"Authentication System","category":"backend","skills":["python","jwt","api","security"],"difficulty":"intermediate","impact":"high","description":"Implement authentication and authorization system."},
    {"name":"Microservices Architecture Demo","category":"backend","skills":["docker","api","microservices"],"difficulty":"advanced","impact":"high","description":"Build microservices-based backend system."},
    
    # FRONTEND DEVELOPMENT
    {"name":"Interactive Data Dashboard","category":"frontend","skills":["javascript","react","data visualization"],"difficulty":"intermediate","impact":"high","description":"Create interactive dashboards using React."},
    {"name":"Personal Portfolio Website","category":"frontend","skills":["html","css","javascript"],"difficulty":"beginner","impact":"medium","description":"Build a personal developer portfolio website."},
    {"name":"Task Management App UI","category":"frontend","skills":["react","ui design","javascript"],"difficulty":"intermediate","impact":"high","description":"Build a task management application interface."},
    
    # FULLSTACK DEVELOPMENT
    {"name":"Fullstack Blog Platform","category":"fullstack","skills":["react","nodejs","database","api"],"difficulty":"intermediate","impact":"high","description":"Build a fullstack blogging platform."},
    {"name":"E-commerce Website","category":"fullstack","skills":["react","nodejs","database"],"difficulty":"advanced","impact":"high","description":"Build an e-commerce website with shopping cart."},
    
    # DEVOPS
    {"name":"CI/CD Pipeline Project","category":"devops","skills":["docker","github actions","ci/cd"],"difficulty":"advanced","impact":"high","description":"Build automated CI/CD pipeline."},
    {"name":"Dockerized Web Application","category":"devops","skills":["docker","deployment"],"difficulty":"intermediate","impact":"high","description":"Containerize web applications using Docker."},
    
    # CLOUD
    {"name":"Deploy ML Model on Cloud","category":"cloud","skills":["aws","mlops","deployment"],"difficulty":"advanced","impact":"high","description":"Deploy machine learning models on AWS."},
    {"name":"Serverless API","category":"cloud","skills":["aws","serverless","api"],"difficulty":"intermediate","impact":"high","description":"Build serverless backend APIs."},
    
    # CYBERSECURITY
    {"name":"Password Strength Analyzer","category":"cybersecurity","skills":["python","security"],"difficulty":"beginner","impact":"medium","description":"Build a tool to analyze password strength."},
    {"name":"Network Intrusion Detection","category":"cybersecurity","skills":["python","machine learning","network security"],"difficulty":"advanced","impact":"high","description":"Detect network intrusion using ML."},
    
    # MOBILE DEVELOPMENT
    {"name":"To-do List Mobile App","category":"mobile","skills":["flutter","mobile development"],"difficulty":"beginner","impact":"medium","description":"Build a simple to-do list mobile application."},
    {"name":"Fitness Tracking App","category":"mobile","skills":["flutter","mobile ui"],"difficulty":"intermediate","impact":"high","description":"Build a fitness tracking mobile application."},
    
    # JAVA DEVELOPMENT
    {"name":"Spring Boot REST API","category":"backend","skills":["java","spring boot","api","database"],"difficulty":"intermediate","impact":"high","description":"Build a REST API using Java Spring Boot."},
    {"name":"Java Banking System","category":"backend","skills":["java","oop","database"],"difficulty":"beginner","impact":"medium","description":"Build a simple banking management system in Java."},
    {"name":"Distributed Microservices with Spring","category":"backend","skills":["java","spring boot","microservices","docker"],"difficulty":"advanced","impact":"high","description":"Build distributed microservices architecture using Spring."},
    
    # KOTLIN DEVELOPMENT
    {"name":"Android Notes App","category":"mobile","skills":["kotlin","android","mobile development"],"difficulty":"beginner","impact":"medium","description":"Build a simple Android notes application."},
    {"name":"Kotlin Weather App","category":"mobile","skills":["kotlin","android","api"],"difficulty":"intermediate","impact":"high","description":"Create a weather forecast Android application."},
    {"name":"Kotlin Chat Application","category":"mobile","skills":["kotlin","android","firebase"],"difficulty":"advanced","impact":"high","description":"Build real-time chat application using Kotlin."},
    
    # C++ DEVELOPMENT
    {"name":"File Compression Tool","category":"systems programming","skills":["c++","algorithms","data structures"],"difficulty":"advanced","impact":"high","description":"Build a file compression tool using Huffman coding."},
    {"name":"2D Game Engine Prototype","category":"game development","skills":["c++","graphics","game development"],"difficulty":"advanced","impact":"high","description":"Build a simple 2D game engine in C++."},
    {"name":"Command Line File Manager","category":"systems programming","skills":["c++","filesystem","cli"],"difficulty":"intermediate","impact":"medium","description":"Build a command line file manager."},
    
    # C# / .NET DEVELOPMENT
    {"name":"ASP.NET Web API","category":"backend","skills":["c#",".net","api","database"],"difficulty":"intermediate","impact":"high","description":"Build a REST API using ASP.NET."},
    {"name":"Inventory Management System","category":"backend","skills":["c#",".net","database"],"difficulty":"beginner","impact":"medium","description":"Build an inventory management system."},
    {"name":"Real-time Chat App with SignalR","category":"backend","skills":["c#",".net","signalr"],"difficulty":"advanced","impact":"high","description":"Build a real-time chat application."},
    
    # GO (GOLANG)
    {"name":"High Performance REST API","category":"backend","skills":["go","api","database"],"difficulty":"intermediate","impact":"high","description":"Build a high performance REST API using Go."},
    {"name":"Concurrent Web Crawler","category":"backend","skills":["go","concurrency","web scraping"],"difficulty":"advanced","impact":"high","description":"Build a multi-threaded web crawler."},
    {"name":"CLI DevOps Tool","category":"devops","skills":["go","cli","devops"],"difficulty":"intermediate","impact":"medium","description":"Build a CLI tool for DevOps automation."},
    
    # RUST
    {"name":"High Performance Web Server","category":"backend","skills":["rust","systems programming"],"difficulty":"advanced","impact":"high","description":"Build a high performance web server in Rust."},
    {"name":"Memory Safe File Processor","category":"systems programming","skills":["rust","file processing"],"difficulty":"intermediate","impact":"medium","description":"Build a memory-safe file processing tool."},
    
    # PHP
    {"name":"Laravel Blog Platform","category":"backend","skills":["php","laravel","database"],"difficulty":"intermediate","impact":"high","description":"Build a blog platform using Laravel."},
    {"name":"PHP Authentication System","category":"backend","skills":["php","authentication","database"],"difficulty":"beginner","impact":"medium","description":"Build login and authentication system."},
    
    # TYPESCRIPT
    {"name":"TypeScript Web App","category":"frontend","skills":["typescript","javascript","web development"],"difficulty":"beginner","impact":"medium","description":"Build a web application using TypeScript."},
    {"name":"React TypeScript Dashboard","category":"frontend","skills":["typescript","react","dashboard"],"difficulty":"intermediate","impact":"high","description":"Build a scalable dashboard with React and TypeScript."},
    
    # SWIFT (iOS)
    {"name":"iOS Todo App","category":"mobile","skills":["swift","ios","mobile development"],"difficulty":"beginner","impact":"medium","description":"Build a simple iOS to-do list app."},
    {"name":"iOS Health Tracker","category":"mobile","skills":["swift","ios","healthkit"],"difficulty":"advanced","impact":"high","description":"Build a health tracking application."},
    
    # GAME DEVELOPMENT
    {"name":"Unity 2D Platformer Game","category":"game development","skills":["unity","c#","game development"],"difficulty":"intermediate","impact":"high","description":"Build a 2D platformer game using Unity."},
    {"name":"Multiplayer Online Game Prototype","category":"game development","skills":["unity","networking","c#"],"difficulty":"advanced","impact":"high","description":"Build a multiplayer game prototype."}
]

def get_all_skills():
    skill_set = set()
    for project in projects:
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
        fixed = correct_skill(skill, all_skills)
        corrected.append(fixed)
    return corrected

def recommend_projects(user_skills, limit=3):
    """
    Given a list of user skills, return the top matching projects.
    Returns highly curated top generic projects (default limit=3 to fit nicely in UI layout).
    """
    user_skills_normalized = normalize_user_skills(user_skills)
    results = []
    for project in projects:
        project_skills = [s.lower() for s in project["skills"]]
        match = len(set(user_skills_normalized) & set(project_skills))
        score = match / len(project_skills)
        if score > 0:
            results.append({
                "name": project["name"],
                "category": project["category"],
                "difficulty": project["difficulty"],
                "description": project["description"],
                "score": round(score, 2),
                "skills_matched": list(set(user_skills_normalized) & set(project_skills)),
                "skills_required": project_skills
            })
            
    # Sort projects by Highest Match Score first.
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]
