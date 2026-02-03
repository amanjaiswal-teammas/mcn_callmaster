import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { Eye, EyeOff } from "lucide-react"; // ✅ Import professional eye icons
import './App.css';
import myImage from './assets/image.jpg';
import logo from './assets/logo.png';
import { BASE_URL } from "./components/config";

const ResetPassword = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const email = location.state?.email || ""; // Ensure email is passed correctly

    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [message, setMessage] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    // Handle Password Reset
    const handleSubmit = async (e) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            setMessage("❌ Passwords do not match.");
            return;
        }

        try {
            const response = await axios.post(`${BASE_URL}/reset-password`, {
                email_id: email,  // API requires email_id as a key
                new_password: password,
                confirm_password: confirmPassword
            });

            setMessage(response.data.message || "✅ Password reset successfully.");
            setTimeout(() => navigate("/"), 2000); // Redirect to login page after 2 seconds
        } catch (error) {
            console.error("Error resetting password:", error);
            setMessage("❌ Failed to reset password. Try again.");
        }
    };

    return (
        <div className="container1">
            {/* Left Section (Image) */}
            <div className="image-section">
                <img src={myImage} alt="Preview" className="image-preview" />
            </div>

            {/* Logo & Welcome Text */}
            <div className="logo">
                <img src={logo} alt="Logo" className="logo-overlay" />
                <div className="welcome-text">Welcome to MasCallNet</div>
            </div>

            {/* Right Section (Password Reset Form) */}
            <div className="login-section">
                <h2>Reset Password</h2>

                <form onSubmit={handleSubmit}>
                    <input
                        type="email"
                        value={email}
                        disabled
                        className="disabled-input"
                    /><br />
                    <br></br>
                    {/* New Password Field with Toggle Eye Icon */}
                    <div className="input-group password-group">
                        <div className="password-wrapper">
                            <input
                                type={showPassword ? "text" : "password"}
                                placeholder="New Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                            <span
                                className="eye-icon"
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </span>
                        </div>
                    </div><br></br>

                    {/* Confirm Password Field with Toggle Eye Icon */}
                    <div className="input-group password-group">
                        <div className="password-wrapper">
                            <input
                                type={showConfirmPassword ? "text" : "password"}
                                placeholder="Confirm Password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                            />
                            <span
                                className="eye-icon"
                                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            >
                                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </span>
                        </div>
                    </div><br></br>

                    <button type="submit">Reset Password</button>
                </form>

                {/* Message Display */}
                {message && <p className="message">{message}</p>}

                {/* Back to Login */}
                <p>
                    <Link to="/">Back to Login</Link>
                </p>
            </div>
        </div>
    );
};

export default ResetPassword;
