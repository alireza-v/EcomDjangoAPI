import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";

function ConfirmPassword() {
        const { uid, token } = useParams();
        const [new_password, set_new_password] = useState("");
        const [message, setMessage] = useState("");
        const navigate = useNavigate();
        const [showPassword, setShowPassword] = useState(false);

        const toggleVisibility = () => {
                setShowPassword((prev) => !prev);
        };

        useEffect(() => {
                document.title = "Confirm password.";
        }, []);

        const handle_confirm_password = async (e) => {
                e.preventDefault();
                try {
                        const response = await axios.post("http://localhost:9000/auth/users/reset_password_confirm/", {
                                uid,
                                token,
                                new_password,
                        });
                        setMessage("Password reset success!");
                        setTimeout(() => {
                                navigate("/login");
                        }, 2000);
                } catch (error) {
                        console.error("Something went wrong during password reset.");
                        console.error(error);
                }
        };

        return (
                <div>
                        <h2>Confirm password</h2>
                        <form onSubmit={handle_confirm_password}>
                                <input
                                        type={showPassword ? "text" : "password"}
                                        value={new_password}
                                        onChange={(e) => set_new_password(e.target.value)}
                                        placeholder="Password"
                                        required
                                />
                                <button type="button" onClick={toggleVisibility}>
                                        {showPassword ? "Hide" : "Show"}
                                </button>
                                <button type="submit">Confirm password</button>
                        </form>
                        {message && <p>{message}</p>}
                </div>
        );
}

export default ConfirmPassword;
