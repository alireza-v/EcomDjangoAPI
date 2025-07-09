import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import CategoryList from "./components/products/CategoryList";
import Register from "./components/authentication/Register";
import Login from "./components/authentication/Login";
import ActivateAccount from "./components/authentication/ActivateEmail";
import ConfirmPassword from "./components/authentication/ConfirmPasswordChange";
import NavigationBar from "./NavigationBar";
import { AuthProvider, useAuth } from './context/AuthContext'; // Import AuthProvider and useAuth


const AuthenticatedContent = () => {
  return <h2>Welcome, Authenticated User!</h2>;
};

// A simple wrapper for components that need auth check
const ProtectedRouteWrapper = ({ children }) => {
  const { isAuthenticated, isLoadingAuth } = useAuth();

  if (isLoadingAuth) {
    return <div>Loading authentication...</div>; // Or a proper spinner
  }

  if (!isAuthenticated) {
    // You can redirect them here if they're not logged in,
    // or the ProtectedRoute component can handle it.
    return <div>Please log in to view this page.</div>; // Fallback for demonstration
  }

  return children;
};

function App() {
  return (
    <AuthProvider>
      {" "}
      {/* Wrap your entire app with AuthProvider */}
      <Router>
        <NavigationBar /> {/* Navigation bar can now consume AuthContext */}
        <Routes>
          <Route path="/" element={<CategoryList />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />{" "}
         
          <Route
            path="/"
            element={
              <ProtectedRouteWrapper>
                <CategoryList />
              </ProtectedRouteWrapper>
            }
          />

        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
