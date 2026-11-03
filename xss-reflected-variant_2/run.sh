#!/usr/bin/env bash
# Runner script for Reflected XSS (Variant 2) - Aman (IIT2024140)
# IIITA Cyber Security Lab (IT-30001)

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=================================================================="
echo " IIIT Allahabad - Cyber Security (IT-30001) Lab Application"
echo " Category: Cross-Site Scripting (XSS) | Variant 2: Reflected XSS"
echo " Implemented by: Aman (IIT2024140)"
echo " Running at: http://127.0.0.1:8080"
echo "=================================================================="

python3 app.py
