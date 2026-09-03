// API Client Configuration & Base URL
const CONFIG = {
    API_BASE_URL: window.API_BASE_URL || window.location.origin
};

class ApiService {
    static async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };

        try {
            const response = await fetch(url, { ...options, headers });
            if (!response.ok) {
                let errorDetail = `HTTP Error ${response.status}`;
                try {
                    const errJson = await response.json();
                    errorDetail = errJson.detail || errorDetail;
                } catch (e) {}
                throw new Error(errorDetail);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error on ${endpoint}:`, error);
            throw error;
        }
    }

    // Energy Summary
    static async getSummary() {
        return this.request('/api/data/summary');
    }

    // Daily Energy CRUD
    static async listEnergyData() {
        return this.request('/api/data');
    }

    static async getEnergyData(id) {
        return this.request(`/api/data/${id}`);
    }

    static async createEnergyData(data) {
        return this.request('/api/data', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static async updateEnergyData(id, data) {
        return this.request(`/api/data/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    static async deleteEnergyData(id) {
        return this.request(`/api/data/${id}`, {
            method: 'DELETE'
        });
    }

    // AI Chat
    static async sendChatMessage(message, conversationId = null) {
        return this.request('/api/chat', {
            method: 'POST',
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId
            })
        });
    }

    // Conversations
    static async listConversations() {
        return this.request('/api/conversations');
    }

    static async getConversation(id) {
        return this.request(`/api/conversations/${id}`);
    }

    static async deleteConversation(id) {
        return this.request(`/api/conversations/${id}`, {
            method: 'DELETE'
        });
    }
}

window.ApiService = ApiService;
