import re

class Normalize_Input():
    COMBINED_SKILLS = {
    "html css": ["html", "css"],
    "python django": ["python","django"],
    "docker kubernetes": ["docker","kubernetes"],
    "c c++": ["c", "c++"]
}
    skill_alias = {
    "py": "python",
    "python3": "python",
    "python 3": "python",
    "py3" : "python",
    "python3" : "python",
    "django rest" : "django_rest_framework",
    "django rest framework": "django_rest_framework",
    "drf": "django_rest_framework",
    "flask api": "flask",
    "fast api": "fastapi",
    "fast-api": "fastapi",
    "node": "node.js",
    "nodejs": "node.js",
    "node js": "node.js",
    "node-js": "node.js",
    "reactjs": "react",
    "react js": "react",
    "nextjs": "next.js",
    "next js": "next.js",
    "vue.js": "vue",
    "vuejs": "vue",
    "vue js": "vue",
    "angularjs": "angular",
    "angular js": "angular",
    "angular.js": "angular",
    "js": "javascript",
    "ts": "typescript",
    "postgres": "postgresql",
    "postgre": "postgresql",
    "psql": "postgresql",
    "postgre_sql": "postgresql",
    "postgre-sql": "postgresql",
    "postgre sql": "postgresql",
    "my sql": "mysql",
    "my_sql": "mysql",
    "my-sql": "mysql",
    "mongo": "mongodb",
    "mongo_db": "mongodb",
    "mongo-db": "mongodb",
    "mongo db": "mongodb",
    "ms sql": "sql_server",
    "mssql": "sql_server",
    "sql server": "sql_server",
    "t sql": "t-sql",
    "power bi": "power_bi",
    "power-bi": "power_bi",
    "powerbi": "power_bi",
    "ms excel": "excel",
    "advanced excel": "excel",
    "google sheet": "google_sheets",
    "google sheets": "google_sheets",
    "machine learning": "machine_learning",
    "ml": "machine_learning",
    "data analysis": "data_analysis",
    "data analytics": "data_analysis",
    "data visualization": "data_visualization",
    "data viz": "data_visualization",
    "statistical analysis": "statistics",
    "stats": "statistics",
    "business_process_analysis": "business_analysis",
    "business process analysis": "business_analysis",
    "aws cloud": "aws",
    "amazon web services": "aws",
    "gcp": "google_cloud",
    "google cloud platform": "google_cloud",
    "azure cloud": "azure",
    "gitlab": "git",
    "github": "git",
    "bitbucket": "git",
    "c sharp": "c#",
    "c-sharp": "c#",
    "dotnet": ".net",
    "asp net": "asp.net",
    "asp.net core": "asp.net",
    "bash shell": "bash",
    "bash shell all shells": "bash",
    "bash shell  all shells": "bash",
    "all shells": "bash",
    "maven build tool": "maven",
    "ms sql server": "mysql",
    "databases": "database",
    "tf": "tensorflow",
    "tensorflow2": "tensorflow",
    "tensorflow framework": "tensorflow",
    "scikit learn": "scikit-learn",
    "pandas library": "pandas",
    "pandas package": "pandas",
    "python pandas": "pandas",
    "numpy library": "numpy",
    "numpy package": "numpy",
    "python numpy": "numpy",
    "matplotlib library": "matplotlib",
    "matplotlib package": "matplotlib",
    "python matplotlib": "matplotlib",
    "aws cloud services": "aws",
    "amazon aws": "aws",
    "amazon web service": "aws",
    "aws services": "aws",
    "tensorflow 2": "tensorflow",
    "pytorch framework": "pytorch",
    "torch": "pytorch",
    "sklearn": "scikit-learn",
    "scikit learn library": "scikit-learn",
    "docker container": "docker",
    "docker containers": "docker",
    "k8s": "kubernetes",
    "kubernetes cluster": "kubernetes",
    "crm": "crm systems",
    "crystal": "crystal reports",
    "css3": "css",
}
    
    BLACKLIST_PATTERNS = [
    r"\byears?\b",
    r"\bdegree\b",
    r"\bbachelor\b",
    r"\bmaster\b",
    r"\bphd\b",
    r"\bexperience\b",
    'acd'
]


    def __init__(self, user_skills):
        self.user_skills = user_skills

    def normalize_skill_text(self):

        self.user_skills = self.user_skills.lower()

        # remove years experience
        self.user_skills = re.sub(r"\d+\+?\s*(years?|yrs?)\s*(of)?\s*(experience|exp)?", "", self.user_skills)

        # remove role words
        role_words = ["developer","engineer","specialist","framework"]
        for word in role_words:
            self.user_skills = self.user_skills.replace(word,"")

        # remove seniority
        seniority = ["junior","jr","senior","sr","lead","principal","staff"]
        for word in seniority:
            self.user_skills = self.user_skills.replace(word,"")

        # remove phrases
        phrases = [
            "experience with","experience in","knowledge of",
            "understanding of","familiar with","proficiency in"
        ]
        for p in phrases:
            self.user_skills = self.user_skills.replace(p,"")

        # parentheses
        self.user_skills = self.user_skills.replace("(", ",")
        self.user_skills = self.user_skills.replace(")", "")

        # normalize separators
        self.user_skills = re.sub(r"[\/&|]", ",", self.user_skills)
        self.user_skills = re.sub(r"\band\b", ",", self.user_skills)
        self.user_skills = re.sub(r"-", ",", self.user_skills)

        # punctuation
        self.user_skills = re.sub(r"[;:.]", ",", self.user_skills)

        # remove etc
        self.user_skills = self.user_skills.replace("etc.", "")
        self.user_skills = self.user_skills.replace("etc", "")

        # remove duplicate comma
        self.user_skills = re.sub(r",+", ",", self.user_skills)

        self.user_skills = re.sub(r"\s+", " ", self.user_skills)

        return self.user_skills.strip()
    
    def clean_skill_function(self):
        split_skills = [i.strip().lower() for i in self.user_skills.split(',') if i.strip()]
        
        self.list_skills = []
        for skill in split_skills:
            if skill in self.COMBINED_SKILLS:
                self.list_skills.extend(self.COMBINED_SKILLS[skill])  # pecah jadi beberapa
            else:
                self.list_skills.append(skill)
        
        return self.list_skills

    def remove_soft_skills(self):
        soft_skills = [
            "communication","verbal","written","listening","negotiation","persuasion","public speaking",
            "teamwork","team player","collaboration","cross functional","cross-functional",
            "leadership","stakeholder","people",
            "time management",
            "problem solving","problem-solving","troubleshooting",
            "adaptability","adaptable","flexibility",
            "creativity",
            "thinking","critical thinking","analytical","strategic thinking",
            "attention to detail","detail oriented",
            "organizational","organization",
            "interpersonal","relationship",
            "work ethic","days", "$"
            "self motivated","self-motivated","self starter","self-starter",
            "fast learner","quick learner","willingness to learn","continuous learning",
            "multitasking","multitask",
            "decision making","decision-making",
            "presentation","presentation skills",
            "initiative","proactive",
            "responsible","accountability","ownership",
            "prioritization","planning","coordination", "advance", "advanced"
        ]
        
        self.final_skills = []
        
        for skill in self.list_skills:
            if not any(keyword in skill for keyword in soft_skills):
                self.final_skills.append(skill)
                
        return self.final_skills
    
    def normalize_skill_list(self):
        self.norm_skills =  list(dict.fromkeys(self.skill_alias.get(s, s) for s in self.final_skills))
        return self.norm_skills

    def remove_noise(self):
        clean = []
        for s in self.norm_skills:
            if not any(re.search(p, s) for p in self.BLACKLIST_PATTERNS):
                clean.append(s)
        return clean
    
    def run_Class(self):
        self.normalize_skill_text()
        self.clean_skill_function()
        self.remove_soft_skills()
        self.normalize_skill_list()
        return self.remove_noise()

