"""
CogniMap — Reference data definitions.
This module hand-defines branches, skills, careers, and the course catalog
with deliberate, logically-consistent structure (not random) so that:
  - branch-relevant courses actually correlate with branch-relevant skills/careers
  - prerequisite chains are real and resolvable
  - some courses are deliberately SHARED across branches (for credit-overlap testing)
"""

# ---------------------------------------------------------------------------
# 1. BRANCHES / SPECIALIZATIONS
# ---------------------------------------------------------------------------
BRANCHES = [
    dict(branch_id="CSE", branch_name="Computer Science and Engineering",
         description="Core computing: algorithms, systems, software engineering.",
         core_domains="Programming|Algorithms|Systems|Software Engineering"),
    dict(branch_id="AIML", branch_name="Artificial Intelligence and Machine Learning",
         description="AI/ML theory and applied model-building.",
         core_domains="Machine Learning|Deep Learning|AI|Statistics"),
    dict(branch_id="AIDS", branch_name="Artificial Intelligence and Data Science",
         description="Data-centric analytics, statistics, and applied ML.",
         core_domains="Data Science|Statistics|Machine Learning|Data Engineering"),
    dict(branch_id="IT", branch_name="Information Technology",
         description="Applied software, networks, databases, enterprise systems.",
         core_domains="Networking|Databases|Web Systems|Cloud"),
    dict(branch_id="CYSEC", branch_name="Cyber Security",
         description="Security, networking defense, ethical hacking, cryptography.",
         core_domains="Security|Networking|Cryptography|Systems"),
    dict(branch_id="CSBS", branch_name="Computer Science and Business Systems",
         description="CS fundamentals blended with business/analytics applications.",
         core_domains="Business Analytics|Software|Management|Data"),
    dict(branch_id="IOT", branch_name="IoT and Embedded Systems",
         description="Embedded programming, hardware-software integration, IoT platforms.",
         core_domains="Embedded Systems|IoT|Networking|Hardware"),
]
BRANCH_IDS = [b["branch_id"] for b in BRANCHES]

# ---------------------------------------------------------------------------
# 2. SKILLS TAXONOMY
# ---------------------------------------------------------------------------
SKILLS = [
    "Python", "Java", "C++", "C", "JavaScript", "SQL",
    "Data Structures", "Algorithms", "DBMS", "Operating Systems", "Distributed Systems",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Statistics",
    "Data Analytics", "Data Engineering", "Business Analytics",
    "Cloud Computing", "Networking", "Cyber Security", "Cryptography", "Ethical Hacking",
    "Web Development", "Frontend Development", "Backend Development", "DevOps",
    "IoT", "Embedded Systems", "Hardware Design", "Software Testing", "Software Engineering",
]

# ---------------------------------------------------------------------------
# 3. COURSE CATALOG
#    Each course: name, credits, semester, prereq (by name, resolved later),
#    skills taught (subset of SKILLS), difficulty (1-5), category,
#    and which branch(es) require / offer it as elective.
#    branches: dict of branch_id -> "core" | "elective"
# ---------------------------------------------------------------------------

COMMON_CORE = [
    # name, credits, semester, prereq, skills, difficulty
    ("Programming Fundamentals (C)", 4, 1, None, ["C", "Data Structures"], 2),
    ("Discrete Mathematics", 3, 1, None, ["Algorithms"], 3),
    ("Linear Algebra & Calculus", 3, 1, None, ["Statistics"], 2),
    ("Digital Logic Design", 3, 2, None, ["Hardware Design"], 3),
    ("Data Structures", 4, 2, "Programming Fundamentals (C)", ["Data Structures", "Algorithms", "C"], 3),
    ("Probability & Statistics", 3, 2, "Linear Algebra & Calculus", ["Statistics"], 3),
    ("Object Oriented Programming (Java)", 4, 3, "Programming Fundamentals (C)", ["Java", "Software Engineering"], 3),
    ("Database Management Systems", 4, 3, "Data Structures", ["DBMS", "SQL"], 3),
    ("Web Technologies", 3, 3, "Programming Fundamentals (C)", ["Web Development", "JavaScript", "Frontend Development"], 2),
    ("Design & Analysis of Algorithms", 4, 4, "Data Structures", ["Algorithms", "Data Structures"], 4),
    ("Operating Systems", 4, 4, "Data Structures", ["Operating Systems", "C"], 4),
    ("Computer Networks", 4, 4, "Data Structures", ["Networking"], 3),
    ("Software Engineering", 3, 4, "Object Oriented Programming (Java)", ["Software Engineering", "Software Testing"], 2),
    ("Python for Applications", 3, 2, "Programming Fundamentals (C)", ["Python"], 2),
]

# Branch-specific courses. Some are deliberately duplicated across branches
# (identical name+definition) to create genuine, testable credit overlap.
BRANCH_COURSES = {
    "CSE": [
        ("Advanced Algorithms & Complexity", 4, 5, "Design & Analysis of Algorithms", ["Algorithms", "Data Structures"], 5, "core"),
        ("Compiler Design", 3, 6, "Advanced Algorithms & Complexity", ["Software Engineering", "C"], 5, "core"),
        ("Distributed Systems", 3, 6, "Operating Systems", ["Distributed Systems", "Networking"], 4, "core"),
        ("Software Architecture & Design Patterns", 3, 7, "Software Engineering", ["Software Engineering"], 4, "core"),
        ("Competitive Programming", 2, 5, "Design & Analysis of Algorithms", ["Algorithms", "Data Structures"], 4, "elective"),
        ("Cloud Native Systems", 3, 7, "Distributed Systems", ["Cloud Computing", "DevOps"], 4, "elective"),
        ("Capstone: Software Systems Project", 3, 8, "Software Architecture & Design Patterns", ["Software Engineering", "Backend Development"], 4, "core"),
    ],
    "AIML": [
        ("Introduction to Machine Learning", 4, 5, "Probability & Statistics", ["Machine Learning", "Python", "Statistics"], 4, "core"),
        ("Neural Networks & Deep Learning", 4, 6, "Introduction to Machine Learning", ["Deep Learning", "Machine Learning", "Python"], 5, "core"),
        ("Natural Language Processing", 3, 7, "Neural Networks & Deep Learning", ["NLP", "Deep Learning"], 5, "core"),
        ("Computer Vision", 3, 7, "Neural Networks & Deep Learning", ["Computer Vision", "Deep Learning"], 5, "core"),
        ("Reinforcement Learning", 3, 8, "Neural Networks & Deep Learning", ["Machine Learning", "Deep Learning"], 5, "elective"),
        ("AI Ethics & Explainability", 2, 8, "Introduction to Machine Learning", ["Machine Learning"], 2, "core"),
        ("Big Data Systems", 3, 6, "Database Management Systems", ["Data Engineering", "Cloud Computing"], 4, "elective"),
        ("Robotics Fundamentals", 3, 8, "Neural Networks & Deep Learning", ["Machine Learning", "Embedded Systems"], 4, "elective"),
    ],
    "AIDS": [
        ("Introduction to Machine Learning", 4, 5, "Probability & Statistics", ["Machine Learning", "Python", "Statistics"], 4, "core"),  # shared with AIML
        ("Statistical Data Analysis", 4, 5, "Probability & Statistics", ["Statistics", "Data Analytics"], 3, "core"),
        ("Data Engineering & ETL", 3, 6, "Database Management Systems", ["Data Engineering", "SQL", "Python"], 4, "core"),
        ("Data Visualization", 2, 6, "Statistical Data Analysis", ["Data Analytics"], 2, "core"),
        ("Big Data Systems", 3, 6, "Database Management Systems", ["Data Engineering", "Cloud Computing"], 4, "core"),  # shared with AIML
        ("Time Series Analysis", 3, 7, "Statistical Data Analysis", ["Statistics", "Data Analytics"], 4, "elective"),
        ("Data Science Capstone", 3, 8, "Data Engineering & ETL", ["Data Analytics", "Machine Learning"], 4, "core"),
    ],
    "IT": [
        ("Cloud Computing Fundamentals", 3, 5, "Computer Networks", ["Cloud Computing", "DevOps"], 3, "core"),
        ("Advanced Database Systems", 3, 5, "Database Management Systems", ["DBMS", "SQL"], 3, "core"),
        ("Enterprise Web Applications", 4, 6, "Web Technologies", ["Backend Development", "Web Development"], 4, "core"),
        ("IT Infrastructure & DevOps", 3, 6, "Cloud Computing Fundamentals", ["DevOps", "Cloud Computing"], 4, "core"),
        ("Network Administration", 3, 7, "Computer Networks", ["Networking"], 3, "core"),
        ("Mobile Application Development", 3, 7, "Enterprise Web Applications", ["Java", "Frontend Development"], 3, "elective"),
        ("IT Project Management", 2, 8, "Software Engineering", ["Software Engineering"], 2, "elective"),
    ],
    "CYSEC": [
        ("Cryptography Fundamentals", 3, 5, "Discrete Mathematics", ["Cryptography"], 4, "core"),
        ("Network Security", 4, 5, "Computer Networks", ["Cyber Security", "Networking"], 4, "core"),
        ("Ethical Hacking & Penetration Testing", 3, 6, "Network Security", ["Ethical Hacking", "Cyber Security"], 5, "core"),
        ("Security Operations & SOC", 3, 6, "Network Security", ["Cyber Security", "Networking"], 4, "core"),
        ("Malware Analysis", 3, 7, "Ethical Hacking & Penetration Testing", ["Cyber Security", "Software Testing"], 5, "elective"),
        ("Cyber Law & Governance", 2, 7, "Network Security", ["Cyber Security"], 2, "elective"),
        ("Security Capstone", 3, 8, "Ethical Hacking & Penetration Testing", ["Cyber Security", "Ethical Hacking"], 4, "core"),
    ],
    "CSBS": [
        ("Business Analytics", 3, 5, "Probability & Statistics", ["Business Analytics", "Data Analytics"], 3, "core"),
        ("Enterprise Resource Planning Systems", 3, 5, "Database Management Systems", ["Business Analytics", "SQL"], 3, "core"),
        ("Financial & Managerial Accounting", 3, 6, None, ["Business Analytics"], 2, "core"),
        ("Statistical Data Analysis", 4, 5, "Probability & Statistics", ["Statistics", "Data Analytics"], 3, "core"),  # shared with AIDS
        ("Product Management", 2, 7, "Software Engineering", ["Software Engineering", "Business Analytics"], 2, "core"),
        ("Introduction to Machine Learning", 4, 6, "Probability & Statistics", ["Machine Learning", "Python", "Statistics"], 4, "elective"),  # shared
        ("Business Systems Capstone", 3, 8, "Enterprise Resource Planning Systems", ["Business Analytics", "Software Engineering"], 3, "core"),
    ],
    "IOT": [
        ("Embedded Systems Programming", 4, 5, "Digital Logic Design", ["Embedded Systems", "C"], 4, "core"),
        ("Microcontrollers & Sensors", 3, 5, "Digital Logic Design", ["Embedded Systems", "Hardware Design"], 4, "core"),
        ("IoT Platforms & Protocols", 3, 6, "Embedded Systems Programming", ["IoT", "Networking"], 4, "core"),
        ("Wireless Sensor Networks", 3, 6, "Computer Networks", ["IoT", "Networking"], 4, "core"),
        ("Edge Computing", 3, 7, "IoT Platforms & Protocols", ["IoT", "Cloud Computing"], 4, "elective"),
        ("Robotics Fundamentals", 3, 7, "Embedded Systems Programming", ["Machine Learning", "Embedded Systems"], 4, "elective"),  # shared with AIML
        ("IoT Capstone", 3, 8, "IoT Platforms & Protocols", ["IoT", "Embedded Systems"], 4, "core"),
    ],
}

# ---------------------------------------------------------------------------
# 4. CAREERS
# ---------------------------------------------------------------------------
CAREERS = [
    dict(career_name="Software Engineer", related_specializations=["CSE", "IT"],
         required_skills=["Java", "Data Structures", "Algorithms", "Software Engineering"], demand_score=9),
    dict(career_name="Backend Developer", related_specializations=["CSE", "IT"],
         required_skills=["Backend Development", "DBMS", "SQL", "Java"], demand_score=8),
    dict(career_name="Systems Engineer", related_specializations=["CSE", "IT"],
         required_skills=["Operating Systems", "Networking", "C"], demand_score=7),
    dict(career_name="DevOps Engineer", related_specializations=["IT", "CSE"],
         required_skills=["DevOps", "Cloud Computing", "Networking"], demand_score=9),
    dict(career_name="Software Architect", related_specializations=["CSE"],
         required_skills=["Software Engineering", "Distributed Systems", "Algorithms"], demand_score=8),
    dict(career_name="Machine Learning Engineer", related_specializations=["AIML", "AIDS"],
         required_skills=["Machine Learning", "Python", "Deep Learning"], demand_score=10),
    dict(career_name="AI Research Engineer", related_specializations=["AIML"],
         required_skills=["Deep Learning", "Machine Learning", "Statistics"], demand_score=9),
    dict(career_name="Computer Vision Engineer", related_specializations=["AIML"],
         required_skills=["Computer Vision", "Deep Learning", "Python"], demand_score=8),
    dict(career_name="NLP Engineer", related_specializations=["AIML"],
         required_skills=["NLP", "Deep Learning", "Python"], demand_score=8),
    dict(career_name="Robotics Engineer", related_specializations=["AIML", "IOT"],
         required_skills=["Machine Learning", "Embedded Systems"], demand_score=7),
    dict(career_name="Data Scientist", related_specializations=["AIDS", "AIML"],
         required_skills=["Machine Learning", "Statistics", "Data Analytics", "Python"], demand_score=10),
    dict(career_name="Data Analyst", related_specializations=["AIDS", "CSBS"],
         required_skills=["Data Analytics", "SQL", "Statistics"], demand_score=8),
    dict(career_name="Business Intelligence Analyst", related_specializations=["AIDS", "CSBS"],
         required_skills=["Business Analytics", "Data Analytics", "SQL"], demand_score=7),
    dict(career_name="Data Engineer", related_specializations=["AIDS"],
         required_skills=["Data Engineering", "SQL", "Cloud Computing", "Python"], demand_score=9),
    dict(career_name="IT Support Engineer", related_specializations=["IT"],
         required_skills=["Networking", "Operating Systems"], demand_score=6),
    dict(career_name="Network Administrator", related_specializations=["IT", "CYSEC"],
         required_skills=["Networking", "Operating Systems"], demand_score=6),
    dict(career_name="Systems Administrator", related_specializations=["IT"],
         required_skills=["Operating Systems", "Cloud Computing", "Networking"], demand_score=6),
    dict(career_name="Database Administrator", related_specializations=["IT", "CSE"],
         required_skills=["DBMS", "SQL"], demand_score=6),
    dict(career_name="Cloud Engineer", related_specializations=["IT", "CSE"],
         required_skills=["Cloud Computing", "DevOps", "Networking"], demand_score=9),
    dict(career_name="Cybersecurity Analyst", related_specializations=["CYSEC"],
         required_skills=["Cyber Security", "Networking"], demand_score=9),
    dict(career_name="Penetration Tester", related_specializations=["CYSEC"],
         required_skills=["Ethical Hacking", "Cyber Security"], demand_score=9),
    dict(career_name="Security Architect", related_specializations=["CYSEC"],
         required_skills=["Cyber Security", "Cryptography", "Networking"], demand_score=8),
    dict(career_name="SOC Analyst", related_specializations=["CYSEC"],
         required_skills=["Cyber Security", "Networking"], demand_score=7),
    dict(career_name="Product Manager (Tech)", related_specializations=["CSBS"],
         required_skills=["Business Analytics", "Software Engineering"], demand_score=8),
    dict(career_name="Business Systems Analyst", related_specializations=["CSBS"],
         required_skills=["Business Analytics", "SQL", "Data Analytics"], demand_score=7),
    dict(career_name="IT Consultant", related_specializations=["CSBS", "IT"],
         required_skills=["Business Analytics", "Software Engineering"], demand_score=6),
    dict(career_name="IoT Solutions Engineer", related_specializations=["IOT"],
         required_skills=["IoT", "Embedded Systems", "Networking"], demand_score=7),
    dict(career_name="Embedded Systems Engineer", related_specializations=["IOT"],
         required_skills=["Embedded Systems", "Hardware Design", "C"], demand_score=7),
    dict(career_name="Firmware Engineer", related_specializations=["IOT"],
         required_skills=["Embedded Systems", "C", "Hardware Design"], demand_score=7),
]
