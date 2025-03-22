import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import LoginSignup from "./App.tsx"; // Now the login/signup page
import RecipeDetail from "./RecipeDetail.tsx";
import Recipes from "./Recipes.tsx";
import { validateToken, logout } from "./utils/auth.ts";
import "./index.css";

// ProtectedRoute component to handle redirection based on auth status
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const checkToken = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        setIsAuthenticated(false);
        return;
      }

      const isValid = await validateToken(token);
      if (!isValid) {
        // If token is invalid, clear it and redirect to login
        logout(navigate);
        setIsAuthenticated(false);
      } else {
        setIsAuthenticated(true);
      }
    };

    checkToken();
  }, [navigate]);

  // Show a loading state while validating the token
  if (isAuthenticated === null) {
    return <div>Loading...</div>;
  }

  // If authenticated, redirect to /recipes when trying to access /
  if (isAuthenticated && window.location.pathname === "/") {
    return <Navigate to="/recipes" replace />;
  }

  return children;
};

// AuthenticatedRoute for protected routes (e.g., /recipes, /recipe/:id)
const AuthenticatedRoute = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const checkToken = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        setIsAuthenticated(false);
        return;
      }

      const isValid = await validateToken(token);
      if (!isValid) {
        // If token is invalid, clear it and redirect to login
        logout(navigate);
        setIsAuthenticated(false);
      } else {
        setIsAuthenticated(true);
      }
    };

    checkToken();
  }, [navigate]);

  if (isAuthenticated === null) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return children;
};

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <LoginSignup />
            </ProtectedRoute>
          }
        />
        <Route
          path="/recipes"
          element={
            <AuthenticatedRoute>
              <Recipes />
            </AuthenticatedRoute>
          }
        />
        <Route
          path="/recipe/:id"
          element={
            <AuthenticatedRoute>
              <RecipeDetail />
            </AuthenticatedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);