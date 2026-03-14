import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const matchApi = {
    chat: (matchId: string, query: string) =>
        api.post('/chat', { match_id: matchId, query }),

    getAwards: (matchId: string) =>
        api.get(`/match/${matchId}/awards`),

    getFlow: (matchId: string) =>
        api.get(`/match/${matchId}/flow`),

    getInsights: (matchId: string) =>
        api.get(`/match/${matchId}/insights`),

    getScorecard: (matchId: string) =>
        api.get(`/match/${matchId}/scorecard`),

    recommendPvP: (matchId: string, query: string) =>
        api.post(`/match/${matchId}/recommend/pvp`, { match_id: matchId, query }),

    recommendStrategy: (matchId: string, query: string) =>
        api.post(`/match/${matchId}/recommend/strategy`, { match_id: matchId, query }),

    recommendPressure: (matchId: string, query: string) =>
        api.post(`/match/${matchId}/recommend/pressure`, { match_id: matchId, query }),
};

export default api;
