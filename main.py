import os
import json
import socket
from datetime import datetime

import pandas as pd
import psutil
import requests


# =========================
# 1. 설정
# =========================
CPU_THRESHOLD = 80
MEMORY_THRESHOLD = 80
DISK_THRESHOLD = 85
HTTP_TIMEOUT = 3

URLS_TO_CHECK = [
    "https://www.google.com",
    "https://www.naver.com"
]

PORTS_TO_CHECK = [
    ("google.com", 443),
    ("naver.com", 443),
    ("127.0.0.1", 8000)
]

LOG_FILE_PATH = "sample_app.log"

RESULT_CSV = "system_check_report.csv"
RESULT_JSON = "system_check_report.json"


# =========================
# 2. 공통 유틸
# =========================
def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add_issue(issue_list, category, target, message, severity):
    issue_list.append({
        "time": current_time(),
        "category": category,
        "target": target,
        "message": message,
        "severity": severity
    })


def classify_overall_status(issue_list):
    severities = [issue["severity"] for issue in issue_list]

    if "CRITICAL" in severities:
        return "CRITICAL"
    elif "CAUTION" in severities:
        return "CAUTION"
    else:
        return "NORMAL"


# =========================
# 3. 시스템 자원 점검
# =========================
def check_system_resources():
    results = []
    issues = []

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent

    if os.name == "nt":
        disk_usage = psutil.disk_usage("C:\\").percent
    else:
        disk_usage = psutil.disk_usage("/").percent

    results.append({
        "time": current_time(),
        "check_type": "system",
        "target": "cpu",
        "value": cpu_usage,
        "status": "OK" if cpu_usage < CPU_THRESHOLD else "ALERT"
    })
    if cpu_usage >= CPU_THRESHOLD:
        add_issue(issues, "system", "cpu", f"High CPU usage detected: {cpu_usage}%", "CAUTION")

    results.append({
        "time": current_time(),
        "check_type": "system",
        "target": "memory",
        "value": memory_usage,
        "status": "OK" if memory_usage < MEMORY_THRESHOLD else "ALERT"
    })
    if memory_usage >= MEMORY_THRESHOLD:
        add_issue(issues, "system", "memory", f"High memory usage detected: {memory_usage}%", "CAUTION")

    results.append({
        "time": current_time(),
        "check_type": "system",
        "target": "disk",
        "value": disk_usage,
        "status": "OK" if disk_usage < DISK_THRESHOLD else "ALERT"
    })
    if disk_usage >= DISK_THRESHOLD:
        add_issue(issues, "system", "disk", f"High disk usage detected: {disk_usage}%", "CRITICAL")

    return results, issues


# =========================
# 4. 포트 점검
# =========================
def check_ports():
    results = []
    issues = []

    for host, port in PORTS_TO_CHECK:
        target_name = f"{host}:{port}"
        try:
            with socket.create_connection((host, port), timeout=3):
                results.append({
                    "time": current_time(),
                    "check_type": "port",
                    "target": target_name,
                    "value": "reachable",
                    "status": "OK"
                })
        except Exception as e:
            results.append({
                "time": current_time(),
                "check_type": "port",
                "target": target_name,
                "value": "unreachable",
                "status": "ALERT"
            })
            add_issue(
                issues,
                "port",
                target_name,
                f"Port check failed: {str(e)}",
                "CRITICAL"
            )

    return results, issues


# =========================
# 5. 웹 응답 점검
# =========================
def check_urls():
    results = []
    issues = []

    for url in URLS_TO_CHECK:
        try:
            response = requests.get(url, timeout=HTTP_TIMEOUT)
            status_code = response.status_code

            results.append({
                "time": current_time(),
                "check_type": "url",
                "target": url,
                "value": status_code,
                "status": "OK" if status_code == 200 else "ALERT"
            })

            if status_code != 200:
                add_issue(
                    issues,
                    "url",
                    url,
                    f"Unexpected HTTP status code: {status_code}",
                    "CAUTION"
                )

        except Exception as e:
            results.append({
                "time": current_time(),
                "check_type": "url",
                "target": url,
                "value": "request_failed",
                "status": "ALERT"
            })
            add_issue(
                issues,
                "url",
                url,
                f"HTTP request failed: {str(e)}",
                "CRITICAL"
            )

    return results, issues


# =========================
# 6. 로그 점검
# =========================
def check_log_file():
    results = []
    issues = []

    if not os.path.exists(LOG_FILE_PATH):
        results.append({
            "time": current_time(),
            "check_type": "log",
            "target": LOG_FILE_PATH,
            "value": "file_not_found",
            "status": "SKIP"
        })
        return results, issues

    error_count = 0
    warning_count = 0

    with open(LOG_FILE_PATH, "r", encoding="utf-8") as file:
        for line in file:
            line_upper = line.upper()
            if "ERROR" in line_upper:
                error_count += 1
            elif "WARN" in line_upper or "WARNING" in line_upper:
                warning_count += 1

    results.append({
        "time": current_time(),
        "check_type": "log",
        "target": LOG_FILE_PATH,
        "value": f"errors={error_count}, warnings={warning_count}",
        "status": "OK" if error_count == 0 and warning_count == 0 else "ALERT"
    })

    if warning_count > 0:
        add_issue(
            issues,
            "log",
            LOG_FILE_PATH,
            f"Warning messages detected: {warning_count}",
            "CAUTION"
        )

    if error_count > 0:
        add_issue(
            issues,
            "log",
            LOG_FILE_PATH,
            f"Error messages detected: {error_count}",
            "CRITICAL"
        )

    return results, issues


# =========================
# 7. 리포트 저장
# =========================
def save_reports(check_results, issues, overall_status):
    report_df = pd.DataFrame(check_results)
    report_df.to_csv(RESULT_CSV, index=False, encoding="utf-8-sig")

    report_json = {
        "generated_at": current_time(),
        "overall_status": overall_status,
        "total_checks": len(check_results),
        "total_issues": len(issues),
        "issues": issues
    }

    with open(RESULT_JSON, "w", encoding="utf-8") as file:
        json.dump(report_json, file, ensure_ascii=False, indent=2)

    print(f"Saved CSV report: {RESULT_CSV}")
    print(f"Saved JSON report: {RESULT_JSON}")
    print()


# =========================
# 8. 메인 실행
# =========================
def run_system_check():
    all_results = []
    all_issues = []

    system_results, system_issues = check_system_resources()
    all_results.extend(system_results)
    all_issues.extend(system_issues)

    port_results, port_issues = check_ports()
    all_results.extend(port_results)
    all_issues.extend(port_issues)

    url_results, url_issues = check_urls()
    all_results.extend(url_results)
    all_issues.extend(url_issues)

    log_results, log_issues = check_log_file()
    all_results.extend(log_results)
    all_issues.extend(log_issues)

    overall_status = classify_overall_status(all_issues)

    print("=== System Check Summary ===")
    print(f"Check time: {current_time()}")
    print(f"Overall status: {overall_status}")
    print(f"Total checks: {len(all_results)}")
    print(f"Total issues: {len(all_issues)}")
    print()

    if all_issues:
        print("=== Issue List ===")
        for issue in all_issues:
            print(f"[{issue['severity']}] {issue['category']} - {issue['target']} - {issue['message']}")
    else:
        print("No issues detected.")
    print()

    save_reports(all_results, all_issues, overall_status)


if __name__ == "__main__":
    run_system_check()