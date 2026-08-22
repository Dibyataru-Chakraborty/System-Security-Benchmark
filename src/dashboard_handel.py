import pandas as pd
import re

def extract_base_registry(path):
    if not isinstance(path, str):
        return ""
    return path.split("\\")[0]

def generate_category_patterns(base_registry):
    return {
        "s/w": rf"^{base_registry}\\SOFTWARE",
        "sys": rf"^{base_registry}\\SYSTEM",
    }

def generate_subcategory_patterns(base_registry):
    return {
        "policies": rf"^{base_registry}\\[A-Za-z\\]+\\Policies",
        "classes": rf"^{base_registry}\\SOFTWARE\\Classes",
        "microsoft": rf"^{base_registry}\\SOFTWARE\\Microsoft",
        "control": rf"^{base_registry}\\[A-Za-z\\]+\\Control",
        "services": rf"^{base_registry}\\[A-Za-z\\]+\\Services",
    }

def assign_category(row):
    base_registry = row["BaseRegistry"]
    category_patterns = generate_category_patterns(base_registry)
    for category, pattern in category_patterns.items():
        if re.match(pattern, row["path"], re.IGNORECASE):
            return category
    return "Unknown"

def assign_subcategory(row):
    base_registry = row["BaseRegistry"]
    subcategory_patterns = generate_subcategory_patterns(base_registry)
    for subcategory, pattern in subcategory_patterns.items():
        if re.match(pattern, row["path"], re.IGNORECASE):
            return subcategory
    return "other"

def process_data(csv_path="outputs/registry_check_results.csv"):
    try:
        dfr1 = pd.read_csv(csv_path)
    except Exception:
        # Return empty dataframes if file doesn't exist yet
        cols = ["sl", "path", "found", "BaseRegistry", "Category", "subCategory"]
        return pd.DataFrame(columns=cols), pd.DataFrame(columns=cols), pd.DataFrame(columns=cols)

    dfr1["BaseRegistry"] = dfr1["path"].apply(extract_base_registry)
    dfr1["Category"] = dfr1.apply(assign_category, axis=1)
    dfr1["subCategory"] = dfr1.apply(assign_subcategory, axis=1)

    dfr2 = dfr1[dfr1["Category"] == "sys"].copy().reset_index(drop=True)
    dfr3 = dfr1[dfr1["Category"] == "s/w"].copy().reset_index(drop=True)

    return dfr1, dfr2, dfr3
