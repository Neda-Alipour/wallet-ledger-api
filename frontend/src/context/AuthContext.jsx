import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginApi, registerApi, logoutApi, getWalletsApi } from '../api/api';
import { decodeJwt } from '../utils/jwt';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [user, setUser] = useState(() => {
    const savedToken = localStorage.getItem('token');
    if (!savedToken) return null;
    const decoded = decodeJwt(savedToken);
    return decoded?.user || null;
  });
  const [loading, setLoading] = useState(true);

  // Validate existing token session on app start
  useEffect(() => {
    async function verifyAuth() {
      if (!token) {
        setLoading(false);
        return;
      }
      
      try {
        // Ping wallet endpoint to verify token validity
        await getWalletsApi();
        const decoded = decodeJwt(token);
        setUser(decoded?.user || { name: 'User' });
      } catch (err) {
        // Token invalid or expired
        console.warn('Session expired or token invalid:', err.message);
        handleLogoutLocally();
      } finally {
        setLoading(false);
      }
    }

    verifyAuth();
  }, [token]);

  const handleLogin = async (email, password) => {
    const data = await loginApi(email, password);
    const accessToken = data.access_token;
    
    localStorage.setItem('token', accessToken);
    setToken(accessToken);
    
    const decoded = decodeJwt(accessToken);
    const userData = decoded?.user || { name: email, id: '' };
    setUser(userData);
    return userData;
  };

  const handleRegister = async (email, password) => {
    await registerApi(email, password);
    // After registration, log the user in automatically
    return handleLogin(email, password);
  };

  const handleLogoutLocally = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const handleLogout = async () => {
    try {
      if (token) {
        await logoutApi();
      }
    } catch (err) {
      console.error('Logout error on server:', err.message);
    } finally {
      handleLogoutLocally();
    }
  };

  const value = {
    token,
    user,
    isAuthenticated: Boolean(token),
    loading,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
