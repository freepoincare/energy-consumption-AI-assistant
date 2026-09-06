// API Client Configuration & Base URL
const CONFIG = {
    API_BASE_URL: window.API_BASE_URL || window.location.origin
};

class ApiService {
    static async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',   // JSON 데이터를 주고받음을 명시
            ...(options.headers || {})
        };

        try {
            const response = await fetch(url, { ...options, headers });
            if (!response.ok) {                   // 응답 코드가 200번대가 아닐 경우 에러 처리
                let errorDetail = `HTTP Error ${response.status}`;
                try {
                    const errJson = await response.json();
                    errorDetail = errJson.detail || errorDetail;    // 서버 에러 발생 시 (예: 404, 500), 서버가 보낸 에러 메시지(errJson.detail)를 알려줌
                } catch (e) {}
                throw new Error(errorDetail);
            }
            return await response.json();   // 성공 시 JSON 결과 반환
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

    // AI Chat (사용자 입력 메시지를 서버의 AI 엔진으로 보냄. 기존 대화가 있다면 conversationId를 함께 보내 대화 맥락을 유지)
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

window.ApiService = ApiService;     // 다른 파일(예: app.js)에서도 import 없이 ApiService.getSummary()와 같은 방식으로 바로 사용 가능
