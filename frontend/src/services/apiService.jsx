import authService from './authService';

const BASE_ENDPOINT = import.meta.env.VITE_BASE_ENDPOINT+ '/api';

async function fetchAPI(endpoint, options = {}) {
  const url = `${BASE_ENDPOINT}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Token ${authService.getToken()}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    // You can handle errors more granularly if you'd like
    throw new Error(`API call error: ${response.status}`);
  }

  return response.json();
}

export const apiService = {
  get: (endpoint) => fetchAPI(endpoint),
  post: (endpoint, data) => fetchAPI(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  // add other methods like delete, put, patch as needed
};
