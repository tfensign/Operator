import axios from 'axios';
import { Message, Checklist, PendingSend, Integration } from '../types';

const API_URL = 'http://localhost:3001';

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const api = {
  // Auth
  setupMasterPassword: (password: string) =>
    client.post('/auth/setup', { master_password: password }),

  unlockApp: (password: string) =>
    client.post('/auth/unlock', { master_password: password }),

  isInitialized: () =>
    client.get('/auth/initialized'),

  // Messages
  getMessages: (platform?: string, priorityMin?: number, priorityMax?: number) =>
    client.get('/messages', { params: { platform, priority_min: priorityMin, priority_max: priorityMax } }),

  getMessage: (id: number) =>
    client.get(`/messages/${id}`),

  searchMessages: (query: string) =>
    client.post('/messages/search', { query_text: query }),

  markMessageRead: (id: number) =>
    client.patch(`/messages/${id}`, { read_at: new Date().toISOString() }),

  deleteMessage: (id: number) =>
    client.patch(`/messages/${id}`, { deleted_at: new Date().toISOString() }),

  // Checklists
  getChecklists: () =>
    client.get('/checklists'),

  getChecklist: (id: number) =>
    client.get(`/checklists/${id}`),

  createChecklist: (title: string, description?: string) =>
    client.post('/checklists', { title, description }),

  createChecklistFromMessage: (messageId: number, title?: string) =>
    client.post(`/checklists/from-message/${messageId}`, { title }),

  addChecklistItem: (checklistId: number, text: string) =>
    client.post(`/checklists/${checklistId}/items`, { text }),

  markItemComplete: (checklistId: number, itemId: number) =>
    client.patch(`/checklists/${checklistId}/items/${itemId}`, {}),

  // Send
  createDraft: (platform: string, to_address: string, subject: string, body: string) =>
    client.post('/send/draft', { platform, to_address, subject, body }),

  getPendingSends: () =>
    client.get('/send/pending'),

  approveSend: (id: number, masterPassword: string) =>
    client.post(`/send/${id}/approve`, { master_password: masterPassword }),

  rejectSend: (id: number) =>
    client.post(`/send/${id}/reject`, {}),

  getSentHistory: () =>
    client.get('/send/history'),

  // Integrations
  getIntegrations: () =>
    client.get('/integrations'),

  getIntegration: (platform: string) =>
    client.get(`/integrations/${platform}`),

  setupIntegration: (platform: string, credentials: Record<string, string>, masterPassword: string) =>
    client.post(`/integrations/${platform}`, { credentials }, {
      params: { master_password: masterPassword }
    }),

  deleteIntegration: (platform: string) =>
    client.delete(`/integrations/${platform}`)
};
