import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { Eye, EyeOff } from "lucide-react"; // Professional eye toggle icons
import "./App.css";
import myImage from "./assets/image.jpg";
import logo from "./assets/logo.png";
import { BASE_URL } from "./components/config";
const Login = ({ onLogin }) => {
  const navigate = useNavigate();
  const [email_id, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    if (!email_id || !password) {
      setMessage("⚠️ Please enter both email and password.");
      return;
    }

    try {
      const response = await axios.post(`${BASE_URL}/login`, {
        email_id,
        password
      });

      if (response.status === 200) {
        localStorage.setItem("token", response.data.token);
        localStorage.setItem("username", response.data.username);
        localStorage.setItem("id", response.data.id);
        localStorage.setItem("client_id", response.data.client_id);
        localStorage.setItem("isLoggedIn", JSON.stringify(true));
        localStorage.setItem("set_limit", response.data.set_limit);
        localStorage.setItem("leadid", response.data.leadid);


        localStorage.setItem("contact_number", response.data.contact_number);

        onLogin();
        navigate("/dashboard", { replace: true }); // Prevents going back to login
      } else {
        setMessage("❌ Login failed. Please try again.");
      }
    } catch (error) {
      console.error("Login error:", error);
      setMessage("❌ Invalid email or password.");
    }
  };

  return (
    <div className="container1">
      {/* Left Section */}
      <div className="image-section">
        <img src={myImage} alt="Preview" className="image-preview" />
      </div>
      <div className="logo">
        <img src={logo} alt="Logo" className="logo-overlay" />
        <div className="welcome-text">Welcome to MasCallNet</div>
      </div>

      {/* Right Section */}
      <div className="login-section">
        <h1>Glad to see you back!</h1>
        <h4>Login to continue.</h4>
        <p className="sub-text">Please enter your email and password.</p>

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="email">Email:</label>
            <input
              type="email"
              id="email"
              value={email_id}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g., xyz@gmail.com"
              required
            />
          </div>

          {/* Password Field with Eye Icon */}
          <div className="input-group password-group">
            <label htmlFor="password">Password:</label>
            <div className="password-wrapper">
              <input
                type={showPassword ? "text" : "password"}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
              <span
                className="eye-icon"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </span>
            </div>
          </div>
          <br />

          {message && <p className="error">{message}</p>}

          <button type="submit" className="login-button">Login</button>
        </form>

        <p>
          Don't have an account? <Link to="/signup">Sign up here</Link> |
          <Link to="/forgot-password/testtoken">Forgot Password?</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
