import axios from 'axios';

// Base URL for the FastAPI backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach Authorization header if access token exists in localStorage
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to format backend error messages cleanly
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'An unexpected error occurred. Please try again.';
    
    if (error.response) {
      // Backend error response from FastAPI
      const detail = error.response.data?.detail;
      if (typeof detail === 'string') {
        message = detail;
      } else if (Array.isArray(detail)) {
        // Pydantic validation error array
        message = detail[0]?.msg || 'Invalid request input.';
      } else if (error.response.status === 401) {
        message = 'Invalid credentials or session expired.';
      } else if (error.response.status === 404) {
        message = 'Requested resource not found.';
      }
    } else if (error.request) {
      message = 'Unable to connect to server. Please ensure the backend is running.';
    }

    return Promise.reject(new Error(message));
  }
);

// Auth API Calls
export async function loginApi(email, password) {
  // FastAPI OAuth2PasswordRequestForm expects application/x-www-form-urlencoded
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await api.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data; // { access_token, type }
}

export async function registerApi(email, password) {
  const response = await api.post('/auth/signup', { email, password });
  return response.data; // { email }
}

export async function logoutApi() {
  const response = await api.get('/auth/logout');
  return response.data; // { details: "Logged out" }
}

// Wallet API Calls
export async function getWalletsApi(walletId = null) {
  const params = walletId ? { wallet_id: walletId } : {};
  const response = await api.get('/wallet/', { params });
  return response.data; // { wallet: active_wallet, wallets: [all_wallets] }
}

export async function getTransactionsApi(walletId = null, limit = 20) {
  const params = { limit };
  if (walletId) {
    params.wallet_id = walletId;
  }
  const response = await api.get('/wallet/transactions', { params });
  return response.data; // { transactions: [...] }
}

export async function depositApi(walletId, amount, reference = '') {
  const response = await api.post('/wallet/deposit', {
    amount: Number(amount),
    reference: reference || null,
  }, {
    params: { wallet_id: walletId }
  });
  return response.data; // TransactionOperationRead
}

export async function withdrawApi(walletId, amount, reference = '') {
  const response = await api.post('/wallet/withdraw', {
    amount: Number(amount),
    reference: reference || null,
  }, {
    params: { wallet_id: walletId }
  });
  return response.data; // TransactionOperationRead
}

export async function transferApi(sourceWalletId, destinationWalletId, amount, reference = '') {
  const response = await api.post('/wallet/transfer', {
    source_wallet_id: sourceWalletId,
    destination_wallet_id: destinationWalletId,
    amount: Number(amount),
    reference: reference || null,
  });
  return response.data; // TransferRead
}

export default api;
