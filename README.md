# System Monitoring Project

## 1. Project Overview
This project simulates a real-world IT system monitoring tool.

It performs system health checks including:
- CPU, Memory, Disk usage
- Port availability
- URL response status
- Log file analysis

The system generates structured reports and detects potential issues.

---

## 2. Features
- System resource monitoring
- Port status check (e.g., 8000)
- External service (URL) check
- Log file analysis
- Issue detection (NORMAL / CAUTION / CRITICAL)
- CSV and JSON report generation

---

## 3. How to Run

```bash
pip install -r requirements.txt
python main.py

## 4. Example Output
After running the program, the following output files are generated:

- `system_check_report.csv`
- `system_check_report.json`

Example console output:

```text
=== System Check Summary ===
Check time: 2026-03-25 22:12:32
Overall status: NORMAL
Total checks: 9
Total issues: 0

No issues detected.

Saved CSV report: system_check_report.csv
Saved JSON report: system_check_report.json


## 5. Tech Stack
- Python
- pandas
- psutil
- requests

---

## 6. Purpose
This project was designed to simulate practical tasks required in IT technical support roles.

It demonstrates the following capabilities:
- Basic system inspection
- Service availability check
- Issue detection and classification
- Structured report generation
- Basic infrastructure and monitoring understanding
