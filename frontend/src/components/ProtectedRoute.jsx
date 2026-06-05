import React, { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';

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
      full_name: decoded.full_name || decoded.email?.split('@')[0] || 'User',
    };
  } catch (e) {
    return null;
  }
}

export const ProtectedRoute = () => {
  const [authChecked, setAuthChecked] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const token = localStorage.getItem('token');

  useEffect(() => {
    if (token) {
      const decoded = decodeToken(token);
      if (decoded) {
        setIsAuthenticated(true);
      } else {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setIsAuthenticated(false);
      }
    } else {
      setIsAuthenticated(false);
    }
    setAuthChecked(true);
  }, [token]);

  if (!authChecked) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 text-slate-500 font-semibold text-sm">
        Authenticating...
      </div>
    );
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
