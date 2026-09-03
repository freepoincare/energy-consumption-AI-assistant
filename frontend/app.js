// Main Frontend Application Logic
document.addEventListener("DOMContentLoaded", () => {
    let currentConversationId = null;

    // DOM Elements
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");
    const btnSend = document.getElementById("btn-send");
    const btnNewChat = document.getElementById("btn-new-chat");
    const conversationList = document.getElementById("conversation-list");
    const currentChatTitle = document.getElementById("current-chat-title");

    // Summary Elements
    const metricAvg = document.getElementById("metric-avg");
    const metricTotal = document.getElementById("metric-total");
    const metricMax = document.getElementById("metric-max");
    const metricMin = document.getElementById("metric-min");
    const summaryPeriod = document.getElementById("summary-period");
    const summaryTrend = document.getElementById("summary-trend");
    const summaryCost = document.getElementById("summary-cost");

    // CRUD Table Elements
    const dailyDataTbody = document.getElementById("daily-data-tbody");
    const btnAddRecord = document.getElementById("btn-add-record");
    const dataModal = document.getElementById("data-modal");
    const modalTitle = document.getElementById("modal-title");
    const dataForm = document.getElementById("data-form");
    const formRecordId = document.getElementById("form-record-id");
    const formDate = document.getElementById("form-date");
    const formValue = document.getElementById("form-value");
    const formMemo = document.getElementById("form-memo");
    const btnModalCancel = document.getElementById("btn-modal-cancel");

    // Initialize Application
    init();

    async function init() {
        await Promise.all([
            loadSummary(),
            loadDailyData(),
            loadConversations()
        ]);
    }

    // -------------------------------------------------------------
    // 1. DATA SUMMARY SECTION
    // -------------------------------------------------------------
    async function loadSummary() {
        try {
            const summary = await ApiService.getSummary();
            renderSummary(summary);
        } catch (error) {
            console.error("Failed to load summary:", error);
            summaryPeriod.textContent = "Error loading summary";
        }
    }

    function renderSummary(summary) {
        if (!summary) return;
        const overall = summary.overall || {};
        const extremes = summary.extremes || {};
        const period = summary.period || {};
        const trend = summary.trend || {};
        const cost = summary.cost || {};

        metricAvg.textContent = `${overall.average_daily_consumption_kwh || 0} kWh`;
        metricTotal.textContent = `${overall.total_consumption_kwh || 0} kWh`;
        
        if (extremes.maximum_day) {
            metricMax.textContent = `${extremes.maximum_day.consumption_kwh} kWh (${extremes.maximum_day.date.substring(5)})`;
        }
        if (extremes.minimum_day) {
            metricMin.textContent = `${extremes.minimum_day.consumption_kwh} kWh (${extremes.minimum_day.date.substring(5)})`;
        }

        summaryPeriod.textContent = `${period.start_date} ~ ${period.end_date} (${period.duration_days} days)`;
        
        const shortTrend = trend.short_term_trend || {};
        const overTrend = trend.overall_trend || {};
        summaryTrend.textContent = `${overTrend.direction || 'stable'} (${overTrend.long_term_change_percentage || 0}%), 7d: ${shortTrend.direction || 'stable'}`;
        
        summaryCost.textContent = cost.total_estimated_cost_gbp ? `£${cost.total_estimated_cost_gbp} (avg £${cost.average_daily_estimated_cost_gbp}/day)` : 'N/A';
    }

    // -------------------------------------------------------------
    // 2. DAILY ENERGY DATA MANAGEMENT (CRUD)
    // -------------------------------------------------------------
    async function loadDailyData() {
        try {
            const result = await ApiService.listEnergyData();
            renderDailyTable(result.records || []);
        } catch (error) {
            console.error("Failed to load daily data:", error);
            dailyDataTbody.innerHTML = `<tr><td colspan="4" style="color:var(--danger);text-align:center;">Failed to load records</td></tr>`;
        }
    }

    function renderDailyTable(records) {
        dailyDataTbody.innerHTML = "";
        if (records.length === 0) {
            dailyDataTbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--text-muted);">No records found</td></tr>`;
            return;
        }

        // Show latest 30 records descending
        const displayRecords = [...records].reverse().slice(0, 30);

        displayRecords.forEach(rec => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${rec.date}</strong></td>
                <td>${rec.value} kWh</td>
                <td title="${rec.memo || ''}">${rec.memo ? (rec.memo.length > 15 ? rec.memo.substring(0, 15) + '...' : rec.memo) : '-'}</td>
                <td>
                    <button class="btn-action edit" data-id="${rec.id}">Edit</button>
                    <button class="btn-action delete" data-id="${rec.id}">Del</button>
                </td>
            `;

            // Action listeners
            tr.querySelector(".btn-action.edit").addEventListener("click", () => openEditModal(rec));
            tr.querySelector(".btn-action.delete").addEventListener("click", () => handleDeleteRecord(rec.id));

            dailyDataTbody.appendChild(tr);
        });
    }

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
        formDate.disabled = true; // Date serves as document ID
        formValue.value = record.value;
        formMemo.value = record.memo || "";
        dataModal.classList.add("active");
    }

    function closeModal() {
        dataModal.classList.remove("active");
    }

    btnModalCancel.addEventListener("click", closeModal);
    btnAddRecord.addEventListener("click", openAddModal);

    dataForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const id = formRecordId.value;
        const dateVal = formDate.value;
        const val = parseFloat(formValue.value);
        const memoVal = formMemo.value.trim() || null;

        try {
            if (id) {
                // Update
                await ApiService.updateEnergyData(id, { value: val, memo: memoVal });
            } else {
                // Create
                await ApiService.createEnergyData({ date: dateVal, value: val, memo: memoVal });
            }
            closeModal();
            await Promise.all([loadDailyData(), loadSummary()]);
        } catch (error) {
            alert(`Error saving record: ${error.message}`);
        }
    });

    async function handleDeleteRecord(id) {
        if (!confirm(`Are you sure you want to delete record for date ${id}?`)) return;
        try {
            await ApiService.deleteEnergyData(id);
            await Promise.all([loadDailyData(), loadSummary()]);
        } catch (error) {
            alert(`Failed to delete record: ${error.message}`);
        }
    }

    // -------------------------------------------------------------
    // 3. AI CHAT & CONVERSATION HISTORY
    // -------------------------------------------------------------
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const msg = chatInput.value.trim();
        if (!msg) return;

        // Render user message
        appendMessage("user", msg);
        chatInput.value = "";
        btnSend.disabled = true;

        // Show typing indicator
        const loaderId = appendTypingIndicator();

        try {
            const resp = await ApiService.sendChatMessage(msg, currentConversationId);
            removeTypingIndicator(loaderId);
            appendMessage("assistant", resp.reply);

            // Update session ID if new
            if (!currentConversationId && resp.conversation_id) {
                currentConversationId = resp.conversation_id;
            }
            // Refresh conversation list to update titles/ordering
            await loadConversations();
        } catch (error) {
            removeTypingIndicator(loaderId);
            appendMessage("assistant", `⚠️ Error: ${error.message}`);
        } finally {
            btnSend.disabled = false;
        }
    });

    function appendMessage(role, content) {
        const bubble = document.createElement("div");
        bubble.className = `message-bubble ${role}`;
        bubble.textContent = content;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendTypingIndicator() {
        const id = `typing-${Date.now()}`;
        const bubble = document.createElement("div");
        bubble.id = id;
        bubble.className = "message-bubble assistant typing-loader";
        bubble.innerHTML = `<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>`;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    function removeTypingIndicator(id) {
        const elem = document.getElementById(id);
        if (elem) elem.remove();
    }

    // Load conversation list
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
            conversationList.innerHTML = `<div style="font-size:0.8rem;color:var(--text-muted);text-align:center;padding:1rem;">No prior chats</div>`;
            return;
        }

        conversations.forEach(conv => {
            const item = document.createElement("div");
            item.className = `conversation-item ${conv.id === currentConversationId ? 'active' : ''}`;
            item.innerHTML = `
                <span title="${conv.title}" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:180px;">${conv.title}</span>
                <button class="btn-delete-conv" title="Delete conversation">✕</button>
            `;

            // Select conversation click
            item.addEventListener("click", (e) => {
                if (e.target.classList.contains("btn-delete-conv")) return;
                selectConversation(conv.id);
            });

            // Delete conversation click
            item.querySelector(".btn-delete-conv").addEventListener("click", async (e) => {
                e.stopPropagation();
                if (confirm(`Delete conversation "${conv.title}"?`)) {
                    await ApiService.deleteConversation(conv.id);
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
            currentChatTitle.textContent = `💬 ${conv.title}`;
            chatMessages.innerHTML = "";

            if (conv.messages && conv.messages.length > 0) {
                conv.messages.forEach(m => appendMessage(m.role, m.content));
            } else {
                chatMessages.innerHTML = `<div class="message-bubble assistant">Empty conversation. Ask a question to start.</div>`;
            }

            renderConversationList((await ApiService.listConversations()).conversations || []);
        } catch (error) {
            alert(`Failed to load conversation: ${error.message}`);
        }
    }

    function startNewChat() {
        currentConversationId = null;
        currentChatTitle.textContent = "🤖 Energy AI Assistant";
        chatMessages.innerHTML = `
            <div class="message-bubble assistant">
                Hello! I am your personal electricity consumption assistant. I have analyzed your 6-month energy consumption data (March 1 to August 31, 2026). Feel free to ask about your average daily usage, peak days, monthly comparisons, or trends!
            </div>
        `;
        renderConversationList((conversationList.dataset.cachedList ? JSON.parse(conversationList.dataset.cachedList) : []));
        loadConversations();
    }

    btnNewChat.addEventListener("click", startNewChat);
});
