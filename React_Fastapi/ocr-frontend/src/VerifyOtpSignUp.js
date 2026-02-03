import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import "./App.css";
import myImage from "./assets/image.jpg";
import logo from "./assets/logo.png";
import { BASE_URL } from "./components/config";

const VerifyOtpSignUp = () => {
    const navigate = useNavigate();
    
    // Retrieve email & phone from localStorage
    const email_id = localStorage.getItem("email_id") || "";
    const contact_number = localStorage.getItem("contact_number") || "";

    // OTP states
    const [emailOtp, setEmailOtp] = useState("");  // Email OTP
    const [mobileOtp, setMobileOtp] = useState("");  // Mobile OTP
    const [message, setMessage] = useState("");  // Status messages
    const [loading, setLoading] = useState(false);  // Loading state

    // Function to verify OTP
    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validate OTP fields
        if (!emailOtp || !mobileOtp) {
            setMessage("❌ Please enter both OTPs.");
            return;
        }

        if (!email_id || !contact_number) {
            setMessage("❌ Missing email or phone number. Please restart the process.");
            return;
        }

        setLoading(true);  // Start loading

        try {
            // API call to verify OTP
            const response = await axios.post(
                `${BASE_URL}/verify-otp-login`,
                {
                    email_id: email_id,
                    contact_number: contact_number,
                    otp: emailOtp,   // Email OTP
                    mobile_otp: mobileOtp,  // Mobile OTP
                },
                {
                    headers: {
                        "Content-Type": "application/json",  // Ensure correct content type
                    },
                }
            );

            // OTP verified successfully
            setMessage(response.data.detail || "✅ OTP verified successfully.");
            setTimeout(() => {
                setLoading(false);
                // Navigate to ResetPassword after verification
                navigate("/", { state: { email: email_id } });
            }, 2000);

        } catch (error) {
            setLoading(false);  // Stop loading
            console.error("Error verifying OTP:", error);

            // Handle error response
            const errorMessage = error.response?.data?.detail || "❌ Invalid OTP or session expired. Please try again.";
            setMessage(errorMessage);
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
                    {/* Mobile OTP Input */}
                    <div className="input-group">
                        <input
                            type="text"
                            placeholder="Enter your Mobile OTP"
                            value={mobileOtp}
                            onChange={(e) => setMobileOtp(e.target.value)}
                            required
                        />
                    </div><br />

                    {/* Email OTP Input */}
                    <div className="input-group">
                        <input
                            type="text"
                            placeholder="Enter your Email OTP"
                            value={emailOtp}
                            onChange={(e) => setEmailOtp(e.target.value)}
                            required
                        />
                    </div><br />

                    {/* Submit Button */}
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

export default VerifyOtpSignUp;
