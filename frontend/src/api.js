const API_BASE = '/api';

let activeUserEmail = 'alice@example.com';

export function setActiveUserEmail(email) {
  activeUserEmail = email;
}

export function getActiveUserEmail() {
  return activeUserEmail;
}

async function request(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    'X-User-Email': activeUserEmail,
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get('content-type');
  const isJson = contentType && contentType.includes('application/json');
  const data = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const errorMsg = (data && data.detail) || response.statusText || 'Request failed';
    throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
  }

  return data;
}

export const api = {
  getUsers: () => request('/users'),
  getCurrentUser: () => request('/users/me'),
  getTickets: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.status && filters.status !== 'ALL') params.append('status', filters.status);
    if (filters.category && filters.category !== 'ALL') params.append('category', filters.category);
    if (filters.priority && filters.priority !== 'ALL') params.append('priority', filters.priority);
    const queryString = params.toString();
    return request(`/tickets${queryString ? `?${queryString}` : ''}`);
  },
  getTicket: (id) => request(`/tickets/${id}`),
  createTicket: (payload) =>
    request('/tickets', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateTicket: (id, payload) =>
    request(`/tickets/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
  updateTicketStatus: (id, status) =>
    request(`/tickets/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),
  addComment: (ticketId, content) =>
    request(`/tickets/${ticketId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    }),
};
