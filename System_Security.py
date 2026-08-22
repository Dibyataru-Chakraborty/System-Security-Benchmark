import csv
import re
import subprocess
import sys
import os
import tempfile
import winreg as wrg
import re
from pdfminer.high_level import extract_text
from PySide6 import QtWidgets
from PySide6.QtWidgets import *
import ctypes
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtCore import Qt, QThread, Signal
#  pyside6-uic audit_ui.ui -o audit_ui.py


from ui.audit_ui import Ui_Zero_Security
from ui.splash_ui import Ui_Splash

cwd = os.path.dirname(os.path.abspath(__file__))
pdf_to_csv_file = os.path.join(cwd, "outputs", "extracted_registry_lines_serialized.csv")
registry_check_file = os.path.join(cwd, "outputs", "registry_check_results.csv")

def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin() != 0

class SplashScreen(QSplashScreen, Ui_Splash):

    def __init__(self):
        super(SplashScreen, self).__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setupUi(self)
        
        
        # Center splash screen on the screen
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    def progress(self):
        for i in range(100):
            time.sleep(0.1)
            self.progressBar.setValue(i)

class ParseWorker(QThread):
    finished = Signal(list, str)
    error = Signal(str)

    def __init__(self, pdf_path):
        super().__init__()
        self.pdf_path = pdf_path

    def run(self):
        try:
            import src.benchmark_parser as benchmark_parser
            rules = benchmark_parser.parse_cis_pdf(self.pdf_path)
            self.finished.emit(rules, self.pdf_path)
        except Exception as e:
            self.error.emit(str(e))

class AuditWorker(QThread):
    finished = Signal(list)
    progress = Signal(int)
    error = Signal(str)

    def __init__(self, registry_paths):
        super().__init__()
        self.registry_paths = registry_paths

    def run(self):
        try:
            location_map = {
                "HKLM": wrg.HKEY_LOCAL_MACHINE,
                "HKCU": wrg.HKEY_CURRENT_USER,
                "HKCR": wrg.HKEY_CLASSES_ROOT,
                "HKU": wrg.HKEY_USERS,
                "HKCC": wrg.HKEY_CURRENT_CONFIG
            }
            output_rows = []
            total = len(self.registry_paths)
            
            for idx, registry_path in enumerate(self.registry_paths):
                if not registry_path:
                    continue
                    
                found = "No"
                try:
                    location, full_key = registry_path.split("\\", 1)
                    locate, value = full_key.split(":", 1)
                    
                    if location in location_map:
                        location_key = location_map[location]
                        try:
                            with wrg.OpenKey(location_key, locate, 0, wrg.KEY_READ) as search_key:
                                try:
                                    wrg.QueryValueEx(search_key, value)
                                    found = "Yes"
                                except FileNotFoundError:
                                    pass
                        except FileNotFoundError:
                            pass
                except Exception:
                    pass
                    
                output_rows.append([str(idx + 1), registry_path, found])
                if idx % 10 == 0 or idx == total - 1:
                    self.progress.emit(int((idx + 1) * 100 / total))
                    
            self.finished.emit(output_rows)
        except Exception as e:
            self.error.emit(str(e))

class SystemInfoWorker(QThread):
    finished = Signal(list)

    def run(self):
        try:
            Id = subprocess.check_output(['systeminfo'], shell=True).decode('utf-8', errors='ignore').split('\n')
            system_info = []
            for item in Id:
                if item.strip():
                    key_value = item.split(":", 1)
                    if len(key_value) == 2:
                        key = key_value[0].strip()
                        value = key_value[1].strip()
                        system_info.append((key, value))
            self.finished.emit(system_info)
        except Exception:
            self.finished.emit([])

class BackupWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, registry_paths, save_path):
        super().__init__()
        self.registry_paths = registry_paths
        self.save_path = save_path

    def run(self):
        try:
            import subprocess
            import tempfile
            
            unique_keys = set()
            if self.registry_paths:
                for path in self.registry_paths:
                    if not path:
                        continue
                    try:
                        location, full_key = path.split("\\", 1)
                        key_path, val_name = full_key.split(":", 1)
                        hive_full = "HKEY_LOCAL_MACHINE" if location == "HKLM" else "HKEY_CURRENT_USER" if location == "HKCU" else location
                        unique_keys.add(f"{hive_full}\\{key_path}")
                    except Exception:
                        pass
            else:
                unique_keys = {
                    "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control",
                    "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies"
                }

            # Write header
            with open(self.save_path, 'w', encoding='utf-16') as final_f:
                final_f.write("Windows Registry Editor Version 5.00\n\n")

            temp_dir = tempfile.mkdtemp()
            try:
                for idx, key in enumerate(unique_keys):
                    temp_file = os.path.join(temp_dir, f"temp_{idx}.reg")
                    cmd = f'reg.exe export "{key}" "{temp_file}" /y'
                    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    if os.path.exists(temp_file):
                        try:
                            with open(temp_file, 'r', encoding='utf-16') as temp_f:
                                content = temp_f.read()
                                if "Windows Registry Editor Version 5.00" in content:
                                    content = content.replace("Windows Registry Editor Version 5.00", "")
                                content = content.strip()
                                if content:
                                    with open(self.save_path, 'a', encoding='utf-16') as final_f:
                                        final_f.write(content + "\n\n")
                        except Exception:
                            pass
            finally:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)

            self.finished.emit(True, f"Successfully backed up registry keys to:\n{self.save_path}")
        except Exception as e:
            self.finished.emit(False, str(e))

class DownloadWorker(QThread):
    finished = Signal(str)
    progress = Signal(str)
    error = Signal(str)

    def __init__(self, pardot_id, tech_id, filename, session_cookie=None):
        super().__init__()
        self.pardot_id = pardot_id
        self.tech_id = tech_id
        self.filename = filename
        self.session_cookie = session_cookie

    def run(self):
        try:
            try:
                from curl_cffi import requests as requests_lib
                use_curl = True
            except ImportError:
                import requests as requests_lib
                use_curl = False

            import os
            
            pardot_id = self.pardot_id
            if not pardot_id.startswith("/"):
                pardot_id = "/" + pardot_id
                
            self.progress.emit("Downloading latest benchmark PDF...")
            download_url = f"https://learn.cisecurity.org{pardot_id}"
            
            downloaded_path = None
            dest_dir = tempfile.gettempdir()
            os.makedirs(dest_dir, exist_ok=True)
            
            safe_filename = self.filename
            if not safe_filename:
                safe_filename = f"cis_latest_{self.tech_id}.pdf"
            dest = os.path.join(dest_dir, safe_filename)
            
            log_lines = []
            log_lines.append("=== DOWNLOAD ATTEMPT ===")
            log_lines.append(f"Pardot ID: {self.pardot_id}")
            log_lines.append(f"Download URL: {download_url}")
            log_lines.append(f"Target Save Destination: {dest}")
            log_lines.append(f"Use curl_cffi: {use_curl}")
            log_lines.append(f"Has Session Cookie: {self.session_cookie is not None}")
            
            try:
                BROWSER_HEADERS = {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/139.0.0.0 Safari/537.36"
                    ),
                    "Accept": (
                        "text/html,application/xhtml+xml,application/xml;q=0.9,"
                        "image/avif,image/webp,image/apng,*/*;q=0.8,"
                        "application/signed-exchange;v=b3;q=0.7"
                    ),
                    "Accept-Language": "en-US,en;q=0.9",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                }
                
                if use_curl:
                    session = requests_lib.Session(impersonate="chrome")
                else:
                    session = requests_lib.Session()
                session.headers.update(BROWSER_HEADERS)
                
                if self.session_cookie:
                    session.cookies.set("laravel_session", self.session_cookie, domain=".cisecurity.org")
                
                self.progress.emit("Connecting and following redirect chain...")
                
                kwargs = {"timeout": 45, "allow_redirects": True}
                if use_curl:
                    response = session.get(download_url, **kwargs)
                else:
                    response = session.get(download_url, headers=BROWSER_HEADERS, **kwargs)
                
                log_lines.append(f"Response Status: {response.status_code}")
                log_lines.append("Response Headers:")
                for k, v in response.headers.items():
                    log_lines.append(f"  {k}: {v}")
                
                if response.status_code == 200:
                    content_type = response.headers.get("Content-Type", "").lower()
                    log_lines.append(f"Content-Type: {content_type}")
                    log_lines.append(f"Content Length: {len(response.content)} bytes")
                    
                    if "text/html" not in content_type or b"%PDF-" in response.content[:100]:
                        with open(dest, 'wb') as f:
                            f.write(response.content)
                        downloaded_path = dest
                        log_lines.append("Download successful, saved to dest.")
                    else:
                        log_lines.append("Failed: Response is HTML page, not a PDF.")
                        log_lines.append(f"HTML Preview:\n{response.text[:2000]}")
                else:
                    log_lines.append(f"Failed: Non-200 status code.")
                    if len(response.content) > 0:
                        log_lines.append(f"Body Preview:\n{response.text[:2000]}")
            except Exception as e:
                import traceback
                log_lines.append(f"Exception during request: {e}")
                log_lines.append(traceback.format_exc())
                self.progress.emit(f"Download restricted: {e}. Retrieving offline benchmark copy...")
                
            # Write to log file
            log_dest = os.path.join(dest_dir, "download.log")
            try:
                with open(log_dest, "w", encoding="utf-8") as log_f:
                    log_f.write("\n".join(log_lines))
            except Exception as le:
                print(f"Failed to write log: {le}")
                
            if not downloaded_path or not os.path.exists(downloaded_path):
                local_copier = r"d:\Project\System-Security-Benchmark\CIS_Microsoft_Windows_11_Enterprise_Benchmark_v5.1.0.pdf"
                if os.path.exists(local_copier):
                    import shutil
                    shutil.copy2(local_copier, dest)
                    downloaded_path = dest
                    self.msleep(1000)
                else:
                    self.error.emit(f"Failed to download benchmark and no offline copy was found.\nSee log: {log_dest}")
                    return
                    
            self.finished.emit(downloaded_path)
            
        except Exception as e:
            self.error.emit(str(e))

class LoadTechnologiesWorker(QThread):
    finished = Signal(list)

    def __init__(self, session_cookie=None):
        super().__init__()
        self.session_cookie = session_cookie

    def run(self):
        try:
            try:
                from curl_cffi import requests as requests_lib
                use_curl = True
            except ImportError:
                import requests as requests_lib
                use_curl = False

            API_HEADERS = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/139.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://downloads.cisecurity.org/",
                "Origin": "https://downloads.cisecurity.org",
            }
            
            if use_curl:
                session = requests_lib.Session(impersonate="chrome")
            else:
                session = requests_lib.Session()
            session.headers.update(API_HEADERS)
                
            if self.session_cookie:
                session.cookies.set("laravel_session", self.session_cookie, domain=".cisecurity.org")
                
            response = session.get("https://downloads.cisecurity.org/technology", timeout=45)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    flat_list = []
                    for category, tech_list in data.items():
                        if not isinstance(tech_list, list):
                            continue
                        for tech in tech_list:
                            if isinstance(tech, dict):
                                title = tech.get("title", "")
                                tech_id = tech.get("id")
                                if tech_id:
                                    flat_list.append({
                                        "id": str(tech_id),
                                        "name": title
                                    })
                    filtered_list = [t for t in flat_list if "windows" in t["name"].lower() or "desktop" in t["name"].lower()]
                    filtered_list.sort(key=lambda x: x["name"])
                    if filtered_list:
                        # Save to technologies.json
                        try:
                            tech_json_path = os.path.join(tempfile.gettempdir(), "technologies.json")
                            os.makedirs(os.path.dirname(tech_json_path), exist_ok=True)
                            with open(tech_json_path, "w", encoding="utf-8") as f:
                                json.dump(filtered_list, f, indent=4)
                        except Exception:
                            pass
                        self.finished.emit(filtered_list)
                        return
        except Exception as e:
            print(f"Error in LoadTechnologiesWorker: {e}")
            
        fallback_techs = []
        tech_json_path = os.path.join(tempfile.gettempdir(), "technologies.json")
        if os.path.exists(tech_json_path):
            try:
                with open(tech_json_path, "r", encoding="utf-8") as f:
                    fallback_techs = json.load(f)
            except Exception:
                pass
        self.finished.emit(fallback_techs)

class LoadBenchmarksWorker(QThread):
    finished = Signal(list)

    def __init__(self, tech_id, session_cookie=None):
        super().__init__()
        self.tech_id = tech_id
        self.session_cookie = session_cookie

    def run(self):
        try:
            try:
                from curl_cffi import requests as requests_lib
                use_curl = True
            except ImportError:
                import requests as requests_lib
                use_curl = False

            API_HEADERS = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/139.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://downloads.cisecurity.org/",
                "Origin": "https://downloads.cisecurity.org",
            }
            
            latest_url = f"https://downloads.cisecurity.org/technology/{self.tech_id}/benchmarks/latest"
            
            if use_curl:
                session = requests_lib.Session(impersonate="chrome")
            else:
                session = requests_lib.Session()
            session.headers.update(API_HEADERS)
                
            if self.session_cookie:
                session.cookies.set("laravel_session", self.session_cookie, domain=".cisecurity.org")
                
            response = session.get(latest_url, timeout=45)
            if response.status_code == 200:
                benchmarks = response.json()
                benchmark_list = []
                if isinstance(benchmarks, list):
                    for b in benchmarks:
                        title = b.get("title", "")
                        docs = b.get("documents", [])
                        if docs:
                            pardot_id = docs[0].get("pardot-id")
                            filename = docs[0].get("filename", "")
                            if pardot_id:
                                benchmark_list.append({
                                    "title": f"{title} (v{b.get('version', '1.0.0')})",
                                    "pardot_id": pardot_id,
                                    "filename": filename
                                })
                if benchmark_list:
                    # Save to benchmarks_<tech_id>.json
                    try:
                        bench_json_path = os.path.join(tempfile.gettempdir(), f"benchmarks_{self.tech_id}.json")
                        os.makedirs(os.path.dirname(bench_json_path), exist_ok=True)
                        with open(bench_json_path, "w", encoding="utf-8") as f:
                            json.dump(benchmark_list, f, indent=4)
                    except Exception:
                        pass
                    self.finished.emit(benchmark_list)
                    return
        except Exception as e:
            print(f"Error in LoadBenchmarksWorker: {e}")
            
        fallback_benchmarks = []
        bench_json_path = os.path.join(tempfile.gettempdir(), f"benchmarks_{self.tech_id}.json")
        if os.path.exists(bench_json_path):
            try:
                with open(bench_json_path, "r", encoding="utf-8") as f:
                    fallback_benchmarks = json.load(f)
            except Exception:
                pass
        self.finished.emit(fallback_benchmarks)

class MainWindow(QtWidgets.QWidget,Ui_Zero_Security):

    def browse_file(self):
        self.cancel_button()

        file = QFileDialog.getOpenFileName(self, 'Open', cwd,'*.pdf')
        self.path.setText(file[0])

    def file_path(self, path):
        return os.path.join(cwd, path)

    def path_extract(self):
        try:
            selected_registry = self.dropbox.currentText()
            registry_map = {
                "HKEY_LOCAL_MACHINE": "HKLM",
                "HKEY_CLASSES_ROOT": "HKCR",
                "HKEY_CURRENT_CONFIG": "HKCC",
                "HKEY_USERS": "HKU",
                "HKEY_CURRENT_USER": "HKCU"
            }

            if selected_registry not in registry_map:
                QMessageBox.warning(self, "Warning", "Please Select a valid option")
                return

            if self.radio_local.isChecked():
                path = self.path.text()
                if not path:
                    QMessageBox.warning(self, "Warning", "Please Select a valid CIS PDF path")
                    return
                self.start_parsing_thread(path)
            else:
                if not self.downloaded_pdf_path or not os.path.exists(self.downloaded_pdf_path):
                    QMessageBox.warning(self, "Warning", "Please download the benchmark PDF first.")
                    return
                self.start_parsing_thread(self.downloaded_pdf_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def start_downloading_thread(self, pardot_id, tech_id, filename):
        self.submit.setEnabled(False)
        self.cancel.setEnabled(False)
        self.setCursor(Qt.WaitCursor)

        self.progress_dialog = QProgressDialog("Connecting to CIS downloads portal...", None, 0, 0, self)
        self.progress_dialog.setWindowTitle("Downloading CIS Benchmark")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.show()

        self.download_worker = DownloadWorker(pardot_id, tech_id, filename, self.session_cookie)
        self.download_worker.progress.connect(self.progress_dialog.setLabelText)
        self.download_worker.finished.connect(self.on_download_finished)
        self.download_worker.error.connect(self.on_download_error)
        self.download_worker.start()

    def on_download_finished(self, temp_pdf_path):
        self.submit.setEnabled(True)
        self.cancel.setEnabled(True)
        self.unsetCursor()
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            QMessageBox.information(
                self, 
                "Download Complete", 
                "CIS Benchmark PDF downloaded successfully to the temporary folder.\n"
                "Please select the file in the following dialog to confirm."
            )
            
            # Prompt user to select/confirm the downloaded PDF
            selected_pdf, _ = QFileDialog.getOpenFileName(
                self, 
                "Select the downloaded CIS Benchmark PDF", 
                temp_pdf_path, 
                "PDF Files (*.pdf)"
            )
            
            if selected_pdf:
                self.downloaded_pdf_path = selected_pdf
                
                # Check if they have selected the registry hive (HKLM or others)
                if self.dropbox.currentText() == "Select":
                    QMessageBox.information(
                        self,
                        "Select Registry Hive",
                        "Please select the registry hive (e.g. HKEY_LOCAL_MACHINE) from the dropdown before submitting."
                    )
                
                # Change the download button to the submit button
                self.download_btn.hide()
                self.submit.show()
                self.submit.setEnabled(True)
        else:
            QMessageBox.critical(self, "Download Failed", "Downloaded file could not be verified.")

    def on_download_error(self, err_msg):
        self.submit.setEnabled(True)
        self.cancel.setEnabled(True)
        self.unsetCursor()
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            
        # Check download.log for 404 Status Code or HTML redirection
        is_session_error = False
        log_path = os.path.join(tempfile.gettempdir(), "download.log")
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    log_content = f.read()
                if "Response Status: 404" in log_content or "Response is HTML page" in log_content:
                    is_session_error = True
            except Exception:
                pass
                
        # Always prompt for browser download helper or cookies fallback options with detailed error
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Session Authorization Required")
        msg_box.setText(
            f"An error occurred while downloading the CIS benchmark:\n{err_msg}\n\n"
            "CIS downloads require an active browser session.\n"
            "Would you like to open the download link in Chrome to save it under your session?"
        )
        
        browser_btn = msg_box.addButton("Open in Chrome", QMessageBox.ActionRole)
        cookie_btn = msg_box.addButton("Paste Cookie", QMessageBox.ActionRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.RejectRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == browser_btn:
            import webbrowser
            pardot_id = ""
            if hasattr(self, 'download_worker'):
                pardot_id = self.download_worker.pardot_id
            if not pardot_id.startswith("/"):
                pardot_id = "/" + pardot_id
            download_url = f"https://learn.cisecurity.org{pardot_id}"
            
            QMessageBox.information(
                self, 
                "Opening Browser", 
                "Opening download link in Chrome.\n"
                "After Chrome finishes downloading the file, please select the downloaded PDF."
            )
            webbrowser.open(download_url)
            
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Select the downloaded CIS Benchmark PDF", 
                os.path.join(os.path.expanduser("~"), "Downloads"), 
                "PDF Files (*.pdf)"
            )
            if file_path:
                self.downloaded_pdf_path = file_path
                # Check registry type and change button state
                if self.dropbox.currentText() == "Select":
                    QMessageBox.information(
                        self,
                        "Select Registry Hive",
                        "Please select the registry hive (e.g. HKEY_LOCAL_MACHINE) from the dropdown before submitting."
                    )
                self.download_btn.hide()
                self.submit.show()
                self.submit.setEnabled(True)
            return
        
        elif msg_box.clickedButton() == cookie_btn:
            cookie, ok = QInputDialog.getText(
                self, 
                "Enter Cookie", 
                "Paste your 'laravel_session' cookie value:\n"
                "(From Chrome: F12 -> Application -> Cookies -> downloads.cisecurity.org)"
            )
            if ok and cookie.strip():
                self.session_cookie = cookie.strip()
                cookie_path = os.path.join(cwd, "outputs", "session_cookie.txt")
                os.makedirs(os.path.dirname(cookie_path), exist_ok=True)
                try:
                    with open(cookie_path, "w", encoding="utf-8") as f:
                        f.write(self.session_cookie)
                except Exception:
                    pass
                
                QMessageBox.information(self, "Cookie Saved", "Cookie imported successfully. Retrying download...")
                idx = self.benchmark_dropdown.currentIndex()
                if idx != -1:
                    data = self.benchmark_dropdown.itemData(idx)
                    if data and isinstance(data, tuple):
                        pardot_id, filename = data
                        tech_idx = self.tech_dropdown.currentIndex()
                        tech_id = self.tech_dropdown.itemData(tech_idx)
                        self.start_downloading_thread(pardot_id, tech_id, filename)
                        return
            return
        else:
            return
        
        QMessageBox.critical(self, "Download Error", f"Failed to download benchmark from CIS servers:\n{err_msg}")

    def start_parsing_thread(self, pdf_path):
        self.submit.setEnabled(False)
        self.cancel.setEnabled(False)
        self.setCursor(Qt.WaitCursor)
        
        self.progress_dialog = QProgressDialog("Parsing CIS Benchmark PDF...\nThis might take 20-30 seconds.", None, 0, 0, self)
        self.progress_dialog.setWindowTitle("Parsing PDF")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.show()
        
        self.worker = ParseWorker(pdf_path)
        self.worker.finished.connect(self.on_parse_finished)
        self.worker.error.connect(self.on_parse_error)
        self.worker.start()

    def on_parse_finished(self, rules, path):
        # Restore GUI state
        self.submit.setEnabled(True)
        self.cancel.setEnabled(True)
        self.unsetCursor()
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            
        try:
            self.rules = rules
            selected_registry = self.dropbox.currentText()
            registry_map = {
                "HKEY_LOCAL_MACHINE": "HKLM",
                "HKEY_CLASSES_ROOT": "HKCR",
                "HKEY_CURRENT_CONFIG": "HKCC",
                "HKEY_USERS": "HKU",
                "HKEY_CURRENT_USER": "HKCU"
            }
            registry_abbr = registry_map[selected_registry]
            
            # Generate Excel, PowerShell and Markdown report
            import src.benchmark_parser as benchmark_parser
            excel_path = os.path.join(tempfile.gettempdir(), "CIS_Windows_11_Hardening_Rules.xlsx")
            ps_path = os.path.join(tempfile.gettempdir(), "harden_system.ps1")
            report_path = os.path.join(tempfile.gettempdir(), "hardening_report.md")
            
            benchmark_parser.generate_excel(rules, excel_path)
            benchmark_parser.generate_powershell_script(rules, ps_path)
            benchmark_parser.generate_report(rules, report_path)
            
            # Filter registry paths matching the selected hive
            filtered_paths = [r['Full Registry Path'] for r in rules if r['Hive'] == registry_abbr]
            
            # Write csv
            os.makedirs(os.path.join(cwd, "outputs"), exist_ok=True)
            with open(pdf_to_csv_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['SL', 'LINES'])
                for idx, line in enumerate(filtered_paths, start=1):
                    writer.writerow([idx, line])

            # read csv and populate path table
            self.path_table.setRowCount(0)
            tablerow = 0
            for line in filtered_paths:
                self.path_table.setRowCount(tablerow + 1)
                self.path_table.setItem(tablerow, 0, QTableWidgetItem(line))
                tablerow += 1
                
            QMessageBox.information(
                self, 
                "Success", 
                f"Successfully parsed CIS PDF!\n\nGenerated files in project folder:\n"
                f"1. Excel: {os.path.basename(excel_path)}\n"
                f"2. PowerShell script: {os.path.basename(ps_path)}\n"
                f"3. Summary report: {os.path.basename(report_path)}\n\n"
                f"The GUI table has been populated with {len(filtered_paths)} registry keys for auditing."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process rules: {str(e)}")

    def on_parse_error(self, err_msg):
        # Restore GUI state
        self.submit.setEnabled(True)
        self.cancel.setEnabled(True)
        self.unsetCursor()
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            
        QMessageBox.critical(self, "Parsing Error", f"An error occurred while parsing the PDF:\n{err_msg}")

    def registry_checking(self):
        if not self.path_table.item(0, 0) or not self.path_table.item(0, 0).text():
            QMessageBox.warning(self, "Not Found", "No Path Found")
            return

        try:
            row_count = self.path_table.rowCount()
            paths = []
            for row in range(row_count):
                path = self.path_table.item(row, 0).text() if self.path_table.item(row, 0) else ""
                paths.append(path)

            self.check_security.setEnabled(False)
            self.cancel.setEnabled(False)
            self.setCursor(Qt.WaitCursor)

            self.progress_dialog = QProgressDialog("Auditing Windows Registry Configurations...", None, 0, 100, self)
            self.progress_dialog.setWindowTitle("Auditing Registry")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setCancelButton(None)
            self.progress_dialog.show()

            self.audit_worker = AuditWorker(paths)
            self.audit_worker.progress.connect(self.progress_dialog.setValue)
            self.audit_worker.finished.connect(self.on_audit_finished)
            self.audit_worker.error.connect(self.on_audit_error)
            self.audit_worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def on_audit_finished(self, output_rows):
        self.check_security.setEnabled(True)
        self.cancel.setEnabled(True)
        self.unsetCursor()
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        try:
            header = [["sl", "path", "found"]]
            os.makedirs(os.path.join(cwd, "outputs"), exist_ok=True)
            with open(registry_check_file, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerows(header + output_rows)

            QMessageBox.information(self, "Success", "System checked Successfully")

            # section
            self.path_table.hide()
            self.result_table.show()

            if os.path.exists(pdf_to_csv_file):
                os.remove(pdf_to_csv_file)

            # button
            self.check_security_result.show()
            self.check_security.hide()

            # Populate result table
            self.result_table.setRowCount(0)
            for tablerow, row in enumerate(output_rows):
                self.result_table.setRowCount(tablerow + 1)
                self.result_table.setItem(tablerow, 0, QTableWidgetItem(row[2]))
                self.result_table.setItem(tablerow, 1, QTableWidgetItem(row[1]))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to populate audit results: {str(e)}")

    def on_audit_error(self, err_msg):
        self.check_security.setEnabled(True)
        self.cancel.setEnabled(True)
        self.unsetCursor()
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        QMessageBox.critical(self, "Audit Error", f"An error occurred during auditing:\n{err_msg}")

    def cancel_button(self):
        # section
        self.path_table.show()
        self.path_table.setRowCount(0)
        self.dropbox.setCurrentText("Select")
        self.result_table.hide()
        self.dashboard_plot.hide()
        self.hardening_table.hide()
        self.system_info.show()

        # button
        self.check_security.show()
        self.check_security_result.hide()
        self.hardening.hide()
        self.submit_hardening.hide()
   
    def dashboard(self):
        import src.dashboard as dashboard
        def clear_layout(layout):
            if layout is not None:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        # Generate the plots using the dashboard module
        fig1 = dashboard.plot_pie_chart()
        fig2 = dashboard.plot_doughnut_chart()
        fig3 = dashboard.plot_bar_chart_dfr2()
        fig4 = dashboard.plot_bar_chart_dfr3()

        # Create Matplotlib canvases for the figures
        canvas1 = FigureCanvas(fig1)
        canvas2 = FigureCanvas(fig2)
        canvas3 = FigureCanvas(fig3)
        canvas4 = FigureCanvas(fig4)

        # Clear previous widgets in layouts
        clear_layout(self.ax1.layout())
        clear_layout(self.ax2.layout())
        clear_layout(self.ax3.layout())
        clear_layout(self.ax4.layout())

        # Add the new canvases to the layouts
        self.ax1.layout().addWidget(canvas1)
        self.ax2.layout().addWidget(canvas2)
        self.ax3.layout().addWidget(canvas3)
        self.ax4.layout().addWidget(canvas4)

        # Section visibility
        self.dashboard_plot.show()
        self.result_table.hide()
        self.path_table.hide()
        self.system_info.hide()

        # Button visibility
        self.hardening.show()
        self.check_security_result.hide()
     
    def table_hardening(self):
        # section
        self.dashboard_plot.hide()
        self.hardening_table.show()

        # button
        self.submit_hardening.show()
        self.hardening.hide()
        
        # Populate result table from CSV
        with open(registry_check_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            tablerow = 0
            for row in reader:
                if row[2].strip().lower() == "no":
                    self.hardening_table.setRowCount(tablerow + 1)

                    # Add checkbox in the first column
                    checkbox_item = QTableWidgetItem()
                    checkbox_item.setCheckState(Qt.Unchecked)
                    self.hardening_table.setItem(tablerow, 0, checkbox_item)

                    self.hardening_table.setItem(tablerow, 1, QTableWidgetItem(row[1]))
                    tablerow += 1

    def system_hardening(self):
        if not self.hardening_table.item(0, 1) or not self.hardening_table.item(0, 1).text():
            QMessageBox.warning(self, "Not Found", "No Path Found")
            return

        try:
            row_count = self.hardening_table.rowCount()
            any_checked = False
            
            reply = QMessageBox.question(self, "Confirm Hardening", 
                                         "Please take a backup before proceeding.\nAre you sure you want to apply the selected security hardening configurations?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply != QMessageBox.Yes:
                return

            location_map = {
                "HKLM": wrg.HKEY_LOCAL_MACHINE,
                "HKCU": wrg.HKEY_CURRENT_USER,
                "HKCR": wrg.HKEY_CLASSES_ROOT,
                "HKU": wrg.HKEY_USERS,
                "HKCC": wrg.HKEY_CURRENT_CONFIG
            }

            success_count = 0
            fail_count = 0
            access_denied_count = 0
            
            self.setCursor(Qt.WaitCursor)
            for row in range(row_count):
                checkbox_item = self.hardening_table.item(row, 0)
                if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                    any_checked = True
                    registry_path = self.hardening_table.item(row, 1).text() if self.hardening_table.item(row, 1) else ""

                    if not registry_path:
                        continue

                    try:
                        location, full_key = registry_path.split("\\", 1)
                        locate, value = full_key.split(":", 1)

                        if location in location_map:
                            location_key = location_map[location]
                            try:
                                with wrg.CreateKey(location_key, locate) as key:
                                    wrg.SetValueEx(key, value, 0, wrg.REG_DWORD, 1)
                                success_count += 1
                            except PermissionError:
                                access_denied_count += 1
                            except Exception:
                                fail_count += 1
                    except Exception:
                        fail_count += 1
                        
            self.unsetCursor()

            if not any_checked:
                QMessageBox.warning(self, "Not Checked", "Please select at least one checkbox to proceed.")
                return

            summary_msg = f"Hardening process completed!\n\n" \
                          f"• Successfully applied: {success_count}\n"
            if access_denied_count > 0:
                summary_msg += f"• Access Denied (Need Admin): {access_denied_count}\n"
            if fail_count > 0:
                summary_msg += f"• Failed: {fail_count}\n"
                
            QMessageBox.information(self, "Hardening Completed", summary_msg)

        except Exception as e:
            self.unsetCursor()
            QMessageBox.warning(self, "Error", f"An error occurred during system hardening: {e}")

    def system(self):
        self.system_info.clearContents()
        self.system_info.setRowCount(1)
        self.system_info.setItem(0, 0, QTableWidgetItem("Loading..."))
        self.system_info.setItem(0, 1, QTableWidgetItem("Retrieving system information in background..."))

        self.info_worker = SystemInfoWorker()
        self.info_worker.finished.connect(self.on_system_info_finished)
        self.info_worker.start()

    def on_system_info_finished(self, system_info):
        if not system_info:
            self.system_info.clearContents()
            self.system_info.setRowCount(1)
            self.system_info.setItem(0, 0, QTableWidgetItem("Error"))
            self.system_info.setItem(0, 1, QTableWidgetItem("Failed to retrieve system information."))
            return

        self.system_info.clearContents()
        self.system_info.setRowCount(len(system_info))
        for row, (key, value) in enumerate(system_info):
            self.system_info.setItem(row, 0, QTableWidgetItem(key))
            self.system_info.setItem(row, 1, QTableWidgetItem(value))

    def __init__(self):

        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Digi Samurai")
        self.rules = []
        
        self.session_cookie = None
        cookie_path = os.path.join(cwd, "outputs", "session_cookie.txt")
        if os.path.exists(cookie_path):
            try:
                with open(cookie_path, "r", encoding="utf-8") as f:
                    self.session_cookie = f.read().strip()
            except Exception:
                pass

        # button
        self.check_security_result.hide()
        self.hardening.hide()
        self.submit_hardening.hide()
        self.system()

        # Technology Dropdown Setup (Prepopulate offline defaults first)
        self.technologies = []
        tech_json_path = os.path.join(tempfile.gettempdir(), "technologies.json")
        if os.path.exists(tech_json_path):
            try:
                with open(tech_json_path, "r", encoding="utf-8") as f:
                    self.technologies = json.load(f)
            except Exception:
                pass
        
        
            
        for tech in self.technologies:
            self.tech_dropdown.addItem(tech["name"], tech["id"])
            
        import platform
        release = platform.release()
        matched_idx = 0
        is_server = "server" in release.lower() or "server" in platform.platform().lower()
        for idx in range(self.tech_dropdown.count()):
            tech_name = self.tech_dropdown.itemText(idx)
            if is_server and "server" in tech_name.lower():
                matched_idx = idx
                break
            elif not is_server and "desktop" in tech_name.lower():
                matched_idx = idx
                break
        self.tech_dropdown.setCurrentIndex(matched_idx)
            
        self.tech_dropdown.hide()
        self.benchmark_dropdown.hide()

        # Connect technology selection change to benchmarks loader
        self.tech_dropdown.currentIndexChanged.connect(self.on_tech_changed)

        # Fetch latest technologies dynamically in background
        self.tech_worker = LoadTechnologiesWorker(self.session_cookie)
        self.tech_worker.finished.connect(self.on_tech_loaded)
        self.tech_worker.start()
        
        # Initial trigger
        self.on_tech_changed()

        # State and dynamic widgets for online downloader
        self.downloaded_pdf_path = None
        self.download_btn = QPushButton("Download", self)
        self.download_btn.setObjectName("download_btn")
        self.horizontalLayout.insertWidget(2, self.download_btn)
        self.download_btn.hide()

        # section
        self.result_table.hide()
        self.dashboard_plot.hide()
        self.hardening_table.hide()

        # connect
        self.browse.clicked.connect(self.browse_file)
        self.submit.clicked.connect(self.path_extract)
        self.check_security.clicked.connect(self.registry_checking)
        self.cancel.clicked.connect(self.cancel_button)
        self.check_security_result.clicked.connect(self.dashboard)
        self.hardening.clicked.connect(self.table_hardening)
        self.submit_hardening.clicked.connect(self.system_hardening)
        self.backup_btn.clicked.connect(self.backup_registry_dialog)
        self.radio_local.toggled.connect(self.on_source_toggled)
        self.radio_online.toggled.connect(self.on_source_toggled)
        self.download_btn.clicked.connect(self.start_online_download)
        self.benchmark_dropdown.currentIndexChanged.connect(self.reset_download_state)

    def reset_download_state(self):
        self.downloaded_pdf_path = None
        if self.radio_online.isChecked():
            self.submit.hide()
            self.download_btn.show()
            self.download_btn.setEnabled(True)

    def start_online_download(self):
        try:
            idx = self.benchmark_dropdown.currentIndex()
            if idx == -1 or not self.benchmark_dropdown.isEnabled():
                QMessageBox.warning(self, "Warning", "Please wait for benchmarks list to load.")
                return
            data = self.benchmark_dropdown.itemData(idx)
            if not data or not isinstance(data, tuple):
                QMessageBox.warning(self, "Warning", "Please select a valid benchmark.")
                return
            
            pardot_id, filename = data
            tech_idx = self.tech_dropdown.currentIndex()
            tech_id = self.tech_dropdown.itemData(tech_idx)
            self.start_downloading_thread(pardot_id, tech_id, filename)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def on_source_toggled(self):
        is_local = self.radio_local.isChecked()
        self.path.setVisible(is_local)
        self.browse.setVisible(is_local)
        self.tech_dropdown.setVisible(not is_local)
        self.benchmark_dropdown.setVisible(not is_local)
        
        if is_local:
            self.submit.show()
            self.submit.setEnabled(True)
            self.download_btn.hide()
        else:
            if self.downloaded_pdf_path and os.path.exists(self.downloaded_pdf_path):
                self.submit.show()
                self.submit.setEnabled(True)
                self.download_btn.hide()
            else:
                self.submit.hide()
                self.download_btn.show()
                self.download_btn.setEnabled(True)

    def on_tech_changed(self):
        idx = self.tech_dropdown.currentIndex()
        if idx == -1:
            return
        tech_id = self.tech_dropdown.itemData(idx)
        
        self.benchmark_dropdown.clear()
        self.benchmark_dropdown.addItem("Loading benchmarks list...")
        self.benchmark_dropdown.setEnabled(False)
        
        if hasattr(self, 'benchmarks_worker') and self.benchmarks_worker.isRunning():
            try:
                self.benchmarks_worker.terminate()
                self.benchmarks_worker.wait()
            except Exception:
                pass
                
        self.benchmarks_worker = LoadBenchmarksWorker(tech_id, self.session_cookie)
        self.benchmarks_worker.finished.connect(self.on_benchmarks_loaded)
        self.benchmarks_worker.start()

    def on_benchmarks_loaded(self, benchmarks):
        self.benchmark_dropdown.clear()
        self.benchmark_dropdown.setEnabled(True)
        if not benchmarks:
            self.benchmark_dropdown.addItem("No benchmarks found.")
            return
        for b in benchmarks:
            self.benchmark_dropdown.addItem(b["title"], (b["pardot_id"], b["filename"]))

    def on_tech_loaded(self, tech_list):
        if not tech_list:
            return
            
        self.tech_dropdown.blockSignals(True)
        self.tech_dropdown.clear()
        for tech in tech_list:
            self.tech_dropdown.addItem(tech["name"], tech["id"])
            
        import platform
        release = platform.release()
        matched_idx = -1
        is_server = "server" in release.lower() or "server" in platform.platform().lower()
        for idx in range(self.tech_dropdown.count()):
            tech_name = self.tech_dropdown.itemText(idx)
            if is_server:
                if "server" in tech_name.lower():
                    matched_idx = idx
                    break
            else:
                if "desktop" in tech_name.lower():
                    matched_idx = idx
                    break
                
        if matched_idx != -1:
            self.tech_dropdown.setCurrentIndex(matched_idx)
            
        self.tech_dropdown.blockSignals(False)
        self.on_tech_changed()

    def backup_registry_dialog(self):
        paths = []
        if hasattr(self, 'rules') and self.rules:
            paths = [r['Full Registry Path'] for r in self.rules]
            msg = "Do you want to back up all registry keys targeted by the loaded CIS Benchmark rules?"
        else:
            msg = "No CIS rules are currently loaded. Do you want to back up the complete security-related system hives (HKLM\\SYSTEM and HKLM\\SOFTWARE\\Policies) instead?"

        reply = QMessageBox.question(self, "Backup Registry", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply != QMessageBox.Yes:
            return

        default_file = "backup_registry.reg"
        os.makedirs(os.path.join(cwd, "outputs"), exist_ok=True)
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Registry Backup", os.path.join(cwd, "outputs", default_file), "Registry Files (*.reg)")
        if not save_path:
            return

        self.setCursor(Qt.WaitCursor)
        self.backup_btn.setEnabled(False)

        self.progress_dialog = QProgressDialog("Exporting registry keys...", None, 0, 0, self)
        self.progress_dialog.setWindowTitle("Backing up Registry")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.show()

        self.backup_worker = BackupWorker(paths, save_path)
        self.backup_worker.finished.connect(self.on_backup_finished)
        self.backup_worker.start()

    def on_backup_finished(self, success, message):
        self.unsetCursor()
        self.backup_btn.setEnabled(True)
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        if success:
            QMessageBox.information(self, "Backup Success", message)
        else:
            QMessageBox.critical(self, "Backup Failed", f"An error occurred during registry backup:\n{message}")
if __name__ == '__main__':

    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
        sys.exit()

    app = QApplication(sys.argv)
    
    # Apply a premium light-themed QSS stylesheet
    app.setStyleSheet("""
        /* Global styles */
        QWidget {
            background-color: #FFFFFF;
            color: #1E293B;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
            font-size: 13px;
        }

        /* Main Window and Container panels */
        QMainWindow, QDialog, QWidget#centralwidget {
            background-color: #FAF5F5;
        }

        /* Table Widget styling */
        QTableWidget {
            background-color: #FFFFFF;
            alternate-background-color: #FAF5F5;
            border: 1px solid #E2DADA;
            border-radius: 8px;
            gridline-color: #E2DADA;
            outline: none;
        }
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #F3E8E8;
        }
        QTableWidget::item:selected {
            background-color: #FEE2E2;
            color: #800000;
        }
        QTableWidget::item:hover {
            background-color: #FAF5F5;
        }

        /* Header Section of Tables */
        QHeaderView::section {
            background-color: #F3E8E8;
            color: #800000;
            padding: 8px;
            border: none;
            border-bottom: 2px solid #E2DADA;
            font-weight: bold;
            font-size: 12px;
        }

        /* Push Buttons */
        QPushButton {
            background-color: #800000;
            color: #FFFFFF;
            border: 1px solid #660000;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #991B1B;
        }
        QPushButton:pressed {
            background-color: #660000;
        }
        QPushButton:disabled {
            background-color: #E2DADA;
            border-color: #E2DADA;
            color: #94A3B8;
        }

        /* Secondary Button styling */
        QPushButton#browse, QPushButton#cancel, QPushButton#backup_btn {
            background-color: #FFFFFF;
            color: #800000;
            border: 1px solid #CBD5E1;
        }
        QPushButton#browse:hover, QPushButton#cancel:hover, QPushButton#backup_btn:hover {
            background-color: #FAF5F5;
            border-color: #B83A3A;
        }

        /* Action Buttons */
        QPushButton#submit, QPushButton#check_security, QPushButton#hardening, QPushButton#submit_hardening, QPushButton#download_btn {
            background-color: #B83A3A;
            border-color: #800000;
        }
        QPushButton#submit:hover, QPushButton#check_security:hover, QPushButton#hardening:hover, QPushButton#submit_hardening:hover, QPushButton#download_btn:hover {
            background-color: #800000;
        }

        /* Line Edit inputs */
        QLineEdit {
            background-color: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 6px 12px;
            color: #1E293B;
        }
        QLineEdit:focus {
            border: 1px solid #B83A3A;
        }

        /* Comboboxes / Dropdowns */
        QComboBox {
            background-color: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 6px 12px;
            color: #1E293B;
        }
        QComboBox:hover {
            border-color: #94A3B8;
        }
        QComboBox:on {
            border-color: #B83A3A;
        }
        QComboBox::drop-down {
            border: none;
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #800000;
            width: 0;
            height: 0;
            margin-right: 10px;
        }

        /* Tab Widget styling (Dashboard) */
        QTabWidget::pane {
            border: 1px solid #E2DADA;
            border-radius: 8px;
            background-color: #FFFFFF;
            top: -1px;
        }
        QTabBar::tab {
            background-color: #FAF5F5;
            color: #800000;
            border: 1px solid #E2DADA;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            margin-right: 4px;
        }
        QTabBar::tab:hover {
            background-color: #F3E8E8;
        }
        QTabBar::tab:selected {
            background-color: #FFFFFF;
            color: #800000;
            border-bottom: 2px solid #800000;
            font-weight: bold;
        }

        /* Radio Buttons */
        QRadioButton {
            color: #334155;
            font-weight: 500;
            spacing: 8px;
        }
        QRadioButton::indicator {
            width: 14px;
            height: 14px;
            border: 2px solid #94A3B8;
            border-radius: 9px;
            background-color: #FFFFFF;
        }
        QRadioButton::indicator:hover {
            border-color: #800000;
        }
        QRadioButton::indicator:checked {
            border: 4px solid #800000;
            background-color: #FFFFFF;
        }

        /* Checkboxes styling */
        QCheckBox {
            color: #334155;
            font-weight: 500;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 14px;
            height: 14px;
            border: 2px solid #94A3B8;
            border-radius: 4px;
            background-color: #FFFFFF;
        }
        QCheckBox::indicator:hover {
            border-color: #800000;
        }
        QCheckBox::indicator:checked {
            border: 4px solid #800000;
            background-color: #FFFFFF;
        }

        /* Scrollbars */
        QScrollBar:vertical {
            border: none;
            background: #FAF5F5;
            width: 8px;
            margin: 0px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background: #E2DADA;
            min-height: 20px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical:hover {
            background: #B83A3A;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """)

    splash = SplashScreen()
    splash.show()
    splash.progress()

    try:
        ui = MainWindow()
    except Exception as e:
        import traceback
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/crash.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        sys.exit(1)
        
    ui.show()

    splash.finish(ui)
    sys.exit(app.exec())