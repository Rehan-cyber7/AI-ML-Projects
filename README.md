# AI/ML and Cybersecurity Projects

A collection of Python projects focused on Artificial Intelligence, Machine Learning, and Cybersecurity.

## Projects

### 1. AI-Based Job Recommendation System
A Python-based application that matches candidate profiles with job listings using skill matching and text similarity.

**Key features**
- Job recommendations
- Candidate and job management
- Skill matching
- Matching scores and analytics
- Web dashboard

**Technologies:** Python, NumPy, SciPy, SQLite, HTML, CSS, JavaScript.

### 2. Phishing Website Detector
A security application that analyzes URLs and estimates whether they may be associated with phishing attacks.

**Key features**
- URL feature analysis
- Machine-learning predictions
- Domain reputation checks
- Flask API
- Browser extension
- Phishing-risk assessment

**Technologies:** Python, Flask, Scikit-learn, Pandas, NumPy, Joblib, JavaScript.

**Note:** Predictions are estimates and should not be treated as guarantees that a website is safe or malicious.

### 3. Penetration Testing Toolkit
A collection of security-testing modules for assessing potential weaknesses in authorized web application tests.

**Key features**
- HTTP security-header analysis
- SSL/TLS analysis
- Directory enumeration
- SQL injection detection
- Reflected XSS detection
- JSON and Markdown reports
- Optional OWASP ZAP integration

**Technologies:** Python, Requests, Beautiful Soup, lxml, Cryptography, OWASP ZAP integration.

**Note:** Use this toolkit only on systems you own or have explicit authorization to test.

## Getting Started

1. Clone or download this repository.
2. Open the required project folder in Visual Studio Code.
3. Create a Python virtual environment for that project.
4. Install the dependencies listed in its `requirements.txt`, if provided.
5. Follow the project's individual setup instructions.

Each project has its own dependencies and should be run separately.

## Repository Structure

```text
AI-ML-Cybersecurity-Projects/
├── README.md
├── 1-Job-Recommendation-System/
├── 2-Phishing-Detector/
└── 3-Penetration-Testing-Toolkit/
```

## Security

Do not commit API keys, passwords, private credentials, or `.env` files.

Security-testing modules must only be used for authorized testing.

## Author

Rehan Shaikh

## License

Add a license if you intend to distribute these projects publicly. Ensure that the licenses of third-party code and dependencies are respected.