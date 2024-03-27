import React from "react";
import { Navigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";

export const ProtectedRoute = ({ children }) => {
  const { isLoggedIn } = useAuth();

  if (!isLoggedIn) {
    // Redirect to the login page if not logged in
    return <Navigate to="/login" />;
  }

  return children; // If logged in, render the children components (the protected route's content)
};
