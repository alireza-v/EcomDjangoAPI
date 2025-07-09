import React, { useState,useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function Register() {
        const [email, setEmail] = useState("test@email.com");
        const [password, setPassword] = useState("123qwe!@#");
        const [message, setMessage] = useState("");
        const navigate = useNavigate();
        const [showPassword, setShowPassword] = useState(false);

        const toggleVisibility = () => {
                setShowPassword((prev) => !prev);
        };

        useEffect(() => {
                document.title = "Register";
        },[]);

        const handleRegister = async (e) => {
                e.preventDefault();
                setMessage(""); // Clear previous messages

                try {
                        const response = await axios.post("http://localhost:9000/auth/users/", {
                                email,
                                password,
                        });
                        setMessage("✅ Registration successful! Please check your email to activate your account.");
                        setTimeout(() => {
                                navigate("/login");
                        }, 2000);
                } catch (error) {
                        if (error.response?.data) {
                                const errorData = error.response.data;
                                const formatted = Object.entries(errorData)
                                        .map(([key, val]) => `${key}: ${val}`)
                                        .join("\n");
                                setMessage(`❌ Error:\n${formatted}`);
                        } else {
                                setMessage("❌ An unknown error occurred.");
                        }
                }
        };

        return (
                <div>
                        <h2>Register</h2>
                        <form onSubmit={handleRegister}>
                                <input
                                        type="email"
                                        placeholder="Email"
                                        value={email}
                                        required
                                        onChange={(e) => setEmail(e.target.value)} />
                                <br />
                                <input
                                        type={showPassword?"text":"password"}
                                        value={password}
                                        required
                                        onChange={(e) => setPassword(e.target.value)}
                                        placeholder="Password" />
                                <button type="button" onClick={toggleVisibility}>{showPassword ? "Hide" : "Show"}</button>
                                <br />
                                <button type="submit">Register</button>
                        </form>
                        {message && <p>{message}</p>}
                </div>
        );
}
export default Register;

