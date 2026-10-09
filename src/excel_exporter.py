import os
import re
import platform
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Color palette definition
COLOR_HEADER_BG = "800000"         # Deep Burgundy
COLOR_HEADER_FG = "FFFFFF"         # White
COLOR_SUBHEADER_BG = "1E293B"      # Dark Slate
COLOR_SUBHEADER_FG = "FFFFFF"      # White

COLOR_PASS_BG = "DCFCE7"           # Light Emerald
COLOR_PASS_FG = "166534"           # Dark Emerald
COLOR_FAIL_BG = "FEE2E2"           # Light Crimson
COLOR_FAIL_FG = "991B1B"           # Dark Crimson

COLOR_ZEBRA_1 = "FFFFFF"           # White
COLOR_ZEBRA_2 = "F8FAFC"           # Ultra light slate/grey
COLOR_BORDER = "CBD5E1"            # Slate border

COLOR_KPI_TOTAL_BG = "F1F5F9"      # Soft grey
COLOR_KPI_TOTAL_FG = "1E293B"      # Dark slate
COLOR_KPI_PASS_BG = "DCFCE7"       # Soft green
COLOR_KPI_PASS_FG = "15803D"       # Dark green
COLOR_KPI_FAIL_BG = "FEE2E2"       # Soft red
COLOR_KPI_FAIL_FG = "B91C1C"       # Dark red
COLOR_KPI_SCORE_BG = "EDE9FE"      # Soft purple
COLOR_KPI_SCORE_FG = "6D28D9"      # Dark purple

# Common styles
FONT_TITLE = Font(name="Segoe UI", size=16, bold=True, color="FFFFFF")
FONT_SECTION = Font(name="Segoe UI", size=12, bold=True, color="1E293B")
FONT_HEADER = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
FONT_BODY = Font(name="Segoe UI", size=10, color="1E293B")
FONT_BODY_BOLD = Font(name="Segoe UI", size=10, bold=True, color="1E293B")
FONT_MONO = Font(name="Consolas", size=9, color="0F172A")
FONT_KPI_LABEL = Font(name="Segoe UI", size=9, bold=True, color="475569")
FONT_KPI_VAL = Font(name="Segoe UI", size=20, bold=True)

THIN_SIDE = Side(border_style="thin", color=COLOR_BORDER)
BORDER_ALL = Border(left=THIN_SIDE, right=THIN_SIDE, top=THIN_SIDE, bottom=THIN_SIDE)
BORDER_TOP_BOTTOM = Border(top=THIN_SIDE, bottom=THIN_SIDE)

FILL_HEADER = PatternFill(start_color=COLOR_HEADER_BG, end_color=COLOR_HEADER_BG, fill_type="solid")
FILL_SUBHEADER = PatternFill(start_color=COLOR_SUBHEADER_BG, end_color=COLOR_SUBHEADER_BG, fill_type="solid")
FILL_ZEBRA_1 = PatternFill(start_color=COLOR_ZEBRA_1, end_color=COLOR_ZEBRA_1, fill_type="solid")
FILL_ZEBRA_2 = PatternFill(start_color=COLOR_ZEBRA_2, end_color=COLOR_ZEBRA_2, fill_type="solid")
FILL_PASS = PatternFill(start_color=COLOR_PASS_BG, end_color=COLOR_PASS_BG, fill_type="solid")
FILL_FAIL = PatternFill(start_color=COLOR_FAIL_BG, end_color=COLOR_FAIL_BG, fill_type="solid")

COLOR_SEV_CRIT_BG = "F3E8FF"  # Soft purple
COLOR_SEV_CRIT_FG = "6B21A8"
COLOR_SEV_HIGH_BG = "FFE4E6"  # Soft rose
COLOR_SEV_HIGH_FG = "9F1239"
COLOR_SEV_MED_BG = "FEF3C7"   # Soft amber
COLOR_SEV_MED_FG = "92400E"
COLOR_SEV_LOW_BG = "E0F2FE"   # Soft sky
COLOR_SEV_LOW_FG = "075985"

FILL_SEV_CRIT = PatternFill(start_color=COLOR_SEV_CRIT_BG, end_color=COLOR_SEV_CRIT_BG, fill_type="solid")
FILL_SEV_HIGH = PatternFill(start_color=COLOR_SEV_HIGH_BG, end_color=COLOR_SEV_HIGH_BG, fill_type="solid")
FILL_SEV_MED = PatternFill(start_color=COLOR_SEV_MED_BG, end_color=COLOR_SEV_MED_BG, fill_type="solid")
FILL_SEV_LOW = PatternFill(start_color=COLOR_SEV_LOW_BG, end_color=COLOR_SEV_LOW_BG, fill_type="solid")

FONT_SEV_CRIT = Font(name="Segoe UI", size=10, bold=True, color=COLOR_SEV_CRIT_FG)
FONT_SEV_HIGH = Font(name="Segoe UI", size=10, bold=True, color=COLOR_SEV_HIGH_FG)
FONT_SEV_MED = Font(name="Segoe UI", size=10, bold=True, color=COLOR_SEV_MED_FG)
FONT_SEV_LOW = Font(name="Segoe UI", size=10, bold=True, color=COLOR_SEV_LOW_FG)

ALIGN_CENTER = Alignment(horizontal="center", vertical="center")
ALIGN_LEFT = Alignment(horizontal="left", vertical="center")
ALIGN_LEFT_WRAP = Alignment(horizontal="left", vertical="center", wrap_text=True)
ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")

def autofit_column_widths(ws, min_width=10, max_width_dict=None, default_max=50):
    """
    Adjust column widths automatically based on cell contents with padding and constraints.
    """
    if max_width_dict is None:
        max_width_dict = {}

    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            # Skip title banner row in Executive Summary
            if cell.row == 1 and ws.title == "Executive Summary":
                continue
            if cell.value is not None:
                val_str = str(cell.value)
                lines = val_str.split("\n")
                line_max = max(len(l) for l in lines) if lines else 0
                max_len = max(max_len, line_max)

        col_max = max_width_dict.get(col_letter, default_max)
        calculated_width = max(max_len + 3, min_width)
        ws.column_dimensions[col_letter].width = min(calculated_width, col_max)

def export_audit_results_to_excel(audit_records, metadata=None, output_path="outputs/CIS_Benchmark_Audit_Results.xlsx"):
    """
    Generates a multi-sheet, enterprise-grade Excel workbook containing:
    1. Executive Summary & KPIs
    2. Detailed Audit Results
    3. Remediation & Hardening Guide
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    wb = openpyxl.Workbook()
    
    if metadata is None:
        metadata = {}

    hostname = metadata.get("hostname", platform.node() or "Local Machine")
    os_name = metadata.get("os_name", f"{platform.system()} {platform.release()} ({platform.version()})")
    scan_date = metadata.get("scan_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    scope = metadata.get("scope", "All Selected Hives")
    compliance_target = metadata.get("compliance_target") or metadata.get("benchmark_title") or "CIS Security Benchmark"
    evaluation_engine = metadata.get("evaluation_engine") or "Risk Nexus CIS Security Benchmark Engine"

    total_rules = len(audit_records)
    pass_count = sum(1 for r in audit_records if str(r.get("status", "")).upper() in ("PASS", "COMPLIANT", "YES"))
    fail_count = total_rules - pass_count
    score_pct = (pass_count / total_rules * 100.0) if total_rules > 0 else 0.0

    # -------------------------------------------------------------
    # Sheet 1: Executive Summary
    # -------------------------------------------------------------
    ws_summary = wb.active
    ws_summary.title = "Executive Summary"
    ws_summary.views.sheetView[0].showGridLines = True

    # 1. Header Banner
    ws_summary.merge_cells("A1:G2")
    banner_cell = ws_summary["A1"]
    banner_cell.value = "  RISK NEXUS - CIS SECURITY BENCHMARK SYSTEM AUDIT REPORT"
    banner_cell.font = FONT_TITLE
    banner_cell.fill = FILL_HEADER
    banner_cell.alignment = Alignment(horizontal="left", vertical="center")

    # 2. Environment Information Table
    ws_summary["A4"] = "System Environment & Audit Scope"
    ws_summary["A4"].font = FONT_SECTION

    env_data = [
        ("Computer Name / Hostname:", hostname, "Audit Timestamp:", scan_date),
        ("Operating System Platform:", os_name, "Compliance Target:", compliance_target),
        ("Target Registry Hive Scope:", scope, "Evaluation Engine:", evaluation_engine),
        ("Created By:", "Dibyataru Chakraborty", "Tool Suite:", "Risk Nexus Security Suite"),
    ]

    for row_idx, (k1, v1, k2, v2) in enumerate(env_data, start=5):
        ws_summary[f"A{row_idx}"] = k1
        ws_summary[f"A{row_idx}"].font = FONT_BODY_BOLD
        ws_summary[f"A{row_idx}"].fill = FILL_ZEBRA_2
        ws_summary[f"A{row_idx}"].border = BORDER_ALL

        ws_summary.merge_cells(f"B{row_idx}:C{row_idx}")
        ws_summary[f"B{row_idx}"] = v1
        ws_summary[f"B{row_idx}"].font = FONT_BODY
        ws_summary[f"B{row_idx}"].border = BORDER_ALL
        ws_summary[f"C{row_idx}"].border = BORDER_ALL

        ws_summary[f"D{row_idx}"] = k2
        ws_summary[f"D{row_idx}"].font = FONT_BODY_BOLD
        ws_summary[f"D{row_idx}"].fill = FILL_ZEBRA_2
        ws_summary[f"D{row_idx}"].border = BORDER_ALL

        ws_summary.merge_cells(f"E{row_idx}:G{row_idx}")
        ws_summary[f"E{row_idx}"] = v2
        ws_summary[f"E{row_idx}"].font = FONT_BODY
        ws_summary[f"E{row_idx}"].border = BORDER_ALL
        ws_summary[f"F{row_idx}"].border = BORDER_ALL
        ws_summary[f"G{row_idx}"].border = BORDER_ALL

    # 3. KPI Summary Cards
    ws_summary["A9"] = "Audit Executive KPI Summary"
    ws_summary["A9"].font = FONT_SECTION

    card_ranges = [
        ("A", "B", 10, "TOTAL RULES AUDITED", str(total_rules), COLOR_KPI_TOTAL_BG, COLOR_KPI_TOTAL_FG),
        ("C", "D", 10, "COMPLIANT (PASSED)", str(pass_count), COLOR_KPI_PASS_BG, COLOR_KPI_PASS_FG),
        ("E", "F", 10, "NON-COMPLIANT (FAILED)", str(fail_count), COLOR_KPI_FAIL_BG, COLOR_KPI_FAIL_FG),
        ("G", "G", 10, "OVERALL SCORE", f"{score_pct:.1f}%", COLOR_KPI_SCORE_BG, COLOR_KPI_SCORE_FG),
    ]

    for c_start, c_end, r_top, label, val, bg_col, fg_col in card_ranges:
        fill_card = PatternFill(start_color=bg_col, end_color=bg_col, fill_type="solid")
        font_card_val = Font(name="Segoe UI", size=20, bold=True, color=fg_col)
        
        # Label cell
        if c_start != c_end:
            ws_summary.merge_cells(f"{c_start}{r_top}:{c_end}{r_top}")
            ws_summary.merge_cells(f"{c_start}{r_top+1}:{c_end}{r_top+2}")
        else:
            ws_summary.merge_cells(f"{c_start}{r_top+1}:{c_start}{r_top+2}")

        lbl_cell = ws_summary[f"{c_start}{r_top}"]
        lbl_cell.value = label
        lbl_cell.font = FONT_KPI_LABEL
        lbl_cell.alignment = ALIGN_CENTER
        lbl_cell.fill = fill_card

        val_cell = ws_summary[f"{c_start}{r_top+1}"]
        val_cell.value = val
        val_cell.font = font_card_val
        val_cell.alignment = ALIGN_CENTER
        val_cell.fill = fill_card

        # Apply borders to card box
        cols_in_card = [c_start] if c_start == c_end else [c_start, c_end]
        for col_name in cols_in_card:
            for row_num in range(r_top, r_top + 3):
                ws_summary[f"{col_name}{row_num}"].border = BORDER_ALL
                ws_summary[f"{col_name}{row_num}"].fill = fill_card

    # 4. Profile / Level Breakdown Table
    ws_summary["A14"] = "Compliance Breakdown by Profile Level"
    ws_summary["A14"].font = FONT_SECTION

    level_headers = ["Profile Level", "Total Rules", "Compliant (Pass)", "Non-Compliant (Fail)", "Pass Rate %"]
    for col_idx, h_text in enumerate(level_headers, start=1):
        cell = ws_summary.cell(row=15, column=col_idx, value=h_text)
        cell.font = FONT_HEADER
        cell.fill = FILL_SUBHEADER
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_ALL

    levels = ["L1", "L2", "NG"]
    curr_row = 16
    for lvl in levels:
        lvl_rules = [r for r in audit_records if str(r.get("level", "")).upper() == lvl or str(r.get("level", "")).upper() == f"LEVEL {lvl[-1]} ({lvl})"]
        if not lvl_rules and lvl == "L1":
            lvl_rules = [r for r in audit_records if "L1" in str(r.get("level", "")).upper()]
        elif not lvl_rules and lvl == "L2":
            lvl_rules = [r for r in audit_records if "L2" in str(r.get("level", "")).upper()]

        if not lvl_rules:
            continue

        lvl_total = len(lvl_rules)
        lvl_pass = sum(1 for r in lvl_rules if str(r.get("status", "")).upper() in ("PASS", "COMPLIANT", "YES"))
        lvl_fail = lvl_total - lvl_pass
        lvl_rate = (lvl_pass / lvl_total * 100.0) if lvl_total > 0 else 0.0

        label_display = f"Level 1 (L1) - Enterprise" if lvl == "L1" else f"Level 2 (L2) - High Security" if lvl == "L2" else "Next Generation (NG)"
        ws_summary.cell(row=curr_row, column=1, value=label_display).alignment = ALIGN_LEFT
        ws_summary.cell(row=curr_row, column=2, value=lvl_total).alignment = ALIGN_CENTER
        ws_summary.cell(row=curr_row, column=3, value=lvl_pass).alignment = ALIGN_CENTER
        ws_summary.cell(row=curr_row, column=4, value=lvl_fail).alignment = ALIGN_CENTER
        ws_summary.cell(row=curr_row, column=5, value=f"{lvl_rate:.1f}%").alignment = ALIGN_CENTER

        for col_idx in range(1, 6):
            c = ws_summary.cell(row=curr_row, column=col_idx)
            c.font = FONT_BODY
            c.border = BORDER_ALL
            c.fill = FILL_ZEBRA_1 if curr_row % 2 == 0 else FILL_ZEBRA_2
        curr_row += 1

    # 5. Category Breakdown Table
    curr_row += 1
    ws_summary.cell(row=curr_row, column=1, value="Compliance Breakdown by Category").font = FONT_SECTION
    curr_row += 1

    cat_headers = ["Category / System Subsystem", "Total Rules", "Compliant (Pass)", "Non-Compliant (Fail)", "Pass Rate %"]
    for col_idx, h_text in enumerate(cat_headers, start=1):
        cell = ws_summary.cell(row=curr_row, column=col_idx, value=h_text)
        cell.font = FONT_HEADER
        cell.fill = FILL_SUBHEADER
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_ALL

    curr_row += 1
    # Group by category
    cats = {}
    for r in audit_records:
        c_name = r.get("category", "General Security")
        if not c_name or c_name == "Unknown":
            c_name = "General Security"
        elif c_name == "sys":
            c_name = "System Configurations (HKLM\\SYSTEM)"
        elif c_name == "s/w":
            c_name = "Software & Policies (HKLM\\SOFTWARE)"
        cats.setdefault(c_name, []).append(r)

    for c_name, c_rules in sorted(cats.items()):
        c_total = len(c_rules)
        c_pass = sum(1 for r in c_rules if str(r.get("status", "")).upper() in ("PASS", "COMPLIANT", "YES"))
        c_fail = c_total - c_pass
        c_rate = (c_pass / c_total * 100.0) if c_total > 0 else 0.0

        ws_summary.cell(row=curr_row, column=1, value=c_name).alignment = ALIGN_LEFT
        ws_summary.cell(row=curr_row, column=2, value=c_total).alignment = ALIGN_CENTER
        ws_summary.cell(row=curr_row, column=3, value=c_pass).alignment = ALIGN_CENTER
        ws_summary.cell(row=curr_row, column=4, value=c_fail).alignment = ALIGN_CENTER
        ws_summary.cell(row=curr_row, column=5, value=f"{c_rate:.1f}%").alignment = ALIGN_CENTER

        for col_idx in range(1, 6):
            c = ws_summary.cell(row=curr_row, column=col_idx)
            c.font = FONT_BODY
            c.border = BORDER_ALL
            c.fill = FILL_ZEBRA_1 if curr_row % 2 == 0 else FILL_ZEBRA_2
        curr_row += 1

    # Adjust widths for Executive Summary
    summary_max_widths = {"A": 36, "B": 26, "C": 26, "D": 26, "E": 26, "F": 26, "G": 26}
    autofit_column_widths(ws_summary, min_width=16, max_width_dict=summary_max_widths)

    # -------------------------------------------------------------
    # Sheet 2: Detailed Audit Results
    # -------------------------------------------------------------
    ws_details = wb.create_sheet(title="Detailed Audit Results")
    ws_details.views.sheetView[0].showGridLines = True

    detail_columns = [
        ("SL", 8, ALIGN_CENTER),
        ("Rule ID", 15, ALIGN_CENTER),
        ("Level", 14, ALIGN_CENTER),
        ("Severity", 14, ALIGN_CENTER),
        ("Rule Title", 55, ALIGN_LEFT_WRAP),
        ("Audit Status", 16, ALIGN_CENTER),
        ("Full Registry Path", 75, ALIGN_LEFT_WRAP),
    ]

    # Write Header
    for col_idx, (col_name, col_width, _) in enumerate(detail_columns, start=1):
        cell = ws_details.cell(row=1, column=col_idx, value=col_name)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_ALL

    # Write Data
    for row_idx, r in enumerate(audit_records, start=2):
        status_val = str(r.get("status", "")).upper()
        is_pass = status_val in ("PASS", "COMPLIANT", "YES")
        row_fill = FILL_ZEBRA_1 if row_idx % 2 == 0 else FILL_ZEBRA_2
        severity_val = str(r.get("severity", r.get("Severity", "Medium")))

        values = [
            r.get("sl", row_idx - 1),
            r.get("rule_id", "-"),
            r.get("level", "L1"),
            severity_val,
            r.get("title", "Benchmark Rule"),
            "PASS" if is_pass else "FAIL",
            r.get("path", f"{r.get('hive','')}\\{r.get('key_path','')}:{r.get('value_name','')}"),
        ]

        for col_idx, val in enumerate(values, start=1):
            cell = ws_details.cell(row=row_idx, column=col_idx, value=val)
            cell.font = FONT_BODY
            cell.alignment = detail_columns[col_idx - 1][2]
            cell.border = BORDER_ALL
            cell.fill = row_fill

            # Color-code Severity (Column 4)
            if col_idx == 4:
                sev_lower = severity_val.lower()
                if "crit" in sev_lower:
                    cell.fill = FILL_SEV_CRIT
                    cell.font = FONT_SEV_CRIT
                elif "high" in sev_lower:
                    cell.fill = FILL_SEV_HIGH
                    cell.font = FONT_SEV_HIGH
                elif "med" in sev_lower:
                    cell.fill = FILL_SEV_MED
                    cell.font = FONT_SEV_MED
                elif "low" in sev_lower or "ng" in sev_lower:
                    cell.fill = FILL_SEV_LOW
                    cell.font = FONT_SEV_LOW

            # Color-code the status column (Column 6: Audit Status)
            if col_idx == 6:
                if is_pass:
                    cell.fill = FILL_PASS
                    cell.font = Font(name="Segoe UI", size=10, bold=True, color=COLOR_PASS_FG)
                else:
                    cell.fill = FILL_FAIL
                    cell.font = Font(name="Segoe UI", size=10, bold=True, color=COLOR_FAIL_FG)

    # Freeze header row & Enable AutoFilter
    ws_details.freeze_panes = "A2"
    if audit_records:
        ws_details.auto_filter.ref = f"A1:{get_column_letter(len(detail_columns))}{len(audit_records) + 1}"

    # Auto-adjust column widths
    detail_max_widths = {
        "A": 8, "B": 16, "C": 15, "D": 15, "E": 60, "F": 16, "G": 80
    }
    for col_idx, (_, col_width, _) in enumerate(detail_columns, start=1):
        col_letter = get_column_letter(col_idx)
        ws_details.column_dimensions[col_letter].width = detail_max_widths.get(col_letter, col_width)

    # -------------------------------------------------------------
    # Sheet 3: Remediation & Hardening Guide
    # -------------------------------------------------------------
    ws_remediation = wb.create_sheet(title="Remediation Guide")
    ws_remediation.views.sheetView[0].showGridLines = True

    rem_columns = [
        ("SL", 8, ALIGN_CENTER),
        ("Rule ID", 15, ALIGN_CENTER),
        ("Level", 14, ALIGN_CENTER),
        ("Severity", 14, ALIGN_CENTER),
        ("Rule Title", 50, ALIGN_LEFT_WRAP),
        ("Target Registry Path", 65, ALIGN_LEFT_WRAP),
        ("PowerShell Remediation Command", 75, ALIGN_LEFT),
        ("Reg.exe CLI Command", 75, ALIGN_LEFT),
    ]

    for col_idx, (col_name, col_width, _) in enumerate(rem_columns, start=1):
        cell = ws_remediation.cell(row=1, column=col_idx, value=col_name)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_ALL

    failed_records = [r for r in audit_records if str(r.get("status", "")).upper() not in ("PASS", "COMPLIANT", "YES")]
    
    for row_idx, r in enumerate(failed_records, start=2):
        row_fill = FILL_ZEBRA_1 if row_idx % 2 == 0 else FILL_ZEBRA_2
        severity_val = str(r.get("severity", r.get("Severity", "Medium")))
        
        hive = r.get("hive", "HKLM")
        key_path = r.get("key_path", "")
        val_name = r.get("value_name", "")
        val_type = r.get("value_type", "REG_DWORD")
        rec_val = str(r.get("recommended_value", "1"))
        
        # PowerShell type mapping
        ps_type = "DWord"
        if val_type == "REG_SZ": ps_type = "String"
        elif val_type == "REG_MULTI_SZ": ps_type = "MultiString"
        elif val_type == "REG_EXPAND_SZ": ps_type = "ExpandString"
        elif val_type == "REG_BINARY": ps_type = "Binary"
        
        hive_ps = f"{hive}:\\"
        ps_cmd = f'Set-ItemProperty -Path "{hive_ps}{key_path}" -Name "{val_name}" -Value {rec_val} -Type {ps_type} -Force'
        reg_cmd = f'reg.exe add "{hive}\\{key_path}" /v "{val_name}" /t {val_type} /d "{rec_val}" /f'
        
        values = [
            row_idx - 1,
            r.get("rule_id", "-"),
            r.get("level", "L1"),
            severity_val,
            r.get("title", "Benchmark Rule"),
            r.get("path", f"{hive}\\{key_path}:{val_name}"),
            ps_cmd,
            reg_cmd
        ]

        for col_idx, val in enumerate(values, start=1):
            cell = ws_remediation.cell(row=row_idx, column=col_idx, value=val)
            cell.font = FONT_MONO if col_idx in (7, 8) else FONT_BODY
            cell.alignment = rem_columns[col_idx - 1][2]
            cell.border = BORDER_ALL
            cell.fill = row_fill

            # Color-code Severity (Column 4)
            if col_idx == 4:
                sev_lower = severity_val.lower()
                if "crit" in sev_lower:
                    cell.fill = FILL_SEV_CRIT
                    cell.font = FONT_SEV_CRIT
                elif "high" in sev_lower:
                    cell.fill = FILL_SEV_HIGH
                    cell.font = FONT_SEV_HIGH
                elif "med" in sev_lower:
                    cell.fill = FILL_SEV_MED
                    cell.font = FONT_SEV_MED
                elif "low" in sev_lower or "ng" in sev_lower:
                    cell.fill = FILL_SEV_LOW
                    cell.font = FONT_SEV_LOW

    ws_remediation.freeze_panes = "A2"
    if failed_records:
        ws_remediation.auto_filter.ref = f"A1:{get_column_letter(len(rem_columns))}{len(failed_records) + 1}"

    rem_max_widths = {
        "A": 8, "B": 16, "C": 15, "D": 15, "E": 55, "F": 70, "G": 80, "H": 80
    }
    for col_idx, (_, col_width, _) in enumerate(rem_columns, start=1):
        col_letter = get_column_letter(col_idx)
        ws_remediation.column_dimensions[col_letter].width = rem_max_widths.get(col_letter, col_width)

    try:
        wb.save(output_path)
        print(f"[SUCCESS] Excel audit report successfully generated at: {output_path}")
        return output_path
    except PermissionError:
        fallback = output_path.replace(".xlsx", "_latest.xlsx")
        try:
            wb.save(fallback)
            print(f"[WARNING] {output_path} is open in Excel. Saved updated copy to: {fallback}")
            return fallback
        except Exception:
            return output_path

def export_benchmark_rules_to_excel(rules_data, output_path="outputs/CIS_Windows_11_Hardening_Rules.xlsx"):
    """
    Exports parsed CIS Benchmark rules to a beautifully styled Excel spreadsheet.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "CIS Benchmark Rules"
    ws.views.sheetView[0].showGridLines = True

    columns = [
        ("SL", 7, ALIGN_CENTER),
        ("Rule ID", 14, ALIGN_CENTER),
        ("Profile/Level", 14, ALIGN_CENTER),
        ("Severity", 14, ALIGN_CENTER),
        ("Rule Title", 45, ALIGN_LEFT_WRAP),
        ("Hive", 10, ALIGN_CENTER),
        ("Key Path", 45, ALIGN_LEFT_WRAP),
        ("Value Name", 26, ALIGN_LEFT),
        ("Value Type", 15, ALIGN_CENTER),
        ("Recommended Value", 20, ALIGN_CENTER),
        ("Full Registry Path", 55, ALIGN_LEFT_WRAP),
    ]

    for col_idx, (col_name, col_width, _) in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_ALL

    for row_idx, r in enumerate(rules_data, start=2):
        row_fill = FILL_ZEBRA_1 if row_idx % 2 == 0 else FILL_ZEBRA_2
        severity_val = str(r.get("Severity", r.get("severity", "Medium")))
        values = [
            row_idx - 1,
            r.get("Rule ID", r.get("rule_id", "-")),
            r.get("Profile/Level", r.get("level", "L1")),
            severity_val,
            r.get("Rule Title", r.get("title", "")),
            r.get("Hive", r.get("hive", "HKLM")),
            r.get("Key Path", r.get("key_path", "")),
            r.get("Value Name", r.get("value_name", "")),
            r.get("Value Type", r.get("value_type", "REG_DWORD")),
            str(r.get("Recommended Value", r.get("recommended_value", "1"))),
            r.get("Full Registry Path", r.get("path", "")),
        ]

        for col_idx, val in enumerate(values, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.font = FONT_BODY
            cell.alignment = columns[col_idx - 1][2]
            cell.border = BORDER_ALL
            cell.fill = row_fill

            # Color-code Severity (Column 4)
            if col_idx == 4:
                sev_lower = severity_val.lower()
                if "crit" in sev_lower:
                    cell.fill = FILL_SEV_CRIT
                    cell.font = FONT_SEV_CRIT
                elif "high" in sev_lower:
                    cell.fill = FILL_SEV_HIGH
                    cell.font = FONT_SEV_HIGH
                elif "med" in sev_lower:
                    cell.fill = FILL_SEV_MED
                    cell.font = FONT_SEV_MED
                elif "low" in sev_lower or "ng" in sev_lower:
                    cell.fill = FILL_SEV_LOW
                    cell.font = FONT_SEV_LOW

    ws.freeze_panes = "A2"
    if rules_data:
        ws.auto_filter.ref = f"A1:{get_column_letter(len(columns))}{len(rules_data) + 1}"

    max_widths = {
        "A": 8, "B": 15, "C": 15, "D": 15, "E": 50, "F": 10, "G": 50, "H": 30, "I": 16, "J": 22, "K": 60
    }
    for col_idx, (_, col_width, _) in enumerate(columns, start=1):
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = max_widths.get(col_letter, col_width)

    try:
        wb.save(output_path)
        print(f"[SUCCESS] Excel benchmark rules file successfully generated at: {output_path}")
        return output_path
    except PermissionError:
        fallback = output_path.replace(".xlsx", "_latest.xlsx")
        try:
            wb.save(fallback)
            print(f"[WARNING] {output_path} is open in Excel. Saved copy to: {fallback}")
            return fallback
        except Exception:
            return output_path

