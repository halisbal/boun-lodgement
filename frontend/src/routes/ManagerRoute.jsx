import React from "react";
import { Navigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";

export const ManagerRoute = ({ children }) => {
  const { isLoggedIn, user } = useAuth();

  if (!isLoggedIn) {
    // Redirect to the login page if not logged in
    return <Navigate to="/login" />;
  }
  if(user.role !== 'manager'){
    return <Navigate to="/login" />;
  }

  return children; // If logged in, render the children components (the protected route's content)
};