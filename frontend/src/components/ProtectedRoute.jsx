import React from 'react';
import { Navigate } from 'react-router-dom';

function isTokenExpired(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

export const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  if (!token || isTokenExpired(token)) {
    localStorage.removeItem('token');
    return <Navigate to="/" replace />;
  }
  return children;
};

export default ProtectedRoute;
