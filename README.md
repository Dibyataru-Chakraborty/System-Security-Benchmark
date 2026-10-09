# **Risk Nexus - Windows Security Auditor & Hardener**

> **Enterprise CIS Security Benchmark Hardening, Compliance & Remediation Platform**  
> **Created By: Dibyataru Chakraborty**

---

## **Overview**

**Risk Nexus** is an enterprise-grade cybersecurity audit and compliance platform designed to assess, audit, remediate, and harden Windows operating systems against official **CIS (Center for Internet Security) Benchmarks**.

With support for both local PDF benchmark files and live online benchmark downloads directly from the CIS repository, **Risk Nexus** provides a fast, dynamic, and non-hardcoded evaluation engine with multi-format reporting (Excel, CSV, `.reg` Registry Backups).

---

## **Key Features**

1. **Dual Network Dashboard (Localhost & LAN)**:
   - Built on a lightweight, high-performance web dashboard running on `0.0.0.0:5000`.
   - Accessible locally (`http://127.0.0.1:5000`) or from any browser across your local network (`http://<local_ip>:5000`).

2. **Automated CIS Online Benchmark Downloader**:
   - Integrated Chrome TLS fingerprint impersonation (`curl_cffi`) to dynamically discover technologies, list benchmark versions, and download official CIS PDF documents.

3. **100% Dynamic Chunk-Based PDF Parsing**:
   - Zero hardcoded maps or rule dictionaries. 
   - Dynamically parses rule IDs, profile levels (Level 1, Level 2, Next Gen), severity levels, registry hives, key paths, value names, types, and recommended values directly from document text.

4. **Live Host Registry Auditing**:
   - Fast, native scanning against multiple registry hives (`HKEY_LOCAL_MACHINE`, `HKEY_CURRENT_USER`, `HKEY_CLASSES_ROOT`, `HKEY_USERS`, `HKEY_CURRENT_CONFIG`).
   - Normalizes and verifies DWORD, String, MultiString, ExpandString, and Binary keys.

5. **Visual Analytics & Category Intelligence**:
   - Real-time Chart.js visual telemetry for compliance score, pass/fail ratios, system vs software path categories, and subcategory breakdown.

6. **Selective Hardening & Automated Remediation**:
   - Review failed benchmarks and selectively apply recommended security hardening values directly to the Windows registry with a single click.

7. **Safety-First Registry Backup**:
   - Automatically exports standard `.reg` backup files prior to remediation for instant rollback.

8. **Enterprise Excel & CSV Reporting**:
   - Generates beautifully styled multi-sheet Excel workbooks (`.xlsx`) featuring Executive Summaries, KPI cards, profile level breakdowns, detailed audit logs, and actionable PowerShell / Reg.exe commands.

---

## **Folder Structure**

```
D:\Project\System-Security-Benchmark
├── src/                               # Core Python logic modules
│   ├── benchmark_parser.py            # Dynamic PDF rule & metadata extraction engine
│   ├── excel_exporter.py              # Multi-sheet enterprise Excel report generator
│   ├── server.py                      # Flask REST API and web application server
│   └── dashboard_handel.py            # Analytics and telemetry category processor
├── static/                            # Frontend assets (Tailwind, Lucide, Chart.js, styles)
│   ├── app.js                         # Dynamic UI state manager and API bridge
│   ├── styles.css                     # Custom styles and scrollbar overrides
│   └── DigiSamurai.png                # Platform icon / branding asset
├── templates/                         # HTML Templates
│   └── index.html                     # Single-page executive dashboard interface
├── outputs/                           # Generated audit reports, logs, and backups
├── dist/                              # Standalone packaged executables
│   └── Risk_Nexus.exe                 # Single-file standalone executable
├── app.py                             # Primary application launcher
├── Risk_Nexus.py                      # Core entrypoint script
├── requirements.txt                   # Dependency list
└── README.md                          # Platform documentation
```

---

## **Installation & Setup**

### **Prerequisites**
- Windows 10 / 11 / Windows Server (x64)
- Python 3.12+ (for running from source)

### **1. Clone Repository**
```powershell
git clone https://github.com/Dibyataru-Chakraborty/System-Security-Benchmark.git
cd System-Security-Benchmark
```

### **2. Set Up Virtual Environment**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### **3. Install Dependencies**
```powershell
pip install -r requirements.txt
```

---

## **Running Risk Nexus**

### **Run from Source**
```powershell
# Launch with Python (Administrator recommended for remediation):
python Risk_Nexus.py
```
*The application will automatically detect your local network IP and open your default browser to `http://127.0.0.1:5000`.*

---

## **Compiling Standalone Executable (.exe)**

To build a clean, single-file executable (`dist/Risk_Nexus.exe`) with administrator elevation:

```powershell
.\venv\Scripts\pyinstaller.exe --onefile --name Risk_Nexus --uac-admin --add-data "templates;templates" --add-data "static;static" --add-data "src;src" --hidden-import "curl_cffi" --hidden-import "openpyxl" --hidden-import "flask" --hidden-import "pdfminer" --hidden-import "pdfminer.high_level" --hidden-import "pdfminer.layout" --hidden-import "pandas" --collect-all "curl_cffi" --collect-all "openpyxl" --collect-all "pdfminer" --exclude-module "PySide6" --exclude-module "shiboken6" --exclude-module "matplotlib" --exclude-module "tkinter" --clean Risk_Nexus.py
```

---

## **Author & Credits**

- **Author / Developer**: **Dibyataru Chakraborty**
- **Platform**: **Risk Nexus Security Benchmark Suite**
- **License**: MIT License