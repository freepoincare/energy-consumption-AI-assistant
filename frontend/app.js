// ============================================================
// Electricity Assistant — Main Frontend Application Logic
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    let currentConversationId = null;
    let energyChart = null;
    let cachedSummary = null;
    let cachedDailyRecords = [];

    // ─── DOM Elements ───────────────────────────────────────────
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");
    const btnSend = document.getElementById("btn-send");
    const btnNewChat = document.getElementById("btn-new-chat");
    const conversationList = document.getElementById("conversation-list");
    const currentChatTitle = document.getElementById("current-chat-title");

    // KPI Elements
    const metricAvg = document.getElementById("metric-avg");
    const metricTotal = document.getElementById("metric-total");
    const metricMax = document.getElementById("metric-max");
    const metricMin = document.getElementById("metric-min");
    const metricMaxDate = document.getElementById("metric-max-date");
    const metricMinDate = document.getElementById("metric-min-date");
    const headerDateRange = document.getElementById("header-date-range");
    const chartSubtitle = document.getElementById("chart-subtitle");

    // Insights
    const insightsContent = document.getElementById("insights-content");

    // CRUD Elements
    const dailyDataTbody = document.getElementById("daily-data-tbody");
    const btnAddRecord = document.getElementById("btn-add-record");
    const btnExportCsv = document.getElementById("btn-export-csv");
    const dataModal = document.getElementById("data-modal");
    const modalTitle = document.getElementById("modal-title");
    const dataForm = document.getElementById("data-form");
    const formRecordId = document.getElementById("form-record-id");
    const formDate = document.getElementById("form-date");
    const formValue = document.getElementById("form-value");
    const formMemo = document.getElementById("form-memo");
    const btnModalCancel = document.getElementById("btn-modal-cancel");
    const btnModalClose = document.getElementById("btn-modal-close");

    // Sidebar
    const sidebarHistory = document.getElementById("sidebar-history");
    const sidebarBackdrop = document.getElementById("sidebar-backdrop");
    const btnHistoryToggle = document.getElementById("btn-history-toggle");
    const btnSidebarClose = document.getElementById("btn-sidebar-close");

    // Dark Mode
    const btnDarkMode = document.getElementById("btn-dark-mode");

    // Quick Questions
    const quickQuestions = document.getElementById("quick-questions");

    // ─── Initialize ─────────────────────────────────────────────
    initDarkMode();
    init();

    async function init() {
        await Promise.all([
            loadSummary(),
            loadDailyData(),
            loadConversations()
        ]);
    }

    // ============================================================
    // DARK MODE
    // ============================================================
    function initDarkMode() {
        const saved = localStorage.getItem("theme");
        if (saved === "dark") {
            document.documentElement.setAttribute("data-theme", "dark");
            toggleDarkModeIcons(true);
        }
    }

    btnDarkMode.addEventListener("click", () => {
        const isDark = document.documentElement.getAttribute("data-theme") === "dark";
        if (isDark) {
            document.documentElement.removeAttribute("data-theme");
            localStorage.setItem("theme", "light");
            toggleDarkModeIcons(false);
        } else {
            document.documentElement.setAttribute("data-theme", "dark");
            localStorage.setItem("theme", "dark");
            toggleDarkModeIcons(true);
        }
        // Update chart colors if chart exists
        if (energyChart) updateChartTheme();
    });

    function toggleDarkModeIcons(isDark) {
        const sunIcon = btnDarkMode.querySelector(".icon-sun");
        const moonIcon = btnDarkMode.querySelector(".icon-moon");
        if (sunIcon) sunIcon.style.display = isDark ? "none" : "block";
        if (moonIcon) moonIcon.style.display = isDark ? "block" : "none";
    }

    // ============================================================
    // SIDEBAR (Conversation History)
    // ============================================================
    function openSidebar() {
        sidebarHistory.classList.add("open");
        sidebarBackdrop.classList.add("active");
    }

    function closeSidebar() {
        sidebarHistory.classList.remove("open");
        sidebarBackdrop.classList.remove("active");
    }

    btnHistoryToggle.addEventListener("click", openSidebar);
    btnSidebarClose.addEventListener("click", closeSidebar);
    sidebarBackdrop.addEventListener("click", closeSidebar);

    // ============================================================
    // TOAST NOTIFICATIONS
    // ============================================================
    function showToast(message, type = "info") {
        const container = document.getElementById("toast-container");
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transition = "opacity 0.3s";
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // ============================================================
    // 1. DATA SUMMARY & KPI CARDS
    // ============================================================
    async function loadSummary() {
        try {
            const summary = await ApiService.getSummary();
            cachedSummary = summary;
            renderSummary(summary);
            renderInsights(summary);
        } catch (error) {
            console.error("Failed to load summary:", error);
            metricAvg.innerHTML = '<span class="error-state">Error</span>';
            metricTotal.innerHTML = '<span class="error-state">Error</span>';
            insightsContent.innerHTML = '<div class="error-state">Unable to load summary data.</div>';
        }
    }

    function renderSummary(summary) {
        if (!summary) return;
        const overall = summary.overall || {};
        const extremes = summary.extremes || {};
        const period = summary.period || {};
        const cost = summary.cost || {};

        // KPI Cards
        metricAvg.textContent = overall.average_daily_consumption_kwh || 0;
        metricTotal.textContent = (overall.total_consumption_kwh || 0).toLocaleString();

        if (extremes.maximum_day) {
            metricMax.textContent = `${extremes.maximum_day.consumption_kwh} kWh`;
            metricMaxDate.textContent = `${extremes.maximum_day.date} (${extremes.maximum_day.day_of_week})`;
        }
        if (extremes.minimum_day) {
            metricMin.textContent = `${extremes.minimum_day.consumption_kwh} kWh`;
            metricMinDate.textContent = `${extremes.minimum_day.date} (${extremes.minimum_day.day_of_week})`;
        }

        // Header date range
        if (period.start_date && period.end_date) {
            headerDateRange.textContent = `${period.start_date} — ${period.end_date}`;
            chartSubtitle.textContent = `Daily usage from ${period.start_date} to ${period.end_date} (${period.duration_days} days)`;
        }
    }

    // ============================================================
    // 2. ENERGY INSIGHTS
    // ============================================================
    function renderInsights(summary) {
        if (!summary) return;
        const ww = summary.weekday_weekend || {};
        const dow = summary.day_of_week || {};
        const recent = summary.recent || {};
        const trend = summary.trend || {};
        const cost = summary.cost || {};

        let html = "";

        // Weekday vs Weekend
        html += `
            <div class="insight-item">
                <h4>Weekly Pattern</h4>
                <div class="insight-row"><span class="label">Weekdays</span><span class="value">${ww.weekday_average_kwh || 0} kWh/day</span></div>
                <div class="insight-row"><span class="label">Weekends</span><span class="value">${ww.weekend_average_kwh || 0} kWh/day</span></div>
                <div class="insight-note">${ww.pattern_description || ''}</div>
            </div>
        `;

        // Day of Week
        if (dow.highest_consumption_day && dow.lowest_consumption_day) {
            html += `
                <div class="insight-item">
                    <h4>Day of Week</h4>
                    <div class="insight-row"><span class="label">Highest</span><span class="value">${dow.highest_consumption_day.day} (${dow.highest_consumption_day.average_kwh} kWh)</span></div>
                    <div class="insight-row"><span class="label">Lowest</span><span class="value">${dow.lowest_consumption_day.day} (${dow.lowest_consumption_day.average_kwh} kWh)</span></div>
                </div>
            `;
        }

        // Recent Periods
        const r7 = recent.recent_7_days || {};
        const r30 = recent.recent_30_days || {};
        html += `
            <div class="insight-item">
                <h4>Recent Activity</h4>
                <div class="insight-row"><span class="label">Last 7 days</span><span class="value">${r7.average_daily_kwh || 0} kWh/day</span></div>
                <div class="insight-row"><span class="label">Last 30 days</span><span class="value">${r30.average_daily_kwh || 0} kWh/day</span></div>
                <div class="insight-note">7-day vs overall: ${r7.percentage_vs_overall_avg > 0 ? '+' : ''}${r7.percentage_vs_overall_avg || 0}%</div>
            </div>
        `;

        // Trend
        const shortTrend = trend.short_term_trend || {};
        const overallTrend = trend.overall_trend || {};
        html += `
            <div class="insight-item">
                <h4>Trend</h4>
                <div class="insight-row"><span class="label">Short-term</span><span class="value">${capitalize(shortTrend.direction || 'stable')}</span></div>
                <div class="insight-row"><span class="label">Long-term</span><span class="value">${capitalize(overallTrend.direction || 'stable')} (${overallTrend.long_term_change_percentage > 0 ? '+' : ''}${overallTrend.long_term_change_percentage || 0}%)</span></div>
            </div>
        `;

        // Estimated Cost
        if (cost && cost.total_estimated_cost_gbp) {
            html += `
                <div class="insight-item">
                    <h4>Estimated Cost</h4>
                    <div class="insight-row"><span class="label">Total</span><span class="value">£${cost.total_estimated_cost_gbp}</span></div>
                    <div class="insight-row"><span class="label">Daily Avg</span><span class="value">£${cost.average_daily_estimated_cost_gbp}/day</span></div>
                    <div class="insight-note" style="color: var(--text-secondary); font-style: italic;">Estimated only — not official billing</div>
                </div>
            `;
        }

        insightsContent.innerHTML = html;
    }

    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    // ============================================================
    // 3. CHART (Chart.js)
    // ============================================================
    function renderChart(records) {
        if (!records || records.length === 0) return;

        const sorted = [...records].sort((a, b) => a.date.localeCompare(b.date));
        const labels = sorted.map(r => r.date);
        const values = sorted.map(r => r.value);

        const isDark = document.documentElement.getAttribute("data-theme") === "dark";
        const gridColor = isDark ? "rgba(45,49,72,0.6)" : "rgba(226,229,240,0.8)";
        const textColor = isDark ? "#8b92a5" : "#6b7280";

        const ctx = document.getElementById("energy-chart").getContext("2d");

        if (energyChart) energyChart.destroy();

        energyChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Daily Consumption (kWh)",
                    data: values,
                    borderColor: "#3b82f6",
                    backgroundColor: "rgba(59,130,246,0.08)",
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: "#3b82f6",
                    pointHoverBorderColor: "#fff",
                    pointHoverBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: "index",
                    intersect: false
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: isDark ? "#1a1d27" : "#fff",
                        titleColor: isDark ? "#e4e7ec" : "#1a1d2e",
                        bodyColor: isDark ? "#8b92a5" : "#6b7280",
                        borderColor: isDark ? "#2d3148" : "#e2e5f0",
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            title: (items) => items[0].label,
                            label: (item) => `${item.parsed.y.toFixed(2)} kWh`
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: {
                            color: textColor,
                            font: { size: 11 },
                            maxTicksLimit: 12,
                            maxRotation: 45
                        },
                        border: { color: gridColor }
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: {
                            color: textColor,
                            font: { size: 11 },
                            callback: (val) => val + " kWh"
                        },
                        border: { display: false },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    function updateChartTheme() {
        if (!energyChart) return;
        const isDark = document.documentElement.getAttribute("data-theme") === "dark";
        const gridColor = isDark ? "rgba(45,49,72,0.6)" : "rgba(226,229,240,0.8)";
        const textColor = isDark ? "#8b92a5" : "#6b7280";

        energyChart.options.scales.x.ticks.color = textColor;
        energyChart.options.scales.x.border.color = gridColor;
        energyChart.options.scales.y.grid.color = gridColor;
        energyChart.options.scales.y.ticks.color = textColor;
        energyChart.options.plugins.tooltip.backgroundColor = isDark ? "#1a1d27" : "#fff";
        energyChart.options.plugins.tooltip.titleColor = isDark ? "#e4e7ec" : "#1a1d2e";
        energyChart.options.plugins.tooltip.bodyColor = isDark ? "#8b92a5" : "#6b7280";
        energyChart.options.plugins.tooltip.borderColor = isDark ? "#2d3148" : "#e2e5f0";
        energyChart.update();
    }

    // ============================================================
    // 4. QUICK QUESTIONS
    // ============================================================
    quickQuestions.addEventListener("click", (e) => {
        const chip = e.target.closest(".chip");
        if (!chip) return;
        const question = chip.getAttribute("data-question");
        if (question) {
            chatInput.value = question;
            chatForm.dispatchEvent(new Event("submit", { cancelable: true }));
        }
    });

    // ============================================================
    // 5. DAILY ENERGY DATA MANAGEMENT (CRUD)
    // ============================================================
    async function loadDailyData() {
        try {
            const result = await ApiService.listEnergyData();
            const records = result.records || [];
            cachedDailyRecords = records;
            renderDailyTable(records);
            renderChart(records);
        } catch (error) {
            console.error("Failed to load daily data:", error);
            dailyDataTbody.innerHTML = `<tr><td colspan="4" class="error-state">Failed to load records. Check backend connection.</td></tr>`;
        }
    }

    function renderDailyTable(records) {
        dailyDataTbody.innerHTML = "";
        if (records.length === 0) {
            dailyDataTbody.innerHTML = `<tr><td colspan="4" class="empty-state">No daily records found</td></tr>`;
            return;
        }

        // Sort descending by date so most recent appears on top
        const displayRecords = [...records].sort((a, b) => b.date.localeCompare(a.date));

        displayRecords.forEach(rec => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${rec.date}</strong></td>
                <td>${rec.value} kWh</td>
                <td title="${rec.memo || ''}">${rec.memo ? (rec.memo.length > 25 ? rec.memo.substring(0, 25) + '...' : rec.memo) : '<span style="color:var(--text-secondary)">—</span>'}</td>
                <td>
                    <button class="btn-action edit" data-id="${rec.id}" aria-label="Edit record for ${rec.date}">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                        Edit
                    </button>
                    <button class="btn-action delete" data-id="${rec.id}" aria-label="Delete record for ${rec.date}">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                        Del
                    </button>
                </td>
            `;

            tr.querySelector(".btn-action.edit").addEventListener("click", () => openEditModal(rec));
            tr.querySelector(".btn-action.delete").addEventListener("click", () => handleDeleteRecord(rec.id));

            dailyDataTbody.appendChild(tr);
        });
    }

    // ─── Modal ──────────────────────────────────────────────────
    function openAddModal() {
        modalTitle.textContent = "Add Daily Energy Record";
        formRecordId.value = "";
        formDate.disabled = false;
        formDate.value = new Date().toISOString().substring(0, 10);
        formValue.value = "";
        formMemo.value = "";
        dataModal.classList.add("active");
    }

    function openEditModal(record) {
        modalTitle.textContent = `Edit Record (${record.date})`;
        formRecordId.value = record.id;
        formDate.value = record.date;
        formDate.disabled = true;
        formValue.value = record.value;
        formMemo.value = record.memo || "";
        dataModal.classList.add("active");
    }

    function closeModal() {
        dataModal.classList.remove("active");
    }

    btnModalCancel.addEventListener("click", closeModal);
    if (btnModalClose) btnModalClose.addEventListener("click", closeModal);
    btnAddRecord.addEventListener("click", openAddModal);

    // Close modal on backdrop click
    dataModal.addEventListener("click", (e) => {
        if (e.target === dataModal) closeModal();
    });

    dataForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const id = formRecordId.value;
        const dateVal = formDate.value;
        const val = parseFloat(formValue.value);
        const memoVal = formMemo.value.trim() || null;

        try {
            if (id) {
                await ApiService.updateEnergyData(id, { value: val, memo: memoVal });
                showToast("Record updated successfully", "success");
            } else {
                await ApiService.createEnergyData({ date: dateVal, value: val, memo: memoVal });
                showToast("Record added successfully", "success");
            }
            closeModal();
            await Promise.all([loadDailyData(), loadSummary()]);
        } catch (error) {
            showToast(`Error saving record: ${error.message}`, "error");
        }
    });

    async function handleDeleteRecord(id) {
        if (!confirm(`Are you sure you want to delete the record for ${id}?`)) return;
        try {
            await ApiService.deleteEnergyData(id);
            showToast("Record deleted", "success");
            await Promise.all([loadDailyData(), loadSummary()]);
        } catch (error) {
            showToast(`Failed to delete: ${error.message}`, "error");
        }
    }

    // ─── Data Export (CSV) ──────────────────────────────────────
    function exportDailyDataToCsv() {
        if (!cachedDailyRecords || cachedDailyRecords.length === 0) {
            showToast("No stored daily records available to export", "error");
            return;
        }

        // Sort chronologically ascending for standard timeseries data export
        const exportRecords = [...cachedDailyRecords].sort((a, b) => a.date.localeCompare(b.date));

        // CSV Header (clean, user-facing timeseries export)
        const headers = ["date", "consumption_kwh", "memo"];

        // Build CSV rows with proper quote escaping for RFC 4180 compliance
        const rows = exportRecords.map(rec => {
            const dateStr = `"${(rec.date || '').replace(/"/g, '""')}"`;
            const valStr = rec.value !== undefined && rec.value !== null ? rec.value : 0;
            const memoStr = `"${(rec.memo || '').replace(/"/g, '""')}"`;
            return [dateStr, valStr, memoStr].join(",");
        });

        const csvContent = [headers.join(","), ...rows].join("\r\n");
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        const startDate = exportRecords[0].date;
        const endDate = exportRecords[exportRecords.length - 1].date;

        link.setAttribute("href", url);
        link.setAttribute("download", `daily_energy_consumption_${startDate}_to_${endDate}.csv`);
        link.style.visibility = "hidden";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        showToast(`Exported ${exportRecords.length} daily energy records to CSV`, "success");
    }

    if (btnExportCsv) {
        btnExportCsv.addEventListener("click", exportDailyDataToCsv);
    }

    // ============================================================
    // 6. AI CHAT & CONVERSATION HISTORY
    // ============================================================
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const msg = chatInput.value.trim();
        if (!msg) return;

        appendMessage("user", msg);
        chatInput.value = "";
        btnSend.disabled = true;

        const loaderId = appendTypingIndicator();

        try {
            const resp = await ApiService.sendChatMessage(msg, currentConversationId);
            removeTypingIndicator(loaderId);
            appendMessage("assistant", resp.reply);

            if (!currentConversationId && resp.conversation_id) {
                currentConversationId = resp.conversation_id;
            }
            await loadConversations();
        } catch (error) {
            removeTypingIndicator(loaderId);
            appendMessage("assistant", `Unable to get a response: ${error.message}`);
        } finally {
            btnSend.disabled = false;
            chatInput.focus();
        }
    });

    function appendMessage(role, content) {
        const bubble = document.createElement("div");
        bubble.className = `message-bubble ${role}`;
        const p = document.createElement("p");
        p.textContent = content;
        bubble.appendChild(p);
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendTypingIndicator() {
        const id = `typing-${Date.now()}`;
        const bubble = document.createElement("div");
        bubble.id = id;
        bubble.className = "message-bubble assistant typing-indicator";
        bubble.innerHTML = `<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>`;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    function removeTypingIndicator(id) {
        const elem = document.getElementById(id);
        if (elem) elem.remove();
    }

    // ─── Conversation List ──────────────────────────────────────
    async function loadConversations() {
        try {
            const res = await ApiService.listConversations();
            renderConversationList(res.conversations || []);
        } catch (error) {
            console.error("Failed to load conversations:", error);
        }
    }

    function renderConversationList(conversations) {
        conversationList.innerHTML = "";
        if (conversations.length === 0) {
            conversationList.innerHTML = `<div class="empty-state">No conversations yet</div>`;
            return;
        }

        conversations.forEach(conv => {
            const item = document.createElement("div");
            item.className = `conversation-item ${conv.id === currentConversationId ? 'active' : ''}`;

            const titleSpan = document.createElement("span");
            titleSpan.className = "conv-title";
            titleSpan.title = conv.title;
            titleSpan.textContent = conv.title;

            const deleteBtn = document.createElement("button");
            deleteBtn.className = "btn-delete-conv";
            deleteBtn.title = "Delete conversation";
            deleteBtn.setAttribute("aria-label", "Delete conversation");
            deleteBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;

            item.appendChild(titleSpan);
            item.appendChild(deleteBtn);

            item.addEventListener("click", (e) => {
                if (e.target.closest(".btn-delete-conv")) return;
                selectConversation(conv.id);
                closeSidebar();
            });

            deleteBtn.addEventListener("click", async (e) => {
                e.stopPropagation();
                if (confirm(`Delete conversation "${conv.title}"?`)) {
                    await ApiService.deleteConversation(conv.id);
                    showToast("Conversation deleted", "info");
                    if (currentConversationId === conv.id) {
                        startNewChat();
                    } else {
                        loadConversations();
                    }
                }
            });

            conversationList.appendChild(item);
        });
    }

    async function selectConversation(convId) {
        try {
            const conv = await ApiService.getConversation(convId);
            if (!conv) return;

            currentConversationId = conv.id;

            // Update title — preserve the SVG icon
            const titleEl = document.getElementById("current-chat-title");
            const svgIcon = titleEl.querySelector("svg");
            titleEl.textContent = conv.title;
            if (svgIcon) titleEl.prepend(svgIcon);

            chatMessages.innerHTML = "";

            if (conv.messages && conv.messages.length > 0) {
                conv.messages.forEach(m => appendMessage(m.role, m.content));
            } else {
                chatMessages.innerHTML = `<div class="message-bubble assistant"><p>Empty conversation. Ask a question to start.</p></div>`;
            }

            renderConversationList((await ApiService.listConversations()).conversations || []);
        } catch (error) {
            showToast(`Failed to load conversation: ${error.message}`, "error");
        }
    }

    function startNewChat() {
        currentConversationId = null;

        const titleEl = document.getElementById("current-chat-title");
        const svgIcon = titleEl.querySelector("svg");
        titleEl.textContent = "Energy AI Assistant";
        if (svgIcon) titleEl.prepend(svgIcon);

        chatMessages.innerHTML = `
            <div class="message-bubble assistant">
                <p>Hello! I'm your personal electricity consumption assistant. I've analyzed your 6-month energy data (March\u2013August 2026). Ask me about usage patterns, trends, or comparisons!</p>
            </div>
        `;
        loadConversations();
    }

    btnNewChat.addEventListener("click", () => {
        startNewChat();
        closeSidebar();
    });
});
