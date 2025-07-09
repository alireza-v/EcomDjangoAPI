import React, { createContext, useState, useEffect, useContext } from "react";

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authToken, setAuthToken] = useState(null);
  const [isLoadingAuth, setIsLoadingAuth] = useState(true); // To indicate if auth check is in progress

  useEffect(() => {
    // Check localStorage for token on initial load
    const token = localStorage.getItem("auth_token");
    if (token) {
      setAuthToken(token);
      setIsAuthenticated(true);
    }
    setIsLoadingAuth(false); // Auth check complete
  }, []);

  const login = (token) => {
    localStorage.setItem("auth_token", token);
    setAuthToken(token);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem("auth_token");
    setAuthToken(null);
    setIsAuthenticated(false);
  };

  const contextValue = {
    isAuthenticated,
    authToken,
    isLoadingAuth,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};

// Custom hook to easily consume auth context
export const useAuth = () => {
  return useContext(AuthContext);
};
