import json
import os
import sys
import re
from typing import Any, Dict, List, Optional

# Prefer curl_cffi (Chrome TLS fingerprint). Fallback to requests.
try:
    from curl_cffi import requests as http
    USE_CURL_CFFI = True
    print("[*] Using curl_cffi (Chrome impersonation)")
except ImportError:
    import requests as http
    USE_CURL_CFFI = False
    print("[!] curl_cffi not installed → using normal requests (downloads may fail with 404)")
    print("    Install with:  pip install curl_cffi")


# ============================================================
# CONFIGURATION
# ============================================================

TECHNOLOGY_URL = "https://downloads.cisecurity.org/technology"
DOWNLOADS_BASE_URL = "https://downloads.cisecurity.org"
LEARN_BASE_URL = "https://learn.cisecurity.org"
TIMEOUT = 45


# ============================================================
# HEADERS
# ============================================================

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


# ============================================================
# GET JSON
# ============================================================

def get_json(url: str) -> Any:
    try:
        kwargs = {"impersonate": "chrome"} if USE_CURL_CFFI else {}
        response = http.get(url, headers=API_HEADERS, timeout=TIMEOUT, **kwargs)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"\nRequest error: {e}")
        return None


# ============================================================
# GET TECHNOLOGIES
# ============================================================

def get_technologies() -> Dict[str, List[Dict[str, Any]]]:
    print("\nFetching technologies...")
    data = get_json(TECHNOLOGY_URL)
    if not data or not isinstance(data, dict):
        return {}
    return data


# ============================================================
# FLATTEN TECHNOLOGIES
# ============================================================

def flatten_technologies(
    technologies: Dict[str, List[Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    result = []
    for category, technology_list in technologies.items():
        if not isinstance(technology_list, list):
            continue
        for technology in technology_list:
            if isinstance(technology, dict):
                item = technology.copy()
                item["category"] = category
                result.append(item)
    return result


# ============================================================
# SEARCH TECHNOLOGIES
# ============================================================

def search_technologies(
    technologies: List[Dict[str, Any]], keyword: str
) -> List[Dict[str, Any]]:
    keyword = keyword.lower().strip()
    if not keyword:
        return []

    results = []
    for technology in technologies:
        searchable = " ".join([
            str(technology.get("id", "")),
            str(technology.get("title", "")),
            str(technology.get("key", "")),
            str(technology.get("category", "")),
            str(technology.get("sub_category", "")),
        ]).lower()
        if keyword in searchable:
            results.append(technology)
    return results


# ============================================================
# DISPLAY TECHNOLOGIES
# ============================================================

def display_technologies(technologies: List[Dict[str, Any]]) -> None:
    if not technologies:
        print("\nNo technologies found.")
        return

    print("\n" + "=" * 100)
    print("TECHNOLOGIES")
    print("=" * 100)
    print(f"Total: {len(technologies)}")
    print("=" * 100)

    for index, technology in enumerate(technologies, start=1):
        print(f"[{index}] {technology.get('title', 'Unknown')}")
        print(f"     ID: {technology.get('id', 'Unknown')}")
        print(f"     Category: {technology.get('category', 'Unknown')}")
        print(f"     Key: {technology.get('key', 'Unknown')}")
        print(f"     Latest version: {technology.get('latest_technology_version', 'Unknown')}")
        print("-" * 100)


# ============================================================
# SELECT TECHNOLOGY
# ============================================================

def select_technology(
    technologies: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    if not technologies:
        return None

    while True:
        choice = input(
            f"\nSelect technology [1-{len(technologies)}] or 'q' to go back: "
        ).strip()

        if choice.lower() == "q":
            return None

        try:
            number = int(choice)
            if 1 <= number <= len(technologies):
                return technologies[number - 1]
            print(f"Please enter a number between 1 and {len(technologies)}.")
        except ValueError:
            print("Please enter a valid number.")


# ============================================================
# GET LATEST BENCHMARKS
# ============================================================

def get_latest_benchmarks(technology_id: int) -> List[Dict[str, Any]]:
    url = f"{DOWNLOADS_BASE_URL}/technology/{technology_id}/benchmarks/latest"

    print("\n" + "=" * 100)
    print("FETCHING LATEST BENCHMARKS")
    print("=" * 100)
    print(f"Technology ID: {technology_id}")
    print(f"URL: {url}")

    data = get_json(url)
    if not data or not isinstance(data, list):
        return []
    return data


# ============================================================
# DISPLAY BENCHMARKS
# ============================================================

def display_benchmarks(benchmarks: List[Dict[str, Any]]) -> None:
    if not benchmarks:
        print("\nNo latest benchmarks found.")
        return

    print("\n" + "=" * 100)
    print("LATEST BENCHMARKS")
    print("=" * 100)

    for index, benchmark in enumerate(benchmarks, start=1):
        print(f"\n[{index}] {benchmark.get('title', 'Unknown')}")
        print(f"    Benchmark ID: {benchmark.get('id', 'Unknown')}")
        print(f"    Technology ID: {benchmark.get('technology_id', 'Unknown')}")
        print(f"    Technology Version: {benchmark.get('technology_version', 'Unknown')}")
        print(f"    Benchmark Version: {benchmark.get('version', 'Unknown')}")
        print(f"    Published: {benchmark.get('published', 'Unknown')}")

        documents = benchmark.get("documents", [])
        print(f"    Documents: {len(documents)}")

        for document_index, document in enumerate(documents, start=1):
            print(f"\n        Document [{document_index}]")
            print(f"        Title: {document.get('title', 'Unknown')}")
            print(f"        Filename: {document.get('filename', 'Unknown')}")
            print(f"        Document ID: {document.get('id', 'Unknown')}")
            print(f"        Pardot ID: {document.get('pardot-id', 'Unknown')}")
            print(f"        API Location: {document.get('location', 'Unknown')}")

        print("\n" + "-" * 100)


# ============================================================
# SELECT BENCHMARK
# ============================================================

def select_benchmark(
    benchmarks: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    if not benchmarks:
        return None

    while True:
        choice = input(
            f"\nSelect benchmark [1-{len(benchmarks)}] or 'q' to go back: "
        ).strip()

        if choice.lower() == "q":
            return None

        try:
            number = int(choice)
            if 1 <= number <= len(benchmarks):
                return benchmarks[number - 1]
            print(f"Please enter a number between 1 and {len(benchmarks)}.")
        except ValueError:
            print("Please enter a valid number.")


# ============================================================
# BUILD BROWSER URL
# ============================================================

def build_browser_download_url(pardot_url: str) -> str:
    if not pardot_url:
        return ""
    if pardot_url.startswith("http://") or pardot_url.startswith("https://"):
        return pardot_url
    return f"{LEARN_BASE_URL}/{pardot_url.lstrip('/')}"


# ============================================================
# DISPLAY DOCUMENTS
# ============================================================

def display_documents(benchmark: Dict[str, Any]) -> None:
    documents = benchmark.get("documents", [])
    if not documents:
        print("\nNo documents found.")
        return

    print("\n" + "=" * 100)
    print("DOCUMENTS")
    print("=" * 100)

    for index, document in enumerate(documents, start=1):
        pardot_id = document.get("pardot-id")
        browser_url = build_browser_download_url(pardot_id)

        print(f"\n[{index}] {document.get('title', 'Unknown')}")
        print(f"    Document ID: {document.get('id', 'Unknown')}")
        print(f"    Filename: {document.get('filename', 'Unknown')}")
        print(f"    Pardot ID: {pardot_id or 'Unknown'}")
        print(f"    Browser URL:\n    {browser_url or 'Unknown'}")
        print(f"    API Location:\n    {document.get('location', 'Unknown')}")
        print("-" * 100)


# ============================================================
# SELECT DOCUMENT
# ============================================================

def select_document(
    documents: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    if not documents:
        return None

    while True:
        choice = input(
            f"\nSelect document [1-{len(documents)}] or 'q' to go back: "
        ).strip()

        if choice.lower() == "q":
            return None

        try:
            number = int(choice)
            if 1 <= number <= len(documents):
                return documents[number - 1]
            print(f"Please enter a number between 1 and {len(documents)}.")
        except ValueError:
            print("Please enter a valid number.")


# ============================================================
# DOWNLOAD FILE  (FIXED – uses Chrome TLS fingerprint)
# ============================================================

def download_file(pardot_url: str, filename: str) -> bool:
    """
    Download using Chrome TLS fingerprint (curl_cffi) when available.
    This is required because CIS rejects normal Python TLS fingerprints.
    """
    if not pardot_url:
        print("\nNo Pardot URL found.")
        return False

    download_url = build_browser_download_url(pardot_url)
    if not filename:
        filename = "cis_benchmark.pdf"
    filename = os.path.basename(filename) or "cis_benchmark.pdf"

    print("\n" + "=" * 100)
    print("BROWSER-STYLE DOWNLOAD")
    print("=" * 100)
    print(f"\nOriginal URL:\n{download_url}")
    print(f"\nFilename:\n{filename}")
    print(f"\nEngine: {'curl_cffi (Chrome)' if USE_CURL_CFFI else 'requests (may fail)'}")

    try:
        # ----------------------------------------------------
        # Create session
        # ----------------------------------------------------
        if USE_CURL_CFFI:
            session = http.Session(impersonate="chrome")
        else:
            session = http.Session()
            session.headers.update(BROWSER_HEADERS)

        # ----------------------------------------------------
        # Follow full redirect chain
        # ----------------------------------------------------
        print("\n[1/2] Following redirect chain...")

        kwargs = {"timeout": TIMEOUT, "allow_redirects": True}
        if USE_CURL_CFFI:
            # curl_cffi Session already has impersonate
            response = session.get(download_url, **kwargs)
        else:
            response = session.get(download_url, headers=BROWSER_HEADERS, **kwargs)

        print(f"Status: {response.status_code}")
        print(f"Final URL:\n{response.url}")
        print(f"Content-Type:\n{response.headers.get('Content-Type')}")
        print(f"Content-Length:\n{response.headers.get('Content-Length')}")

        # ----------------------------------------------------
        # Error handling
        # ----------------------------------------------------
        if response.status_code != 200:
            print(f"\nDownload endpoint returned HTTP {response.status_code}.")
            if response.status_code == 404:
                print(
                    "\n>>> STILL 404?\n"
                    "1. Make sure you installed:  pip install curl_cffi\n"
                    "2. Select the document again (fresh token)\n"
                    "3. If it still fails → CIS is blocking non-browser clients tightly.\n"
                    "   In that case use Playwright (full browser)."
                )
            save_debug_response(response)
            return False

        content_type = response.headers.get("Content-Type", "").lower()
        if "text/html" in content_type and "pdf" not in content_type:
            print("\nWARNING: Server returned HTML instead of PDF.")
            save_debug_response(response)
            return False

        # ----------------------------------------------------
        # Filename from Content-Disposition
        # ----------------------------------------------------
        content_disposition = response.headers.get("Content-Disposition", "")
        if content_disposition:
            match = re.search(
                r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?',
                content_disposition,
                re.IGNORECASE,
            )
            if match:
                server_filename = match.group(1).strip()
                if server_filename:
                    filename = server_filename

        # ----------------------------------------------------
        # Save
        # ----------------------------------------------------
        return save_response_to_file(response, filename)

    except Exception as e:
        print(f"\nDownload error:\n{e}")
        return False


# ============================================================
# SAVE HTTP RESPONSE TO FILE
# ============================================================

def save_response_to_file(response, filename: str) -> bool:
    filename = os.path.basename(filename) or "cis_benchmark.pdf"

    print(f"\nSaving file as:\n{filename}")

    try:
        # curl_cffi and requests both support .content
        content = response.content

        with open(filename, "wb") as f:
            f.write(content)

    except OSError as e:
        print(f"\nCould not write file:\n{e}")
        return False

    if not os.path.exists(filename):
        print("\nFile was not created.")
        return False

    file_size = os.path.getsize(filename)

    print("\n" + "=" * 100)
    print("DOWNLOAD COMPLETE")
    print("=" * 100)
    print(f"File:\n{os.path.abspath(filename)}")
    print(f"Size:\n{file_size:,} bytes")

    # Verify PDF
    try:
        with open(filename, "rb") as f:
            signature = f.read(5)
        if signature == b"%PDF-":
            print("Format: PDF ✓")
            return True
        print("WARNING: File does not start with %PDF-")
        return False
    except OSError as e:
        print(f"\nCould not verify file:\n{e}")
        return False


# ============================================================
# SAVE DEBUG RESPONSE
# ============================================================

def save_debug_response(response) -> None:
    try:
        content_type = response.headers.get("Content-Type", "").lower()
        filename = "cis_download_debug.html" if "html" in content_type else "cis_download_debug.txt"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"\nDebug response saved to:\n{os.path.abspath(filename)}")
    except Exception as e:
        print(f"\nCould not save debug response:\n{e}")


# ============================================================
# DOWNLOAD SELECTED DOCUMENT
# ============================================================

def download_benchmark_document(benchmark: Dict[str, Any]) -> None:
    documents = benchmark.get("documents", [])
    if not documents:
        print("\nNo documents available.")
        return

    display_documents(benchmark)
    document = select_document(documents)
    if not document:
        return

    pardot_id = document.get("pardot-id")
    filename = document.get("filename", "cis_benchmark.pdf")

    if not pardot_id:
        print("\nNo pardot-id exists for this document.")
        return

    download_file(pardot_id, filename)


# ============================================================
# TECHNOLOGY DETAILS MENU
# ============================================================

def technology_details_menu(technology: Dict[str, Any]) -> None:
    technology_id = technology.get("id")
    technology_title = technology.get("title", "Unknown")

    while True:
        print("\n" + "=" * 100)
        print(f"SELECTED TECHNOLOGY: {technology_title}")
        print("=" * 100)
        print(f"ID: {technology_id}")
        print(f"Category: {technology.get('category', 'Unknown')}")
        print(f"Key: {technology.get('key', 'Unknown')}")
        print(f"Latest version: {technology.get('latest_technology_version', 'Unknown')}")

        print("\n1. Get latest benchmarks")
        print("2. Select benchmark")
        print("3. Download benchmark PDF")
        print("4. Save benchmarks JSON")
        print("0. Back")
        print("=" * 100)

        choice = input("\nChoose option: ").strip()

        if choice == "1":
            benchmarks = get_latest_benchmarks(technology_id)
            display_benchmarks(benchmarks)
            input("\nPress ENTER to continue...")

        elif choice == "2":
            benchmarks = get_latest_benchmarks(technology_id)
            if not benchmarks:
                input("\nPress ENTER to continue...")
                continue

            display_benchmarks(benchmarks)
            benchmark = select_benchmark(benchmarks)
            if not benchmark:
                continue

            while True:
                print("\n" + "=" * 100)
                print(benchmark.get("title", "Unknown"))
                print("=" * 100)
                print("1. View documents")
                print("2. Download document")
                print("0. Back")

                benchmark_choice = input("\nChoose option: ").strip()

                if benchmark_choice == "1":
                    display_documents(benchmark)
                    input("\nPress ENTER to continue...")
                elif benchmark_choice == "2":
                    download_benchmark_document(benchmark)
                    input("\nPress ENTER to continue...")
                elif benchmark_choice == "0":
                    break
                else:
                    print("\nInvalid option.")

        elif choice == "3":
            benchmarks = get_latest_benchmarks(technology_id)
            if not benchmarks:
                input("\nPress ENTER to continue...")
                continue

            display_benchmarks(benchmarks)
            benchmark = select_benchmark(benchmarks)
            if benchmark:
                download_benchmark_document(benchmark)
            input("\nPress ENTER to continue...")

        elif choice == "4":
            benchmarks = get_latest_benchmarks(technology_id)
            if not benchmarks:
                input("\nPress ENTER to continue...")
                continue

            filename = input("\nFilename [benchmark.json]: ").strip() or "benchmark.json"
            save_json(benchmarks, filename)
            input("\nPress ENTER to continue...")

        elif choice == "0":
            break
        else:
            print("\nInvalid option.")


# ============================================================
# OPTION 1 – LIST ALL TECHNOLOGIES
# ============================================================

def option_list_technologies(technologies: List[Dict[str, Any]]) -> None:
    if not technologies:
        print("\nNo technologies available.")
        return

    while True:
        display_technologies(technologies)
        technology = select_technology(technologies)
        if not technology:
            break
        technology_details_menu(technology)


# ============================================================
# OPTION 2 – SEARCH TECHNOLOGIES
# ============================================================

def option_search_technologies(technologies: List[Dict[str, Any]]) -> None:
    keyword = input("\nEnter search keyword (title, ID, key, category): ").strip()
    if not keyword:
        return

    results = search_technologies(technologies, keyword)
    print(f"\nFound {len(results)} matching technologies.")

    if not results:
        input("\nPress ENTER to continue...")
        return

    display_technologies(results)
    technology = select_technology(results)
    if technology:
        technology_details_menu(technology)


# ============================================================
# FETCH ALL BENCHMARKS
# ============================================================

def fetch_all_benchmarks(
    technologies: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    results = []
    total = len(technologies)

    for index, technology in enumerate(technologies, start=1):
        technology_id = technology.get("id")
        title = technology.get("title", "Unknown")

        print("\n" + "=" * 100)
        print(f"[{index}/{total}] {title}")
        print(f"Technology ID: {technology_id}")
        print("=" * 100)

        benchmarks = get_latest_benchmarks(technology_id)
        results.append({
            "technology": technology,
            "benchmarks": benchmarks,
        })

    return results


# ============================================================
# SAVE JSON
# ============================================================

def save_json(data: Any, filename: str) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("\nJSON saved:")
        print(os.path.abspath(filename))
    except OSError as e:
        print(f"\nCould not save JSON:\n{e}")


# ============================================================
# OPTION 3 – FETCH ALL
# ============================================================

def option_fetch_all(technologies: List[Dict[str, Any]]) -> None:
    print("\nWARNING")
    print("This will request the benchmark endpoint for every technology.")
    print(f"\nTechnologies: {len(technologies)}")

    confirm = input("\nContinue? [y/n]: ").strip().lower()
    if confirm != "y":
        return

    results = fetch_all_benchmarks(technologies)
    print("\nCompleted.")

    filename = input("\nSave filename [cis_benchmarks.json]: ").strip() or "cis_benchmarks.json"
    save_json(results, filename)
    input("\nPress ENTER to continue...")


# ============================================================
# MAIN MENU
# ============================================================

def show_menu() -> None:
    print("\n" + "=" * 100)
    print(" CIS BENCHMARK EXPLORER")
    print("=" * 100)
    print("1. List all technologies")
    print("2. Search technologies")
    print("3. Fetch all latest benchmarks")
    print("4. Refresh technologies")
    print("0. Exit")
    print("=" * 100)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 100)
    print(" CIS BENCHMARK EXPLORER")
    print("=" * 100)
    print("\nTechnology API:")
    print(TECHNOLOGY_URL)

    technology_data = get_technologies()
    if not technology_data:
        print("\nUnable to retrieve technologies.")
        sys.exit(1)

    technologies = flatten_technologies(technology_data)
    print(f"\nLoaded {len(technologies)} technologies.")

    while True:
        show_menu()
        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            option_list_technologies(technologies)
        elif choice == "2":
            option_search_technologies(technologies)
        elif choice == "3":
            option_fetch_all(technologies)
        elif choice == "4":
            print("\nRefreshing technologies...")
            technology_data = get_technologies()
            if technology_data:
                technologies = flatten_technologies(technology_data)
                print(f"\nLoaded {len(technologies)} technologies.")
        elif choice == "0":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid option.")


if __name__ == "__main__":
    main()