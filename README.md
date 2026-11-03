# Web Server Security — Exploitation and Mitigation

**Indian Institute of Information Technology Allahabad (IIITA)**  
**Department of Information Technology**  
**Course:** Cyber Security (IT-30001) | Autumn Semester 2026  
**Instructor:** Dr. Soumyadev Maity  
**Group:** 7

---

## Assignment Overview

This repository demonstrates the exploitation and mitigation of four web server vulnerability categories:

| # | Category | Directory | Variant | Member |
|---|----------|-----------|---------|--------|
| 1 | SQL Injection | [`sql-injection/`](sql-injection/) | *TBD* | *TBD* |
| 2 | **OS Command Injection** | [`os-command-injection/`](os-command-injection/) | **In-Band (output returned)** | **Varun (IIT2024150)** |
| 3 | Cross-Site Scripting (XSS) | [`xss/`](xss/) | *TBD* | *TBD* |
| 4 | Cross-Site Request Forgery (CSRF) | [`csrf/`](csrf/) | *TBD* | *TBD* |

> Each member should add their implementation inside their respective directory.

---

## Table 3: Ownership Declaration

| Member Name | Roll Number | Category | Variant Implemented |
|:---|:---|:---|:---|
| **Varun** | **IIT2024150** | OS Command Injection | In-Band (command output returned) |
| *[Member 2]* | *[Roll No]* | *[Category]* | *[Variant]* |
| *[Member 3]* | *[Roll No]* | *[Category]* | *[Variant]* |
| *[Member 4]* | *[Roll No]* | *[Category]* | *[Variant]* |

> **Declaration:** Each variant was exclusively implemented by the assigned member named above. No two members have implemented the same variant of the same category.

---

## How to Run Each Module

### OS Command Injection
```bash
cd os-command-injection/
./run.sh          # Start the web server on http://127.0.0.1:5000
./run.sh test     # Run automated exploit + mitigation tests
```

*(Other members: add your run instructions here)*

---

## Repository Structure

```
├── README.md                    ← This file (group-level)
├── os-command-injection/        ← Varun's implementation
│   ├── app.py
│   ├── templates/index.html
│   ├── test_exploit.py
│   ├── requirements.txt
│   ├── run.sh
│   ├── README.md
│   ├── WALKTHROUGH.md
│   ├── VIDEO_SCRIPT.md
│   └── ASSIGNMENT_EXPLAINED.md
├── sql-injection/               ← [Member 2's implementation]
├── xss/                         ← [Member 3's implementation]
└── csrf/                        ← [Member 4's implementation]
```
