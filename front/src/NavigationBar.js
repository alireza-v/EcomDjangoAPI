import React from "react";
import { Link,useNavigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

function NavigationBar() {
  const { isAuthenticated, logout } = useAuth(); // Get isAuthenticated state and logout function
  const navigate = useNavigate();

  const handleLogout = () => {
    logout(); // Call the logout function from context
    navigate("/login"); // Redirect to login page after logout
  };

  return (
    <nav className="navbar">
      <ul className="nav-links">
       
        {isAuthenticated ? (
          <>
            {/* Links visible only when authenticated */}
            <li>
              <Link to="/">Home</Link>
            </li>

            <li>
              <button onClick={handleLogout} className="nav-button">
                Logout
              </button>
            </li>
          </>
        ) : (
          <>
            {/* Links visible only when not authenticated */}
            <li>
              <Link to="/login">Login</Link>
            </li>
            <li>
              <Link to="/register">Register</Link>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
}
export default NavigationBar;
