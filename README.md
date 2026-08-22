# **Digi Samurai - Windows Security Auditor & Hardener**

A robust, premium, high-contrast security framework to assess, audit, and enhance Windows system security according to the **CIS Microsoft Windows 11 Enterprise Benchmark v5.1.0**.

---

## **Folder Structure**

```
D:\Project\System-Security-Benchmark
├── src/                               # Core Python logic modules
│   ├── benchmark_parser.py            # High-fidelity PDF extraction and rule mapping
│   ├── dashboard.py                   # Matplotlib dashboard plotting routines
│   └── dashboard_handel.py            # Data preprocessing and category sorting
├── ui/                                # PySide6 Graphical User Interface layouts
│   ├── audit_ui.ui / audit_ui.py      # Main window UI structure
│   └── splash_ui.ui / splash_ui.py    # Splash screen UI structure
├── outputs/                           # Active audit output files
│   ├── download.log                   # Connection logs for dynamic downloading
│   └── extracted_registry_lines_serialized.csv  # CSV database of parsed benchmark lines
├── dist/                              # Standalone packaged executables
│   └── System_Security.exe            # Standalone single-file executable
├── System_Security.py                 # Main Graphical User Interface (GUI) entry point
├── requirements.txt                   # Dependency list
└── LICENSE                            # License details
```

*Note: All intermediate cache files (`technologies.json`, `benchmarks_<id>.json`), downloaded PDFs, and report exports (`harden_system.ps1`, `CIS_Windows_11_Hardening_Rules.xlsx`, `hardening_report.md`) are saved directly inside the system's temporary directory (`tempfile.gettempdir()`) to prevent workspace pollution.*

---

## **Standalone Executable (.exe)**

The application is pre-packaged as a single, standalone executable that requests administrative permissions automatically:

### **Run Standalone:**
Launch **`dist/System_Security.exe`** directly from anywhere. 
* All libraries (Matplotlib, PySide6, pandas, curl_cffi, pdfminer) are bundled in this single file.
* It automatically triggers the Windows UAC (User Account Control) prompt to run with Administrator privileges, which are required to write and apply registry hardening.

### **Compile From Source:**
To compile the executable yourself:
1. Ensure the virtual environment is activated.
2. Install PyInstaller:
   ```powershell
   pip install pyinstaller
   ```
3. Run the compiler:
   ```powershell
   pyinstaller --onefile --noconsole --uac-admin System_Security.py
   ```
The compiled output will be available under `dist/System_Security.exe`. You can safely delete the generated `build/` folder and `System_Security.spec` configuration file.

---

## **Developer Installation**

### **Prerequisites**
Ensure you have Python 3.12+ installed. The project runs in a localized virtual environment (`venv`).

### **Activation & Dependencies**
To activate the virtual environment and install dependencies:
1. Open PowerShell in the project directory.
2. Run the activation script:
   ```powershell
   .\venv\Scripts\activate
   ```
3. Install required packages:
   ```powershell
   pip install -r requirements.txt
   ```

### **Compiling UI Layouts**
If you modify the Qt Designer `.ui` layout files in the `ui/` directory, recompile them to Python modules:
```powershell
pyside6-uic .\ui\audit_ui.ui -o .\ui\audit_ui.py
pyside6-uic .\ui\splash_ui.ui -o .\ui\splash_ui.py
```

---

## **How to Run (Source)**

Launch the interactive PySide6 desktop auditor:
```powershell
# Active virtual environment:
python System_Security.py

# Direct invocation via venv:
.\venv\Scripts\python.exe System_Security.py
```

---

## **GUI Features**

1. **Source Toggles:** Choose between "Use Local CIS PDF File" (local file search) and "Download CIS PDF Online" (automated fetching from the web).
2. **Dynamic Search & Filtering:** Downloads online benchmark databases matching your system, automatically searching and filtering for the `"windows"` and `"desktop"` keywords.
3. **Select Hive:** Select the target registry hive (e.g. `HKEY_LOCAL_MACHINE`) from the dropdown.
4. **Download Confirmation & Verification:** When selecting the online downloader, the application guides you through downloading the file, prompts a verification file dialog, and reminds you to choose a registry hive before activating the Submit button.
5. **Session Authorization Required Fallback:** If connection logs indicate authorization blockages, a helper prompt allows you to open the link directly in Chrome or paste your `laravel_session` cookie to bypass authentication restrictions.
6. **Submit (Audit):** Click the bottom `Submit` button to run an audit scanning your host system's current registry.
7. **Interactive Dashboard:** Click the `Dashboard` button to view high-contrast Matplotlib graphs. The charts utilize separate color palettes (Emerald/Maroon for Pie, Teal/Indigo for Systems, Lime/Rose for Software) to offer clear visual differentiation.
8. **Hardening Checkboxes:** Select the desired rules and click `Hardening` to generate checkboxes for individual settings, allowing you to selectively generate hardening steps.
9. **Registry Hardening Execution:** Apply your selected hardening configurations directly to the system registry through Python's native `winreg` wrapper.
10. **Backup Registry:** Click `Backup Registry` next to the Cancel/Submit buttons to generate a standard `.reg` file backup containing either the targeted CIS registry keys (if parsed) or the complete system security hives (as a fallback). You can select your desired save path.