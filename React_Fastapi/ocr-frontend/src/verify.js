import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import axios from "axios";  // Import axios for API requests
import "./App.css";
import myImage from "./assets/image.jpg";
import logo from "./assets/logo.png";
import { BASE_URL } from "./components/config";
const VerifyPassword = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [email] = useState(location.state?.email || "");  // Email is passed via state
    const [otp, setOtp] = useState("");
    const [message, setMessage] = useState("");  // To display messages like success or error
    const [loading, setLoading] = useState(false);  // Loading state for the button

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!otp) {
            setMessage("❌ Please enter OTP.");
            return;
        }

        setLoading(true);  // Start loading state

        try {
            // Make API call to verify OTP
            const response = await axios.post(`${BASE_URL}/verify-otp`, {
                email_id: email,
                otp: otp
            });

            // If OTP is verified successfully
            setMessage(response.data.message || "OTP verified successfully.");
            setTimeout(() => {
                setLoading(false);
                // After OTP verification, navigate to the ResetPassword page
                navigate("/ResetPassword", { state: { email } });
            }, 2000); // Delay before navigating

        } catch (error) {
            setLoading(false);  // End loading state
            console.error("Error verifying OTP:", error);
            setMessage("❌ Invalid OTP or session expired. Please try again.");
        }
    };

    return (
        <div className="container1">
            <div className="image-section">
                <img src={myImage} alt="Preview" className="image-preview" />
            </div>

            <div className="logo">
                <img src={logo} alt="Logo" className="logo-overlay" />
                <div className="welcome-text">Welcome to MasCallNet</div>
            </div>

            <div className="login-section">
                <h2>Verify OTP</h2>

                <form onSubmit={handleSubmit}>
                    <div className="input-group">
                        <input type="email" value={email} disabled />
                    </div><br></br>

                    <div className="input-group">
                        <input
                            type="text"
                            placeholder="Enter your OTP"
                            value={otp}
                            onChange={(e) => setOtp(e.target.value)}
                            required
                        />
                    </div><br></br>

                    <button type="submit" disabled={loading}>
                        {loading ? "Verifying..." : "Verify OTP"}
                    </button>
                </form>

                {/* Message Display */}
                {message && <p className="message">{message}</p>}

                <p>
                    <Link to="/">Back to Login</Link>
                </p>
            </div>
        </div>
    );
};

export default VerifyPassword;
