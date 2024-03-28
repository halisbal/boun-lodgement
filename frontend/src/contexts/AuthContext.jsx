import React, { useState } from "react";
import { useEffect } from "react";
import authService from "../services/authService";

export const AuthContext = React.createContext();

export const AuthProvider = ({ children }) => {
  console.log("AuthProvider");
  const [user, setUser] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = authService.getToken();

    if (token) {
      authService.getUserInfo().then((response) => {
        if (response) {
          setUser(response);
          console.log(response);
          setIsLoggedIn(true);
        }
      });
    } else {
      setIsLoggedIn(false);
      setUser(null);
    }
  }, []);

  const login = async (username, password) => {
    const response = await authService.login(username, password);
    if (response) {
      console.log("authlogin true response authcontext login");
      setIsLoggedIn(true);
      const userInfo = await authService.getUserInfo();
      if (userInfo) {
        setUser(userInfo);
      }
      return true;
    }
    return false;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setIsLoggedIn(false);
  };

  const contextValue = {
    user,
    isLoggedIn,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};
