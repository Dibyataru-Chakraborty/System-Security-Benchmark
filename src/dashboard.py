import os
import pandas as pd
from matplotlib.figure import Figure
import src.dashboard_handel as dh

def get_data(csv_path="outputs/registry_check_results.csv"):
    try:
        data = pd.read_csv(csv_path)
    except Exception:
        data = pd.DataFrame(columns=["found"])
        
    found_counts = data["found"].value_counts().reset_index()
    found_counts.columns = ["found", "count"]
    
    dfr1, dfr2, dfr3 = dh.process_data(csv_path)
    
    return data, found_counts, dfr1, dfr2, dfr3

# Premium high-contrast clean light theme palette
pie_colors = ["#EF4444", "#10B981", "#F59E0B", "#64748B"] # Fail (red), Pass (green), Warning (amber), Slate (other)
doughnut_colors = ["#4F46E5", "#06B6D4", "#10B981", "#F59E0B", "#EC4899"] # Indigo, Teal, Emerald, Amber, Pink
bar_chart_colors_dfr2 = ["#EF4444", "#10B981", "#64748B"] # Fail, Pass, Other
bar_chart_colors_dfr3 = ["#EF4444", "#10B981", "#64748B"] # Fail, Pass, Other

def dynamic_fontsize(scale=1):
    return 10 * scale

def apply_chart_style(fig, ax, title_text):
    # Set clean white figure background
    fig.patch.set_facecolor('#FFFFFF')
    # Set soft light grey axis background
    ax.set_facecolor('#F8FAFC')
    
    # Configure soft grey grid lines
    ax.grid(True, color="#E2E8F0", linestyle="-", linewidth=0.8, alpha=0.8)
    
    # Hide top and right borders for a modern look
    if 'top' in ax.spines:
        ax.spines['top'].set_visible(False)
    if 'right' in ax.spines:
        ax.spines['right'].set_visible(False)
    if 'left' in ax.spines:
        ax.spines['left'].set_color('#CBD5E1')
        ax.spines['left'].set_linewidth(1.0)
    if 'bottom' in ax.spines:
        ax.spines['bottom'].set_color('#CBD5E1')
        ax.spines['bottom'].set_linewidth(1.0)
        
    # Title styling
    ax.set_title(
        title_text,
        fontsize=dynamic_fontsize(1.3),
        weight="bold",
        color="#1E293B",
        pad=15
    )

def plot_pie_chart(csv_path="outputs/registry_check_results.csv"):
    _, found_counts, _, _, _ = get_data(csv_path)
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    
    # Custom color mapping based on labels to ensure red is Fail and green is Pass
    custom_colors = []
    if not found_counts.empty:
        for val in found_counts["found"]:
            val_lower = str(val).lower()
            if val_lower == "no" or "fail" in val_lower or "non-compliant" in val_lower or "false" in val_lower:
                custom_colors.append("#B83A3A") # Light Maroon
            elif val_lower == "yes" or "pass" in val_lower or "compliant" in val_lower or "true" in val_lower:
                custom_colors.append("#10B981") # Green
            elif "warning" in val_lower or "not found" in val_lower or "missing" in val_lower:
                custom_colors.append("#F59E0B") # Amber
            else:
                custom_colors.append("#64748B") # Slate
                
        wedges, texts, autotexts = ax.pie(
            found_counts["count"],
            labels=found_counts["found"],
            autopct="%1.1f%%",
            colors=custom_colors,
            textprops=dict(color="#1E293B", weight="semibold", fontsize=dynamic_fontsize(0.9))
        )
        # Style label text inside wedges
        for autotext in autotexts:
            autotext.set_color('white')
            
        ax.legend(
            wedges,
            [
                f"{cat} ({val})"
                for cat, val in zip(found_counts["found"], found_counts["count"])
            ],
            title="Registry Keys Status",
            loc="upper left",
            bbox_to_anchor=(1.05, 0.95),
            fontsize=dynamic_fontsize(0.85),
            title_fontsize=dynamic_fontsize(0.9),
            framealpha=0.8,
            edgecolor="#E2E8F0"
        )
        
    apply_chart_style(fig, ax, "Detection Rate of Registry paths")
    fig.tight_layout(pad=2)
    return fig

def plot_doughnut_chart(csv_path="outputs/registry_check_results.csv"):
    _, _, dfr1, _, _ = get_data(csv_path)
    category_counts = dfr1["Category"].value_counts().reset_index()
    category_counts.columns = ["Category", "Count"]
    
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    
    if not category_counts.empty:
        wedges, texts, autotexts = ax.pie(
            category_counts["Count"],
            labels=category_counts["Category"],
            autopct="%1.1f%%",
            startangle=140,
            colors=doughnut_colors[: len(category_counts)],
            wedgeprops=dict(width=0.3, edgecolor='white', linewidth=1.5),
            textprops=dict(color="#1E293B", fontsize=dynamic_fontsize(0.85))
        )
        ax.legend(
            wedges,
            [
                f"{cat} ({val})"
                for cat, val in zip(category_counts["Category"], category_counts["Count"])
            ],
            title="Categories List",
            loc="upper left",
            bbox_to_anchor=(1.05, 0.95),
            fontsize=dynamic_fontsize(0.85),
            title_fontsize=dynamic_fontsize(0.9),
            framealpha=0.8,
            edgecolor="#E2E8F0"
        )
        
    apply_chart_style(fig, ax, "Types of paths available")
    fig.tight_layout(pad=2)
    return fig

def plot_bar_chart_dfr2(csv_path="outputs/registry_check_results.csv"):
    _, _, _, dfr2, _ = get_data(csv_path)
    
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    
    if not dfr2.empty:
        subCategory_found_counts = (
            dfr2.groupby(["subCategory", "found"]).size().reset_index(name="count")
        )
        subCategory_found_counts_pivot = subCategory_found_counts.pivot(
            index="subCategory", columns="found", values="count"
        ).fillna(0)
        
        # Map colors according to columns (Pass/Fail)
        bar_colors = []
        for col in subCategory_found_counts_pivot.columns:
            col_lower = str(col).lower()
            if col_lower == "no" or "fail" in col_lower or "non-compliant" in col_lower or "false" in col_lower:
                bar_colors.append("#6366F1") # Indigo
            elif col_lower == "yes" or "pass" in col_lower or "compliant" in col_lower or "true" in col_lower:
                bar_colors.append("#14B8A6") # Teal
            else:
                bar_colors.append("#94A3B8") # Light Slate
                
        subCategory_found_counts_pivot.plot(
            kind="bar", ax=ax, color=bar_colors, width=0.7, edgecolor='white', linewidth=1.0
        )
        ax.set_xlabel("Subcategory", fontsize=dynamic_fontsize(0.95), labelpad=10, weight="bold", color="#475569")
        ax.set_ylabel("Count", fontsize=dynamic_fontsize(0.95), labelpad=10, weight="bold", color="#475569")
        ax.tick_params(axis="both", labelsize=dynamic_fontsize(0.85), labelcolor="#475569")
        
        # Legend styling
        ax.legend(
            title="Status",
            fontsize=dynamic_fontsize(0.85),
            title_fontsize=dynamic_fontsize(0.9),
            framealpha=0.8,
            edgecolor="#E2E8F0"
        )
        
        # Annotations on top of bars
        for p in ax.patches:
            height = p.get_height()
            if height > 0:
                ax.annotate(
                    f"{int(height)}",
                    (p.get_x() + p.get_width() / 2.0, height),
                    ha="center",
                    va="center",
                    fontsize=dynamic_fontsize(0.8),
                    weight="bold",
                    color="#1E293B",
                    xytext=(0, 4),
                    textcoords="offset points",
                )
                
    apply_chart_style(fig, ax, "HKLM System Categories")
    fig.tight_layout(pad=2)
    return fig

def plot_bar_chart_dfr3(csv_path="outputs/registry_check_results.csv"):
    _, _, _, _, dfr3 = get_data(csv_path)
    
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    
    if not dfr3.empty:
        subCategory_found_counts = (
            dfr3.groupby(["subCategory", "found"]).size().reset_index(name="count")
        )
        subCategory_found_counts_pivot = subCategory_found_counts.pivot(
            index="subCategory", columns="found", values="count"
        ).fillna(0)
        
        bar_colors = []
        for col in subCategory_found_counts_pivot.columns:
            col_lower = str(col).lower()
            if col_lower == "no" or "fail" in col_lower or "non-compliant" in col_lower or "false" in col_lower:
                bar_colors.append("#F43F5E") # Rose
            elif col_lower == "yes" or "pass" in col_lower or "compliant" in col_lower or "true" in col_lower:
                bar_colors.append("#84CC16") # Lime
            else:
                bar_colors.append("#94A3B8") # Light Slate
                
        subCategory_found_counts_pivot.plot(
            kind="bar", ax=ax, color=bar_colors, width=0.7, edgecolor='white', linewidth=1.0
        )
        ax.set_xlabel("Subcategory", fontsize=dynamic_fontsize(0.95), labelpad=10, weight="bold", color="#475569")
        ax.set_ylabel("Count", fontsize=dynamic_fontsize(0.95), labelpad=10, weight="bold", color="#475569")
        ax.tick_params(axis="both", labelsize=dynamic_fontsize(0.85), labelcolor="#475569")
        
        ax.legend(
            title="Status",
            fontsize=dynamic_fontsize(0.85),
            title_fontsize=dynamic_fontsize(0.9),
            framealpha=0.8,
            edgecolor="#E2E8F0"
        )
        
        for p in ax.patches:
            height = p.get_height()
            if height > 0:
                ax.annotate(
                    f"{int(height)}",
                    (p.get_x() + p.get_width() / 2.0, height),
                    ha="center",
                    va="center",
                    fontsize=dynamic_fontsize(0.8),
                    weight="bold",
                    color="#1E293B",
                    xytext=(0, 4),
                    textcoords="offset points",
                )
                
    apply_chart_style(fig, ax, "HKLM Software Categories")
    fig.tight_layout(pad=2)
    return fig
