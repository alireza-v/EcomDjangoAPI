import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function Login() {
        const [email, setEmail] = useState("alirezasonym5@gmail.com"); // Better to start with empty strings for user input
        const [password, setPassword] = useState("123qwe!@#");
        const [message, setMessage] = useState("");
        const [isSubmitting, setIsSubmitting] = useState(false); // To prevent multiple submissions
        const navigate = useNavigate();
        const [showPassword, setShowPassword] = useState(false);

        // Initial check for authentication token on component mount
        useEffect(() => {
                const auth_token = localStorage.getItem("auth_token");
                if (auth_token) {
                        // If a token exists, immediately redirect without showing the login form
                        // This prevents the flicker of the login form before redirection
                        navigate("/");
                        // Optionally, you could set a message here if you want to notify the user
                        // before the redirect, but direct navigation is usually preferred for login pages.
                }
        }, [navigate]); // navigate should be in the dependency array

        // Set document title
        useEffect(() => {
                document.title = "Login";
        }, []);

        const toggleVisibility = () => {
                setShowPassword((prev) => !prev);
        };

        const handleLogin = async (e) => {
                e.preventDefault(); // Prevent default form submission behavior

                // Prevent multiple submissions
                if (isSubmitting) {
                        return;
                }

                setMessage(""); // Clear previous messages
                setIsSubmitting(true); // Disable the submit button

                try {
                        const response = await axios.post(
                                "http://localhost:9000/auth/token/login/",
                                { email, password },
                                { headers: { "Content-Type": "application/json" } }
                        );

                        // Assuming the token is directly in response.data.auth_token
                        const authToken = response.data.auth_token;

                        if (authToken) {
                                localStorage.setItem("auth_token", authToken);
                                setMessage("✅ Login successful! Redirecting..."); // User sees this message

                                // Use a short delay for the "Login successful" message to be visible
                                setTimeout(() => {
                                        navigate("/"); // Redirect to the home page or dashboard
                                }, 1000); // 1 second delay
                        } else {
                                // This case handles if the API call was successful but no token was returned
                                setMessage("❌ Login successful, but no authentication token received.");
                        }
                } catch (error) {
                        console.error("Login error:", error); // Log the full error for debugging

                        if (error.response?.data) {
                                const errorData = error.response.data;
                                // Check for common error keys like 'non_field_errors' or 'detail'
                                if (errorData.non_field_errors) {
                                        setMessage(`❌ ${errorData.non_field_errors[0]}`);
                                } else if (errorData.detail) {
                                        setMessage(`❌ ${errorData.detail}`);
                                } else {
                                        // Fallback for other errors in the response data
                                        const formatted = Object.entries(errorData)
                                                .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(", ") : val}`)
                                                .join("\n");
                                        setMessage(`❌ ${formatted}`);
                                }
                        } else if (error.request) {
                                // The request was made but no response was received (e.g., network error)
                                setMessage("❌ Network error. Please check your internet connection or server status.");
                        } else {
                                // Something else happened in setting up the request
                                setMessage("❌ An unexpected error occurred.");
                        }
                } finally {
                        setIsSubmitting(false); // Re-enable the submit button regardless of success or failure
                }
        };

        // If the user is already authenticated, don't render the login form at all.
        // The initial useEffect already handles the redirection, so this ensures
        // the component doesn't briefly show the login form after a refresh if already logged in.
        if (localStorage.getItem("auth_token")) {
                return null; // Or a loading spinner if you prefer
        }

        return (
                <div>
                        <h2>Login</h2>
                        <form onSubmit={handleLogin}>
                                <div>
                                        <label htmlFor="email">Email:</label>
                                        <input
                                                id="email"
                                                type="email"
                                                value={email}
                                                placeholder="Enter your email"
                                                onChange={(e) => setEmail(e.target.value)}
                                                required
                                        />
                                </div>
                                <div>
                                        <label htmlFor="password">Password:</label>
                                        <input
                                                id="password"
                                                type={showPassword ? "text" : "password"}
                                                value={password}
                                                placeholder="Enter your password"
                                                onChange={(e) => setPassword(e.target.value)}
                                                required
                                        />
                                        <button type="button" onClick={toggleVisibility} disabled={isSubmitting}>
                                                {showPassword ? "Hide" : "Show"}
                                        </button>
                                </div>
                                <button type="submit" disabled={isSubmitting}>
                                        {isSubmitting ? "Logging in..." : "Login"}
                                </button>
                        </form>
                        {message && <p className={message.startsWith("✅") ? "success-message" : "error-message"}>{message}</p>}
                </div>
        );
}
export default Login;
