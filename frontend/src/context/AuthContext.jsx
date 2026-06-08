import React, { createContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api, { authService, profileService } from '../services/api';

export const AuthContext = createContext(undefined);

function decodeToken(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      window
        .atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    const decoded = JSON.parse(jsonPayload);
    return {
      id: decoded.sub || '',
      email: decoded.email || '',
      full_name: decoded.full_name || null,
      created_at: null,
    };
  } catch (e) {
    return null;
  }
}

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;
    const initAuth = async () => {
      if (token) {
        const decodedUser = decodeToken(token);
        if (decodedUser) {
          if (!cancelled) setUser(decodedUser);
          try {
            const profile = await profileService.getCurrentUser();
            if (!cancelled) {
              setUser((prev) => ({
                ...prev,
                full_name: profile.full_name,
                created_at: profile.created_at,
              }));
            }
          } catch (e) {
            if (!cancelled) console.error("Failed to fetch profile metadata:", e);
          }
        } else {
          localStorage.removeItem('token');
          if (!cancelled) setToken(null);
        }
      }
      if (!cancelled) setIsLoading(false);
    };
    initAuth();
    return () => { cancelled = true; };
  }, [token]);

  const login = async (email, password) => {
    setIsLoading(true);
    try {
      const data = await authService.login(email, password);
      localStorage.setItem('token', data.access_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
      setToken(data.access_token);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email, password, fullName) => {
    setIsLoading(true);
    try {
      const data = await authService.register(email, password, fullName);
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
        setToken(data.access_token);
      } else {
        await login(email, password);
      }
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
    setToken(null);
    setUser(null);
    navigate('/', { replace: true });
  };

  const updateUser = (updatedFields) => {
    setUser((prev) => ({ ...prev, ...updatedFields }));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        isLoading,
        login,
        register,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
