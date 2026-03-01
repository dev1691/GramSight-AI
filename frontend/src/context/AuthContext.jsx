import React, { createContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext(null);

function decodeToken(token) {
  try {
    const payload = token.split('.')[1];
    const json = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(json);
  } catch {
    return null;
  }
}

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('gs_token'));
  const [role, setRole] = useState(() => localStorage.getItem('gs_role') || 'farmer');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      localStorage.setItem('gs_token', token);
      const isDemo = token === 'demo' || token.startsWith('demo.');
      const storedRole = localStorage.getItem('gs_role') || 'farmer';
      if (isDemo) {
        setUser({ email: 'demo@gramsight.ai', role: storedRole });
        setRole(storedRole);
      } else {
        const decoded = decodeToken(token);
        if (decoded) {
          setUser({ ...decoded, email: decoded.sub, role: storedRole });
          setRole(storedRole);
        } else {
          setUser(null);
          setToken(null);
        }
      }
    } else {
      localStorage.removeItem('gs_token');
      setUser(null);
    }
    setLoading(false);
  }, [token]);

  const login = useCallback((accessToken, userRole = 'farmer') => {
    localStorage.setItem('gs_role', userRole);
    setRole(userRole);
    setToken(accessToken);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('gs_token');
    localStorage.removeItem('gs_role');
    setToken(null);
    setRole(null);
    setUser(null);
  }, []);

  const loginDemo = useCallback((userRole = 'farmer') => {
    localStorage.setItem('gs_role', userRole);
    setRole(userRole);
    setToken('demo');
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, role, login, loginDemo, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
