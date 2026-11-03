# Web Server Security: Exploitation and Mitigation

**Indian Institute of Information Technology Allahabad**

**Course:** Cyber Security (IT-30001), Autumn Semester 2026

**Instructor:** Dr. Soumyadev Maity | **Group:** 7

Group assignment covering SQL injection, OS command injection, cross-site scripting (XSS), and cross-site request forgery (CSRF). Each member owns one variant and demonstrates both a working exploit and a mitigation that blocks the same payload.

## Team and ownership (Table 3)

| Member | Roll number | Category | Assigned variant |
| --- | --- | --- | --- |
| Suyash Kumar | IIT2024169 | SQL injection | Variant 1: Authentication bypass |
| Aryan | IIT2024128 | CSRF | Variant 2: POST-based forged action (auto-submitting form) |
| Varun | IIT2024150 | OS command injection | Variant 1: In-band (command output returned) |
| Aman | IIT2024140 | XSS | Variant 2: Reflected XSS |
| Vivek | IIT2024125 | CSRF | Variant 1: GET-based forged action |

Each member is responsible for personally implementing, narrating, and defending their assigned variant. The two CSRF assignments use different variants, as required when a category is shared.

> **Assignment wording:** The PDF header states a maximum of four members, while instruction 1 explicitly permits larger groups if members sharing a category choose different variants. This five-member allocation follows instruction 1 and covers all four categories.

## Available projects

| Project documentation | Stack | Local URL |
| --- | --- | --- |
| [SQL injection: authentication bypass](sql-injection-variant_1/README.md) | Node.js, Express, sql.js (SQLite) | http://localhost:3000 |
| [OS command injection: in-band output](os-command-injection-variant_1/README.md) | Python, Flask, system `ping` | http://127.0.0.1:5000 |
| [CSRF: POST-based forged action](csrf-post-variant_2/README.md) | Python, Flask (bank and attacker apps) | Bank: http://localhost:3000; attacker: http://localhost:3001 |
| [CSRF: GET-based forged action](csrf-get-variant_1/README.md) | Node.js | Portal: http://localhost:3000; attacker: http://localhost:4000 |

Each project README contains its setup instructions, vulnerable code path, exact exploit, root cause, implemented mitigation, and mitigation theory. The OS command injection project requires Linux, WSL, or macOS because it uses Unix-style `ping` arguments.

Run the SQL, GET-based CSRF, and POST-based CSRF demos separately because their default victim apps use port `3000`.

The XSS implementation is not present in this checkout yet.
