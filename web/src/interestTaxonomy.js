// Interest domain -> subtopics taxonomy for the New Student "Interests" input.
//
// Reuses the project's existing 11 academic domains (same names as
// skill_domain_map.csv) and existing terminology only:
//   - subtopics that ARE skill_name values from course_skill.csv, or
//   - subtopics that ARE course_name values from courses.csv
// No invented terms. Kept intentionally small per domain (2-4 items).
//
// Not integrated into the recommendation model or domain_strength.py —
// display/reference data only for the interests UI in NewStudent.jsx.

export const INTEREST_LEVELS = ['Low', 'Medium', 'High']

export const INTEREST_DOMAINS = {
  'Programming': ['Data Structures', 'Algorithms', 'Backend Development', 'Frontend Development'],
  'Mathematics': ['Discrete Mathematics', 'Linear Algebra & Calculus'],
  'Statistics': ['Probability & Statistics', 'Statistical Data Analysis', 'Time Series Analysis'],
  'AI / Machine Learning': ['Machine Learning', 'Deep Learning', 'Computer Vision', 'NLP'],
  'Data Science': ['Data Analytics', 'Data Engineering', 'Business Analytics'],
  'Database Systems': ['DBMS', 'SQL'],
  'Computer Networks': ['Networking', 'Network Administration', 'IoT', 'Wireless Sensor Networks'],
  'Cybersecurity': ['Ethical Hacking', 'Cryptography', 'Network Security', 'Malware Analysis'],
  'Operating Systems / Systems': ['Operating Systems', 'Embedded Systems', 'Hardware Design'],
  'Software Engineering': ['Software Testing', 'Web Development', 'Software Architecture & Design Patterns'],
  'Cloud / Distributed Systems': ['Cloud Computing', 'Distributed Systems', 'DevOps', 'Edge Computing'],
}

export const INTEREST_DOMAIN_NAMES = Object.keys(INTEREST_DOMAINS)
