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
| 4 | Cross-Site Post Based Request Forgery (CSRF) | [`csrf-post/`](csrf-post/) | **POST Based** | **Aryan (IIT2024128)** |

---

## Table 3: Ownership Declaration

| Member Name | Roll Number | Category | Variant Implemented |
|:---|:---|:---|:---|
| **Varun** | **IIT2024150** | OS Command Injection | In-Band (command output returned) |
| **Aryan** | **IIT2024128** | Cross Site Request Forgery | POST Based|
| *[Member 3]* | *[Roll No]* | *[Category]* | *[Variant]* |
| *[Member 4]* | *[Roll No]* | *[Category]* | *[Variant]* |

---

## How to Run Each Module

### OS Command Injection
```bash
cd os-command-injection/
./run.sh          # Start the web server on http://127.0.0.1:5000
./run.sh test     # Run automated exploit + mitigation tests
```
---

### CSRF (POST Based)
```bash
cd csrf-post/
./run.sh          # Start the bank server at localhost:3000 
                  # and attack server at localhost:3001
```
---


## Repository Structure

```
├── README.md                    
├── os-command-injection/       
│   ├── app.py
│   ├── templates/index.html
│   ├── test_exploit.py
│   ├── requirements.txt
│   ├── run.sh
│   ├── README.md
│   ├── WALKTHROUGH.md
├── sql-injection/               
├── xss/                         
└── csrf/                        
```
