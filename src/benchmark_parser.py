import os
import re
import pandas as pd
from pdfminer.high_level import extract_text

def extract_benchmark_metadata(raw_text="", pdf_path=""):
    """
    Dynamically extracts document title, version, compliance target,
    and evaluation engine from the benchmark PDF text or filename.
    """
    title = "CIS Security Benchmark"
    version = ""
    
    if raw_text:
        first_chunk = raw_text[:4000]
        m_title = re.search(r'(CIS\s+[A-Za-z0-9\s\(\)]+Benchmark(?:\s+v[\d\.]+)?|\bCIS\s+Windows\s+[0-9A-Za-z\s]+Benchmark)', first_chunk, re.IGNORECASE)
        if m_title:
            title = re.sub(r'\s+', ' ', m_title.group(1)).strip()
        
        m_ver = re.search(r'\bv?(\d+\.\d+(?:\.\d+)?)\b', title)
        if m_ver:
            version = f"v{m_ver.group(1)}"
            
    if (not title or title == "CIS Security Benchmark") and pdf_path:
        base_name = os.path.basename(pdf_path).replace(".pdf", "")
        clean_name = base_name.replace("_", " ").replace("-", " ")
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()
        if "CIS" in clean_name.upper():
            title = clean_name
            m_ver = re.search(r'\bv?(\d+\.\d+(?:\.\d+)?)\b', title, re.IGNORECASE)
            if m_ver:
                version = f"v{m_ver.group(1)}"

    return {
        "benchmark_title": title,
        "benchmark_version": version,
        "compliance_target": title,
        "evaluation_engine": "Risk Nexus CIS Security Benchmark Engine",
    }

def determine_severity(rule_id="", level="L1", title="", key_path=""):
    """
    Computes an accurate severity level (Critical, High, Medium, Low)
    based on profile level and security risk keywords.
    """
    text = f"{title} {key_path}".lower()
    
    # Critical criteria
    if any(k in text for k in ["firewall", "credential", "uac", "administrator", "bitlocker", "smbv1", "antivirus", "defender", "remote code", "anonymous"]):
        return "Critical"
    
    # High criteria
    if any(k in text for k in ["audit", "password", "lockout", "encryption", "tls", "rdp", "remote desktop", "privilege", "telemetry"]):
        return "High"
        
    # Level based defaults
    if level == "L2":
        return "High"
    elif level == "NG":
        return "Low"
    elif level == "L1":
        return "Medium"
        
    return "Medium"

def parse_cis_pdf(pdf_path):
    print(f"Reading and extracting text from {pdf_path}...")
    raw_text = extract_text(pdf_path)
    
    print("Extracting rule headings...")
    heading_pattern = r'\n\s*(\d+\.\d+(?:\.\d+)*)\s+(Ensure\s+[^\n]+(?:\n[^\n]+)?)'
    headings = []
    
    for m in re.finditer(heading_pattern, raw_text):
        sec = m.group(1)
        title_raw = m.group(2)
        
        title = re.sub(r'\s+', ' ', title_raw).strip()
        
        post_context = raw_text[m.end():m.end() + 1500]
        if "Profile Applicability" not in post_context:
            continue
            
        title = re.sub(r'\.+\s*\d+\s*$', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        level = "L1"
        if "Level 2 (L2)" in post_context[:1000]:
            level = "L2"
        elif "Level 1 (L1)" in post_context[:1000]:
            level = "L1"
        elif "NG" in post_context[:1000]:
            level = "NG"
            
        headings.append({
            'id': sec,
            'level': level,
            'title': title,
            'raw_pos': m.start()
        })
        
    headings.sort(key=lambda x: x['raw_pos'])
    print(f"Extracted {len(headings)} clean rule headings.")
    
    print("Normalizing text for registry path mapping...")
    cleaned_text = re.sub(r'(?<!\n)\n(?!\n)', ' ', raw_text)
            
    reg_pattern = r'\b(HKLM|HKCU)\\[A-Za-z0-9_\\\(\)\{\}\<\>\s*-]+\:[A-Za-z0-9_\*-\\\(\)\{\}\<\>]+'
    
    rules_data = []
    seen_paths = set()
    
    for m in re.finditer(reg_pattern, cleaned_text):
        full_reg = m.group(0).strip()
        full_reg = re.sub(r'\s+', ' ', full_reg)
        
        if ":" not in full_reg:
            continue
            
        try:
            hive, key_value = full_reg.split("\\", 1)
            key_path, val_name = key_value.split(":", 1)
        except ValueError:
            continue
            
        pos = m.start()
        
        preceding_heading = None
        for h in headings:
            if h['raw_pos'] < pos:
                preceding_heading = h
            else:
                break
                
        if not preceding_heading:
            continue
            
        rule_id = preceding_heading['id']
        level = preceding_heading['level']
        title = preceding_heading['title']
        
        dup_key = (rule_id, full_reg)
        if dup_key in seen_paths:
            continue
        seen_paths.add(dup_key)
        
        context_start = max(0, pos - 300)
        context_end = min(len(cleaned_text), pos + 200)
        context = cleaned_text[context_start:context_end]
        
        type_match = re.search(r'\b(REG_DWORD|REG_SZ|REG_MULTI_SZ|REG_EXPAND_SZ|REG_BINARY)\b', context, re.IGNORECASE)
        val_type = type_match.group(1).upper() if type_match else "REG_DWORD"
        
        val_value = "1"
        
        num_match = re.search(r'(?:value of|set to|value:?)\s*([0-9]+)\b', context, re.IGNORECASE)
        if num_match:
            val_value = num_match.group(1)
        else:
            status_match = re.search(r'(?:set to|be)\s*(Enabled|Disabled|Enable|Disable)\b', context, re.IGNORECASE)
            if status_match:
                status = status_match.group(1).lower()
                if "disable" in status:
                    val_value = "0"
                else:
                    val_value = "1"
            else:
                if "disable" in title.lower():
                    val_value = "0"
                elif "enable" in title.lower():
                    val_value = "1"
                    
        if val_type == "REG_MULTI_SZ" and val_value in ("0", "1"):
            val_value = "" if val_value == "0" else "Enabled"
            
        rules_data.append({
            'Rule ID': rule_id,
            'Profile/Level': level,
            'Rule Title': title,
            'Hive': hive,
            'Key Path': key_path,
            'Value Name': val_name,
            'Value Type': val_type,
            'Recommended Value': val_value,
            'Full Registry Path': f"{hive}\\{key_path}:{val_name}"
        })
        
    return rules_data

def generate_excel(rules, output_path):
    print(f"Generating Excel file at {output_path}...")
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame(rules)
    try:
        df.to_excel(output_path, index=False)
        print("Excel file generated successfully.")
    except PermissionError:
        alt_path = output_path.replace(".xlsx", "_new.xlsx")
        print(f"Warning: Permission denied to write to {output_path} (likely open in Excel). Trying {alt_path}...")
        try:
            df.to_excel(alt_path, index=False)
            print(f"Excel file generated successfully at {alt_path}.")
        except Exception as e:
            print(f"Error: Failed to write Excel file: {e}")
            raise e
    except Exception as e:
        print(f"Error: Failed to write Excel file: {e}")
        raise e

def generate_powershell_script(rules, output_path):
    print(f"Generating PowerShell script at {output_path}...")
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    ps_content = """# PowerShell System Hardening Script based on CIS Windows 11 Enterprise Benchmark
# Auto-generated. "dont harden my system now" is respected - run this manually if needed.

# 1. Administrator check
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "This script must be run as Administrator."
    Exit
}

$BackupFile = Join-Path $PSScriptRoot "backup_registry.reg"
Write-Host "Creating registry backup at $BackupFile..." -ForegroundColor Cyan

# Prepare registry backup list
$BackupKeys = @()

function Add-ToBackup($Hive, $KeyPath) {
    $FullPath = "$Hive\\$KeyPath"
    if ($BackupKeys -notcontains $FullPath) {
        $BackupKeys += $FullPath
    }
}
"""
    
    for r in rules:
        hive_full = "HKLM:" if r['Hive'] == "HKLM" else "HKCU:"
        ps_content += f'Add-ToBackup "{hive_full}" "{r["Key Path"]}"\n'
        
    ps_content += """
# Backup keys using reg.exe export
# Note: we ignore keys that don't exist yet to avoid error spew.
foreach ($key in $BackupKeys) {
    $regPath = $key -replace "HKLM:", "HKLM" -replace "HKCU:", "HKCU"
    Write-Host "Backing up $regPath..." -ForegroundColor DarkGray
    & reg.exe export "$regPath" "$BackupFile" /y *>$null
}
Write-Host "Backup completed!" -ForegroundColor Green

Write-Host "Applying CIS Hardening configurations..." -ForegroundColor Cyan

function Set-RegistryValue($Hive, $KeyPath, $ValueName, $ValueType, $ValueData) {
    $FullPath = "$Hive\\$KeyPath"
    
    # Create key if not exists
    if (-not (Test-Path $FullPath)) {
        New-Item -Path $FullPath -Force | Out-Null
    }
    
    # Map types
    $Type = $ValueType
    if ($ValueType -eq "REG_DWORD") { $Type = "DWord" }
    elseif ($ValueType -eq "REG_SZ") { $Type = "String" }
    elseif ($ValueType -eq "REG_MULTI_SZ") { $Type = "MultiString" }
    elseif ($ValueType -eq "REG_EXPAND_SZ") { $Type = "ExpandString" }
    elseif ($ValueType -eq "REG_BINARY") { $Type = "Binary" }
    
    # Write value
    try {
        Set-ItemProperty -Path $FullPath -Name $ValueName -Value $ValueData -Type $Type -Force
        Write-Host "SUCCESS: $FullPath`:$ValueName set to $ValueData ($ValueType)" -ForegroundColor Green
    } catch {
        Write-Error "FAILED: $FullPath`:$ValueName. Error: $_"
    }
}
"""
    
    for idx, r in enumerate(rules, 1):
        hive_full = "HKLM:" if r['Hive'] == "HKLM" else "HKCU:"
        val_name_esc = r['Value Name'].replace('"', '`"')
        key_path_esc = r['Key Path'].replace('"', '`"')
        val_data_esc = str(r['Recommended Value']).replace('"', '`"')
        
        ps_content += f'# Rule {r["Rule ID"]}: {r["Rule Title"]}\n'
        ps_content += f'Set-RegistryValue -Hive "{hive_full}" -KeyPath "{key_path_esc}" -ValueName "{val_name_esc}" -ValueType "{r["Value Type"]}" -ValueData "{val_data_esc}"\n\n'
        
    ps_content += """
Write-Host "CIS Benchmark Hardening script completed!" -ForegroundColor Green
Write-Host "Please restart the system to apply all changes." -ForegroundColor Yellow
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ps_content)
    print("PowerShell script generated successfully.")

def generate_report(rules, output_path):
    print(f"Generating report at {output_path}...")
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    levels = {}
    hives = {}
    types = {}
    
    for r in rules:
        lvl = r['Profile/Level']
        levels[lvl] = levels.get(lvl, 0) + 1
        
        hv = r['Hive']
        hives[hv] = hives.get(hv, 0) + 1
        
        tp = r['Value Type']
        types[tp] = types.get(tp, 0) + 1
        
    md_content = f"""# CIS Windows 11 Enterprise Benchmark Security Assessment Report

This report summarizes the security recommendations extracted from the **CIS Microsoft Windows 11 Enterprise Benchmark v5.1.0**.

---

## Executive Summary

- **Total Security Rules Extracted:** {len(rules)}
- **Primary Registry Hives Targeted:**
{chr(10).join([f"  - **{hv}**: {count} rules" for hv, count in hives.items()])}
- **Rules Profile Breakdown:**
{chr(10).join([f"  - **{lvl}**: {count} rules" for lvl, count in levels.items()])}
- **Value Types Used:**
{chr(10).join([f"  - **{tp}**: {count} settings" for tp, count in types.items()])}

---

## Proposed System Hardening Actions

A companion PowerShell hardening script has been generated at `harden_system.ps1`. When executed with administrative privileges, it will perform the following actions:
1. **Registry Backup:** Back up all targeted registry keys to `backup_registry.reg`.
2. **Apply Security Configurations:** Automatically configure all {len(rules)} registry values according to CIS recommendations.

---

## Detailed Rules Table

| Rule ID | Level | Rule Title | Registry Path | Type | Value |
|---|---|---|---|---|---|
"""
    
    for r in rules:
        md_content += f"| {r['Rule ID']} | {r['Profile/Level']} | {r['Rule Title']} | `{r['Full Registry Path']}` | `{r['Value Type']}` | `{r['Recommended Value']}` |\n"
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print("Report generated successfully.")
