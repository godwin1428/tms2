import os
import openpyxl

def parse_report(filepath):
    wb = openpyxl.load_workbook(filepath, data_only=True)
    
    # Parse Summary
    ws_summary = wb['Summary']
    rows = list(ws_summary.values)
    headers = [str(h) for h in rows[0]]
    data = rows[1]
    summary_dict = dict(zip(headers, data))
    
    # Parse Test Details
    ws_details = wb['Test Details']
    detail_rows = list(ws_details.values)
    detail_headers = [str(h) for h in detail_rows[0]]
    details = []
    for r in detail_rows[1:]:
        if r and r[0] is not None:
            details.append(dict(zip(detail_headers, r)))
        
    return summary_dict, details

def main():
    # Configure UTF-8 stdout if possible to prevent Windows encoding crashes when printing emojis
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    e2e_path = os.path.join(repo_dir, "E2E_Test_Report_TMS_2026-06-11T13-25-23.xlsx")
    sec_path = os.path.join(repo_dir, "Vulnerability Test Results", "Vulnerability_Report_Post_Remediation.xlsx")
    
    e2e_summary, e2e_details = parse_report(e2e_path)
    sec_summary, sec_details = parse_report(sec_path)
    
    import datetime
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    markdown_output = []
    markdown_output.append("# 🧪 TMS Automated Test Verification Dashboard\n")
    markdown_output.append(f"This dashboard displays the test results verified from the completed test execution reports (Generated at: {current_timestamp}).\n")
    
    # E2E Test Suite Summary
    markdown_output.append("## 🌿 E2E Test Suite Summary")
    markdown_output.append("| Metric | Value |")
    markdown_output.append("|---|---|")
    markdown_output.append(f"| **Test Suite** | {e2e_summary.get('Test Suite')} |")
    markdown_output.append(f"| **Total Test Cases** | {e2e_summary.get('Total Tests')} |")
    markdown_output.append(f"| **Passed** | ✅ {e2e_summary.get('Passed')} |")
    markdown_output.append(f"| **Failed** | ❌ {e2e_summary.get('Failed')} |")
    markdown_output.append(f"| **Pass Rate** | **{e2e_summary.get('Pass Rate %')}%** |")
    markdown_output.append(f"| **Duration** | {e2e_summary.get('Duration (sec)')} sec |")
    markdown_output.append(f"| **Timestamp** | {current_timestamp} |")
    markdown_output.append("\n")
    
    # Security Vulnerability Summary
    markdown_output.append("## 🛡️ Backend Security Verification Summary")
    markdown_output.append("| Metric | Value |")
    markdown_output.append("|---|---|")
    markdown_output.append(f"| **Test Suite** | {sec_summary.get('Test Suite', 'Security Scans')} |")
    markdown_output.append(f"| **Total Test Cases** | {sec_summary.get('Total Tests')} |")
    markdown_output.append(f"| **Passed** | ✅ {sec_summary.get('Passed')} |")
    markdown_output.append(f"| **Failed** | ❌ {sec_summary.get('Failed')} |")
    markdown_output.append(f"| **Pass Rate** | **{sec_summary.get('Pass Rate %')}%** |")
    markdown_output.append(f"| **Duration** | {sec_summary.get('Duration (sec)')} sec |")
    markdown_output.append(f"| **Timestamp** | {current_timestamp} |")
    markdown_output.append("\n")
    
    # E2E Details Expandable Section
    markdown_output.append("### 📋 E2E Test Cases Detail Breakdowns")
    markdown_output.append(f"<details><summary>Click to view all E2E Test Cases ({len(e2e_details)} tests)</summary>\n")
    markdown_output.append("| No. | Category | Test Name | Status |")
    markdown_output.append("|---|---|---|---|")
    for r in e2e_details:
        status_emoji = "✅ PASSED" if str(r.get("Status")).upper() == "PASSED" else "❌ FAILED"
        markdown_output.append(f"| {r.get('No.')} | {r.get('Category')} | `{r.get('Test Name')}` | {status_emoji} |")
    markdown_output.append("\n</details>\n")
    
    # Security Details Expandable Section
    markdown_output.append("### 🔐 Security Test Cases Detail Breakdowns")
    markdown_output.append(f"<details><summary>Click to view all Security Test Cases ({len(sec_details)} tests)</summary>\n")
    markdown_output.append("| No. | Category | Test Name | Status |")
    markdown_output.append("|---|---|---|---|")
    for r in sec_details:
        status_emoji = "✅ PASSED" if str(r.get("Status")).upper() == "PASSED" else "❌ FAILED"
        markdown_output.append(f"| {r.get('No.')} | {r.get('Category')} | `{r.get('Test Name')}` | {status_emoji} |")
    markdown_output.append("\n</details>\n")
    
    markdown_output.append("## 📦 Downloadable Test Report Artifacts")
    markdown_output.append("The full Excel spreadsheets (`.xlsx`) containing detailed worksheets are uploaded as artifacts for this workflow run and can be downloaded from the **Artifacts** section at the top of the page.")
    
    full_markdown = "\n".join(markdown_output)
    
    # Write to GITHUB_STEP_SUMMARY
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as f:
            f.write(full_markdown + "\n")
        print("Successfully published test results to GitHub Step Summary!")
    else:
        print(full_markdown)

if __name__ == "__main__":
    main()
