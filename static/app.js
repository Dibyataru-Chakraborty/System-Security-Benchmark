// Digi Samurai Enterprise Dashboard Application State
let appState = {
  rules: [],
  auditRecords: [],
  failedRecords: [],
  selectedHardeningPaths: new Set(),
  charts: {},
};

// Enterprise Cyber Toast Notification (Replaces ugly browser alerts)
function showToast(title, message, type = "info", duration = 4500) {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className =
    "pointer-events-auto flex items-start space-x-3 p-4 rounded-xl shadow-2xl backdrop-blur-md transition-all duration-300 transform translate-y-2 opacity-0 border text-xs";

  let borderColor = "border-slate-700/80 bg-slate-900/95 text-slate-200";
  let iconHtml = `<i data-lucide="info" class="w-5 h-5 text-indigo-400 shrink-0"></i>`;
  let titleColor = "text-indigo-400";

  if (type === "success") {
    borderColor =
      "border-emerald-500/50 bg-slate-950/95 text-emerald-100 shadow-[0_0_20px_rgba(16,185,129,0.15)]";
    iconHtml = `<i data-lucide="shield-check" class="w-5 h-5 text-emerald-400 shrink-0"></i>`;
    titleColor = "text-emerald-400";
  } else if (type === "error") {
    borderColor =
      "border-rose-500/50 bg-slate-950/95 text-rose-100 shadow-[0_0_20px_rgba(244,63,94,0.15)]";
    iconHtml = `<i data-lucide="alert-triangle" class="w-5 h-5 text-rose-400 shrink-0"></i>`;
    titleColor = "text-rose-400";
  } else if (type === "warning") {
    borderColor =
      "border-amber-500/50 bg-slate-950/95 text-amber-100 shadow-[0_0_20px_rgba(245,158,11,0.15)]";
    iconHtml = `<i data-lucide="alert-circle" class="w-5 h-5 text-amber-400 shrink-0"></i>`;
    titleColor = "text-amber-400";
  }

  toast.className += ` ${borderColor}`;
  toast.innerHTML = `
    ${iconHtml}
    <div class="flex-1 min-w-0">
      <h4 class="text-xs font-extrabold uppercase tracking-wider ${titleColor}">${escapeHtml(title)}</h4>
      <p class="text-xs text-slate-300 mt-0.5 whitespace-pre-line leading-relaxed">${escapeHtml(message)}</p>
    </div>
    <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-white transition-colors shrink-0">
      <i data-lucide="x" class="w-4 h-4"></i>
    </button>
  `;

  container.appendChild(toast);
  lucide.createIcons();

  requestAnimationFrame(() => {
    toast.classList.remove("translate-y-2", "opacity-0");
  });

  if (duration > 0) {
    setTimeout(() => {
      toast.classList.add("opacity-0", "translate-y-2");
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
}

// Initialize Application on Page Load
document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
  loadSystemInfo();
  loadTechnologies();
  fetchAnalytics();
});

// Tab Switching Handler
function switchTab(tabId) {
  document
    .querySelectorAll(".tab-content")
    .forEach((el) => el.classList.add("hidden"));
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.remove(
      "text-white",
      "bg-brand-900/90",
      "border-brand-700/60",
    );
    btn.classList.add("text-slate-400", "border-transparent");
  });

  const activeContent = document.getElementById(tabId);
  if (activeContent) activeContent.classList.remove("hidden");

  const activeBtn = document.getElementById(tabId.replace("tab-", "tab-btn-"));
  if (activeBtn) {
    activeBtn.classList.remove("text-slate-400", "border-transparent");
    activeBtn.classList.add(
      "text-white",
      "bg-brand-900/90",
      "border-brand-700/60",
    );
  }

  if (tabId === "tab-dashboard") {
    fetchAnalytics();
  }
  lucide.createIcons();
}

// Toggle Benchmark Source Mode
function toggleSourceMode() {
  const isOnline =
    document.querySelector('input[name="benchmark_source"]:checked').value ===
    "online";
  document
    .getElementById("local-source-box")
    .classList.toggle("hidden", isOnline);
  document
    .getElementById("online-source-box")
    .classList.toggle("hidden", !isOnline);
}

// Load System Telemetry
async function loadSystemInfo() {
  try {
    const res = await fetch("/api/system-info");
    const data = await res.json();
    if (data.success && data.data) {
      const tbody = document.getElementById("telemetry-table-body");
      tbody.innerHTML = "";
      data.data.forEach((item) => {
        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-800/40 transition-colors";
        tr.innerHTML = `
                    <td class="py-2.5 px-4 font-semibold text-slate-300">${escapeHtml(item.key)}</td>
                    <td class="py-2.5 px-4 text-slate-200">${escapeHtml(item.value)}</td>
                `;
        tbody.appendChild(tr);
      });

      if (data.hostname) {
        const hostEl = document.getElementById("hostname-text");
        if (hostEl) hostEl.textContent = `Host: ${data.hostname}`;
        document.getElementById("host-badge").classList.remove("hidden");
      }

      if (data.os_name) {
        const osEl = document.getElementById("spec-target-os");
        if (osEl) {
          osEl.textContent = data.os_name;
          osEl.title = data.os_name;
        }
      }
    }
  } catch (err) {
    console.error("Failed to load telemetry:", err);
  }
}

// Load Technologies for Online Downloader (Dynamic from CIS)
async function loadTechnologies() {
  try {
    const select = document.getElementById("tech-select");
    const res = await fetch("/api/technologies");
    const data = await res.json();
    if (data.success && data.technologies) {
      select.innerHTML =
        '<option value="">-- Choose Technology Platform --</option>';
      data.technologies.forEach((tech) => {
        const opt = document.createElement("option");
        opt.value = tech.id;
        const catLabel = tech.category ? ` [${tech.category}]` : "";
        opt.textContent = `${tech.name}${catLabel}`;
        select.appendChild(opt);
      });
      // Reset benchmark select
      const bSelect = document.getElementById("benchmark-select");
      if (bSelect)
        bSelect.innerHTML =
          '<option value="">-- Select Technology Platform First --</option>';
    }
  } catch (err) {
    console.error("Error loading technologies:", err);
  }
}

// On Technology Selected -> Fetch Benchmark Versions Dynamically
async function onTechSelected() {
  const techId = document.getElementById("tech-select").value;
  const bSelect = document.getElementById("benchmark-select");
  const urlInput = document.getElementById("pardot-url-input");

  if (!techId) {
    bSelect.innerHTML =
      '<option value="">-- Select Technology Platform First --</option>';
    if (urlInput) urlInput.value = "";
    return;
  }

  bSelect.innerHTML =
    '<option value="">Loading live benchmarks from CIS...</option>';
  try {
    const res = await fetch(`/api/benchmarks/${techId}`);
    const data = await res.json();
    if (data.success && data.benchmarks && data.benchmarks.length > 0) {
      bSelect.innerHTML =
        '<option value="">-- Choose Benchmark Document --</option>';
      data.benchmarks.forEach((b) => {
        const opt = document.createElement("option");
        opt.value = JSON.stringify(b);
        opt.textContent = b.title;
        bSelect.appendChild(opt);
      });
    } else {
      bSelect.innerHTML =
        '<option value="">No benchmark documents available</option>';
    }
  } catch (err) {
    bSelect.innerHTML =
      '<option value="">Failed to load benchmark versions</option>';
  }
}

// On Benchmark Selected -> Update URL input dynamically
function onBenchmarkSelected() {
  const bSelect = document.getElementById("benchmark-select");
  const urlInput = document.getElementById("pardot-url-input");
  if (!bSelect.value || !urlInput) return;
  try {
    const bData = JSON.parse(bSelect.value);
    if (bData.title) {
      appState.selectedBenchmarkTitle = bData.title;
      const stdEl = document.getElementById("spec-standard");
      if (stdEl) {
        stdEl.textContent = bData.title;
        stdEl.title = bData.title;
      }
    }
    if (bData.download_url) {
      urlInput.value = bData.download_url;
    } else if (bData.pardot_id) {
      const cleanId = bData.pardot_id.replace(/^\/+/, "");
      urlInput.value = `https://learn.cisecurity.org/${cleanId}`;
    }
  } catch (e) {}
}

// Trigger Browser Direct Download
function triggerBrowserDownload() {
  let url = document.getElementById("pardot-url-input")?.value.trim();

  // If no URL was entered manually, get it from the selected benchmark
  if (!url) {
    const bSelect = document.getElementById("benchmark-select");

    if (bSelect?.value) {
      try {
        const bData = JSON.parse(bSelect.value);
        if (bData.download_url) {
          url = bData.download_url;
        } else if (bData.pardot_id) {
          const cleanId = bData.pardot_id.replace(/^\/+/, "");
          url = `https://learn.cisecurity.org/${cleanId}`;
        }
      } catch (e) {}
    }
  }

  if (!url) {
    showToast(
      "URL Required",
      "Please select a benchmark version or enter a Pardot URL.",
      "warning",
    );
    return;
  }

  window.open(url, "_blank");
}

// Download Online Benchmark
async function downloadOnlineBenchmark() {
  const bSelect = document.getElementById("benchmark-select");
  if (!bSelect || !bSelect.value) {
    showToast(
      "Selection Required",
      "Please select a Technology Platform and Benchmark Document first.",
      "warning",
    );
    return;
  }

  let bData;
  try {
    bData = JSON.parse(bSelect.value);
  } catch (e) {
    showToast("Invalid Selection", "Please re-select a benchmark version.", "error");
    return;
  }

  const title = bData.title || "CIS Benchmark";
  const pardotId = bData.pardot_id || "";
  const filename = bData.filename || `${title.replace(/\s+/g, "_")}.pdf`;

  showLoading(
    "Downloading CIS Benchmark",
    `Fetching ${title} from repository...`,
  );

  try {
    const res = await fetch("/api/download-benchmark", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        pardot_id: pardotId,
        filename: filename,
      }),
    });
    const data = await res.json();
    hideLoading();

    if (data.success) {
      const pathInput = document.getElementById("pdf-path-input");
      if (pathInput) pathInput.value = data.path;
      appState.selectedBenchmarkTitle = title;
      const stdEl = document.getElementById("spec-standard");
      if (stdEl) {
        stdEl.textContent = title;
        stdEl.title = title;
      }
      showToast(
        "Benchmark Ready",
        `${data.message || "Benchmark downloaded successfully."} Ready to parse!`,
        "success",
      );
      // Auto-trigger parsing
      parseBenchmark();
    } else {
      showToast("Download Notice", data.error || "Unable to auto-download. Opening direct link.", "warning");
      if (data.download_url) {
        window.open(data.download_url, "_blank");
      }
    }
  } catch (err) {
    hideLoading();
    showToast("Download Request Failed", err.message, "error");
  }
}

// Handle Local PDF Upload
async function handleFileUpload(event) {
  const input = (event && event.target) ? event.target : document.getElementById("pdf-file-picker");
  if (!input || !input.files || input.files.length === 0) return;
  const file = input.files[0];
  const formData = new FormData();
  formData.append("file", file);

  showLoading(
    "Uploading Benchmark PDF",
    `Uploading ${file.name} to server...`,
  );

  try {
    const res = await fetch("/api/upload-pdf", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    hideLoading();

    if (data.success) {
      const pathInput = document.getElementById("pdf-path-input");
      if (pathInput) pathInput.value = data.path;
      if (data.compliance_target) {
        appState.selectedBenchmarkTitle = data.compliance_target;
        const stdEl = document.getElementById("spec-standard");
        if (stdEl) {
          stdEl.textContent = data.compliance_target;
          stdEl.title = data.compliance_target;
        }
      }
      showToast(
        "Upload Successful",
        `Target: ${data.compliance_target || file.name}`,
        "success",
      );
      // Auto-trigger parsing
      parseBenchmark();
    } else {
      showToast("Upload Failed", data.error || "Unknown error", "error");
    }
  } catch (err) {
    hideLoading();
    showToast("Upload Error", err.message, "error");
  }
}

// Alias for uploadPdfFile
function uploadPdfFile(input) {
  handleFileUpload({ target: input });
}

// Parse Benchmark Rules
async function parseBenchmark() {
  const path = document.getElementById("pdf-path-input").value.trim();
  showLoading(
    "Parsing CIS Benchmark PDF",
    "Extracting security rules, levels, and registry targets (approx 15-25s)...",
  );

  try {
    const res = await fetch("/api/parse-benchmark", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        pdf_path: path,
        benchmark_title: appState.selectedBenchmarkTitle || "",
      }),
    });
    const data = await res.json();
    hideLoading();

    if (data.success) {
      appState.rules = data.rules || [];
      if (data.compliance_target) {
        appState.selectedBenchmarkTitle = data.compliance_target;
        const stdEl = document.getElementById("spec-standard");
        if (stdEl) {
          stdEl.textContent = data.compliance_target;
          stdEl.title = data.compliance_target;
        }
      }
      updateKPICards(data.total_rules, 0, data.total_rules, 0.0);
      showToast(
        "Benchmark Parsed",
        `Successfully extracted ${data.total_rules} security rules for ${data.compliance_target || "CIS Benchmark"}. Ready to run live audit!`,
        "success",
      );
    } else {
      showToast("Parsing Failed", data.error || "Unknown error", "error");
    }
  } catch (err) {
    hideLoading();
    showToast("Parsing Request Failed", err.message, "error");
  }
}

// Execute Live Security Audit
async function executeAudit() {
  const selectedHive = document.getElementById("hive-select").value;
  const pdfPath = document.getElementById("pdf-path-input")?.value.trim() || "";

  showLoading(
    "Auditing Windows Registry",
    `Scanning security policies against ${selectedHive}...`,
  );

  try {
    const res = await fetch("/api/audit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        hive: selectedHive,
        pdf_path: pdfPath,
        benchmark_title: appState.selectedBenchmarkTitle || "",
      }),
    });
    const data = await res.json();
    hideLoading();

    if (data.success) {
      appState.auditRecords = data.records || [];
      appState.failedRecords = appState.auditRecords.filter(
        (r) => r.status !== "PASS",
      );

      updateKPICards(
        data.total_rules,
        data.passed,
        data.failed,
        data.score_pct,
      );
      renderAuditTable();
      renderHardeningTable();
      fetchAnalytics();

      switchTab("tab-audit");
      showToast(
        "Audit Completed",
        `Scanned ${data.total_rules} rules: ${data.passed} Passed, ${data.failed} Failed (Score: ${data.score_pct}%)`,
        "success",
      );
    } else {
      showToast("Audit Failed", data.error || "Unknown error", "error");
    }
  } catch (err) {
    hideLoading();
    showToast("Audit Request Failed", err.message, "error");
  }
}

// Update KPI Cards UI
function updateKPICards(total, passed, failed, score) {
  document.getElementById("kpi-total").textContent = total;
  document.getElementById("kpi-passed").textContent = passed;
  document.getElementById("kpi-failed").textContent = failed;
  document.getElementById("kpi-score").textContent = `${score}%`;

  const statusEl = document.getElementById("kpi-status-text");
  if (statusEl) {
    if (score >= 80) statusEl.textContent = "High Compliance";
    else if (score >= 50) statusEl.textContent = "Moderate Compliance";
    else statusEl.textContent = "Hardening Required";
  }
}

function getSeverityBadge(severity) {
  const sev = (severity || "Medium").trim();
  const sevLower = sev.toLowerCase();
  if (sevLower.includes("crit")) {
    return `<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-purple-950/80 text-purple-300 border border-purple-700/70">Critical</span>`;
  } else if (sevLower.includes("high")) {
    return `<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-950/80 text-rose-300 border border-rose-700/70">High</span>`;
  } else if (sevLower.includes("med")) {
    return `<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold uppercase bg-amber-950/80 text-amber-300 border border-amber-700/70">Medium</span>`;
  } else {
    return `<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium uppercase bg-cyan-950/80 text-cyan-300 border border-cyan-700/70">Low</span>`;
  }
}

// Render Audit Results Table
function renderAuditTable() {
  const tbody = document.getElementById("audit-table-body");
  const query = document.getElementById("audit-search").value.toLowerCase();
  const filterStatus = document.getElementById("filter-status").value;
  const filterLevel = document.getElementById("filter-level").value;
  const filterSeverity = document.getElementById("filter-severity") ? document.getElementById("filter-severity").value : "ALL";

  let filtered = appState.auditRecords.filter((r) => {
    const matchesQuery =
      !query ||
      (r.rule_id && r.rule_id.toLowerCase().includes(query)) ||
      (r.title && r.title.toLowerCase().includes(query)) ||
      (r.path && r.path.toLowerCase().includes(query));

    const matchesStatus = filterStatus === "ALL" || r.status === filterStatus;
    const matchesLevel = filterLevel === "ALL" || (r.level && r.level.includes(filterLevel));
    const matchesSeverity = filterSeverity === "ALL" || (r.severity && r.severity.toLowerCase() === filterSeverity.toLowerCase());

    return matchesQuery && matchesStatus && matchesLevel && matchesSeverity;
  });

  tbody.innerHTML = "";
  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-slate-500">No matching audit rules found.</td></tr>`;
    document.getElementById("audit-count-label").textContent =
      `Showing 0 of ${appState.auditRecords.length} rules`;
    return;
  }

  filtered.forEach((r, idx) => {
    const isPass = r.status === "PASS";
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-800/40 transition-colors";
    tr.innerHTML = `
            <td class="py-2.5 px-3 text-center text-slate-400">${idx + 1}</td>
            <td class="py-2.5 px-3 text-center">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${isPass ? "bg-emerald-950 text-emerald-400 border border-emerald-700/60" : "bg-rose-950 text-rose-400 border border-rose-700/60"}">
                    ${isPass ? "PASS" : "FAIL"}
                </span>
            </td>
            <td class="py-2.5 px-3 text-center font-mono text-slate-300 font-semibold">${escapeHtml(r.rule_id)}</td>
            <td class="py-2.5 px-3 text-center text-slate-400 text-[11px] font-mono">${escapeHtml(r.level)}</td>
            <td class="py-2.5 px-3 text-center">${getSeverityBadge(r.severity)}</td>
            <td class="py-2.5 px-4 text-slate-200 leading-relaxed">${escapeHtml(r.title)}</td>
            <td class="py-2.5 px-4 font-mono text-[11px] text-slate-400 break-all">${escapeHtml(r.path)}</td>
        `;
    tbody.appendChild(tr);
  });

  document.getElementById("audit-count-label").textContent =
    `Showing ${filtered.length} of ${appState.auditRecords.length} rules`;
}

function filterAuditTable() {
  renderAuditTable();
}

// Filter Hardening Remediation Table
function filterHardeningTable() {
  renderHardeningTable();
}

// Render Hardening Remediation Table
function renderHardeningTable() {
  const tbody = document.getElementById("hardening-table-body");
  const master = document.getElementById("hardening-select-all");
  const countLabel = document.getElementById("hardening-count-label");
  const searchInput = document.getElementById("hardening-search");
  const levelSelect = document.getElementById("hardening-filter-level");
  const sevSelect = document.getElementById("hardening-filter-severity");

  const query = searchInput ? searchInput.value.toLowerCase().trim() : "";
  const filterLevel = levelSelect ? levelSelect.value : "ALL";
  const filterSeverity = sevSelect ? sevSelect.value : "ALL";

  tbody.innerHTML = "";

  const allCount = appState.failedRecords.length;
  if (allCount === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-slate-500">No failed security rules identified. System is fully compliant!</td></tr>`;
    if (master) master.checked = false;
    if (countLabel) countLabel.textContent = "0 non-compliant rules";
    return;
  }

  // Filter non-compliant records
  const filtered = appState.failedRecords.filter((r) => {
    const matchesQuery =
      !query ||
      (r.rule_id && r.rule_id.toLowerCase().includes(query)) ||
      (r.title && r.title.toLowerCase().includes(query)) ||
      (r.path && r.path.toLowerCase().includes(query));

    const matchesLevel =
      filterLevel === "ALL" || (r.level && r.level.includes(filterLevel));

    const matchesSeverity =
      filterSeverity === "ALL" || (r.severity && r.severity.toLowerCase() === filterSeverity.toLowerCase());

    return matchesQuery && matchesLevel && matchesSeverity;
  });

  if (countLabel) {
    countLabel.textContent = `Showing ${filtered.length} of ${allCount} rules (${appState.selectedHardeningPaths.size} selected)`;
  }

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-slate-500">No non-compliant rules match your search filter.</td></tr>`;
    if (master) master.checked = false;
    return;
  }

  // Synchronize master checkbox state (checked if all currently visible filtered items are selected)
  if (master) {
    const allFilteredSelected = filtered.every((r) => appState.selectedHardeningPaths.has(r.path));
    master.checked = allFilteredSelected && filtered.length > 0;
  }

  filtered.forEach((r, idx) => {
    const isChecked = appState.selectedHardeningPaths.has(r.path);
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-800/40 transition-colors";

    const tdCheck = document.createElement("td");
    tdCheck.className = "py-2.5 px-3 text-center";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = isChecked;
    checkbox.className = "rounded border-slate-700 text-brand-700 focus:ring-brand-700 cursor-pointer";
    checkbox.addEventListener("change", (e) => {
      if (e.target.checked) {
        appState.selectedHardeningPaths.add(r.path);
      } else {
        appState.selectedHardeningPaths.delete(r.path);
      }
      if (master) {
        master.checked = filtered.every((item) => appState.selectedHardeningPaths.has(item.path));
      }
      if (countLabel) {
        countLabel.textContent = `Showing ${filtered.length} of ${allCount} rules (${appState.selectedHardeningPaths.size} selected)`;
      }
    });
    tdCheck.appendChild(checkbox);
    tr.appendChild(tdCheck);

    const tdId = document.createElement("td");
    tdId.className = "py-2.5 px-3 text-center font-mono text-slate-300 font-semibold";
    tdId.textContent = r.rule_id;
    tr.appendChild(tdId);

    const tdLevel = document.createElement("td");
    tdLevel.className = "py-2.5 px-3 text-center text-slate-400 text-[11px] font-mono";
    tdLevel.textContent = r.level;
    tr.appendChild(tdLevel);

    const tdSev = document.createElement("td");
    tdSev.className = "py-2.5 px-3 text-center";
    tdSev.innerHTML = getSeverityBadge(r.severity);
    tr.appendChild(tdSev);

    const tdTitle = document.createElement("td");
    tdTitle.className = "py-2.5 px-4 text-slate-200";
    tdTitle.textContent = r.title;
    tr.appendChild(tdTitle);

    const tdPath = document.createElement("td");
    tdPath.className = "py-2.5 px-4 font-mono text-[11px] text-slate-400 break-all";
    tdPath.textContent = r.path;
    tr.appendChild(tdPath);

    tbody.appendChild(tr);
  });
}

function toggleSelectAllHardening(fromMasterCheckbox = false) {
  const master = document.getElementById("hardening-select-all");
  const searchInput = document.getElementById("hardening-search");
  const levelSelect = document.getElementById("hardening-filter-level");
  const sevSelect = document.getElementById("hardening-filter-severity");

  const query = searchInput ? searchInput.value.toLowerCase().trim() : "";
  const filterLevel = levelSelect ? levelSelect.value : "ALL";
  const filterSeverity = sevSelect ? sevSelect.value : "ALL";

  const targetList = appState.failedRecords.filter((r) => {
    const matchesQuery =
      !query ||
      (r.rule_id && r.rule_id.toLowerCase().includes(query)) ||
      (r.title && r.title.toLowerCase().includes(query)) ||
      (r.path && r.path.toLowerCase().includes(query));

    const matchesLevel =
      filterLevel === "ALL" || (r.level && r.level.includes(filterLevel));

    const matchesSeverity =
      filterSeverity === "ALL" || (r.severity && r.severity.toLowerCase() === filterSeverity.toLowerCase());

    return matchesQuery && matchesLevel && matchesSeverity;
  });

  if (targetList.length === 0) return;

  if (fromMasterCheckbox) {
    if (master && master.checked) {
      targetList.forEach((r) => appState.selectedHardeningPaths.add(r.path));
    } else {
      targetList.forEach((r) => appState.selectedHardeningPaths.delete(r.path));
    }
  } else {
    // Toggled from the "Select / Deselect All" button
    const isAllSelected = targetList.every((r) => appState.selectedHardeningPaths.has(r.path));
    if (isAllSelected) {
      targetList.forEach((r) => appState.selectedHardeningPaths.delete(r.path));
      if (master) master.checked = false;
    } else {
      targetList.forEach((r) => appState.selectedHardeningPaths.add(r.path));
      if (master) master.checked = true;
    }
  }
  renderHardeningTable();
}

// Execute Hardening
async function executeHardening() {
  const paths = Array.from(appState.selectedHardeningPaths);
  if (paths.length === 0) {
    showToast("Selection Needed", "Please select at least one rule checkbox to harden.", "warning");
    return;
  }

  showLoading(
    "Applying Hardening Configurations",
    `Enforcing ${paths.length} registry security policies...`,
  );

  try {
    const res = await fetch("/api/harden", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paths: paths, backup: true }),
    });
    const data = await res.json();
    hideLoading();

    if (data.success) {
      let msg =
        `Applied: ${data.success_count} | Failed: ${data.fail_count}`;
      if (data.denied_count > 0)
        msg += ` | Denied: ${data.denied_count} (Need Admin)`;
      
      showToast("Hardening Completed", msg, "success");

      // Re-run audit to reflect changes
      executeAudit();
    } else {
      showToast("Hardening Error", data.error, "error");
    }
  } catch (err) {
    hideLoading();
    showToast("Hardening Request Failed", err.message, "error");
  }
}

// Trigger Registry Backup
async function triggerBackup() {
  showLoading(
    "Backing up Registry",
    "Exporting security hives using reg.exe...",
  );
  try {
    const res = await fetch("/api/backup-registry", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paths: [] }),
    });
    const data = await res.json();
    hideLoading();
    if (data.success) {
      showToast(
        "Registry Backup Created",
        `Backup file generated successfully at:\n${data.path}`,
        "success",
      );
    } else {
      showToast("Backup Failed", data.error, "error");
    }
  } catch (err) {
    hideLoading();
    showToast("Backup Request Failed", err.message, "error");
  }
}

// Download Excel & CSV Reports
function downloadExcelReport() {
  window.location.href = "/api/export-excel";
}

function downloadRulesExcel() {
  window.location.href = "/api/export-rules-excel";
}

function downloadCSVReport() {
  window.location.href = "/api/export-csv";
}

// Fetch Analytics & Render Chart.js
async function fetchAnalytics() {
  try {
    const res = await fetch("/api/analytics");
    const data = await res.json();
    if (data.success) {
      renderCharts(data);
    }
  } catch (err) {
    console.error("Analytics fetch error:", err);
  }
}

function renderCharts(analytics) {
  // 1. Detection / Compliance Pie Chart
  const ctx1 = document.getElementById("chart-detection");
  if (ctx1) {
    if (appState.charts.detection) appState.charts.detection.destroy();
    appState.charts.detection = new Chart(ctx1, {
      type: "doughnut",
      data: {
        labels: ["Pass (Compliant)", "Fail (Non-Compliant)"],
        datasets: [
          {
            data: [
              analytics.detection_rate.pass,
              analytics.detection_rate.fail,
            ],
            backgroundColor: ["#10B981", "#EF4444"],
            borderWidth: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: "#CBD5E1", font: { size: 11 } },
          },
        },
      },
    });
  }

  // 2. Categories Doughnut Chart
  const ctx2 = document.getElementById("chart-categories");
  if (ctx2) {
    const labels = Object.keys(analytics.categories);
    const values = Object.values(analytics.categories);
    if (appState.charts.categories) appState.charts.categories.destroy();
    appState.charts.categories = new Chart(ctx2, {
      type: "pie",
      data: {
        labels: labels.map((l) =>
          l === "sys" ? "SYSTEM (HKLM)" : l === "s/w" ? "SOFTWARE (HKLM)" : l,
        ),
        datasets: [
          {
            data: values,
            backgroundColor: [
              "#6366F1",
              "#06B6D4",
              "#F59E0B",
              "#EC4899",
              "#8B5CF6",
            ],
            borderWidth: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: "#CBD5E1", font: { size: 11 } },
          },
        },
      },
    });
  }

  // 3. System Subcategories Bar Chart
  const ctx3 = document.getElementById("chart-system");
  if (ctx3) {
    const sysLabels = Object.keys(analytics.system_subcategories);
    const passVals = sysLabels.map(
      (l) => analytics.system_subcategories[l].pass,
    );
    const failVals = sysLabels.map(
      (l) => analytics.system_subcategories[l].fail,
    );

    if (appState.charts.system) appState.charts.system.destroy();
    appState.charts.system = new Chart(ctx3, {
      type: "bar",
      data: {
        labels: sysLabels,
        datasets: [
          { label: "Pass", data: passVals, backgroundColor: "#10B981" },
          { label: "Fail", data: failVals, backgroundColor: "#EF4444" },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: "#94A3B8" }, grid: { color: "#1E293B" } },
          y: { ticks: { color: "#94A3B8" }, grid: { color: "#1E293B" } },
        },
        plugins: {
          legend: {
            position: "top",
            labels: { color: "#CBD5E1", font: { size: 11 } },
          },
        },
      },
    });
  }

  // 4. Software Subcategories Bar Chart
  const ctx4 = document.getElementById("chart-software");
  if (ctx4) {
    const swLabels = Object.keys(analytics.software_subcategories);
    const passVals = swLabels.map(
      (l) => analytics.software_subcategories[l].pass,
    );
    const failVals = swLabels.map(
      (l) => analytics.software_subcategories[l].fail,
    );

    if (appState.charts.software) appState.charts.software.destroy();
    appState.charts.software = new Chart(ctx4, {
      type: "bar",
      data: {
        labels: swLabels,
        datasets: [
          { label: "Pass", data: passVals, backgroundColor: "#10B981" },
          { label: "Fail", data: failVals, backgroundColor: "#EF4444" },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: "#94A3B8" }, grid: { color: "#1E293B" } },
          y: { ticks: { color: "#94A3B8" }, grid: { color: "#1E293B" } },
        },
        plugins: {
          legend: {
            position: "top",
            labels: { color: "#CBD5E1", font: { size: 11 } },
          },
        },
      },
    });
  }
}

// Helpers
function showLoading(title, msg) {
  document.getElementById("modal-loading-title").textContent = title;
  document.getElementById("modal-loading-msg").textContent = msg;
  document.getElementById("modal-loading").classList.remove("hidden");
}

function hideLoading() {
  document.getElementById("modal-loading").classList.add("hidden");
}

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
