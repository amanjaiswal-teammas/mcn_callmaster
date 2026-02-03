import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./Login";
import Signup from "./signup";
import ResetPassword from "./ResetPassword";
import Dashboard from "./dashboard";
import ForgotPassword from "./forgot";
import VerifyPassword from "./verify";
import VerifyOtpSignUp from "./VerifyOtpSignUp"; 
import APIKey from "./components/APIKey";

import Analysis from "./components/Analysis";
import Prompt from "./components/Prompt";
import Recordings from "./components/Recordings";
import Settings from "./components/Settings";
import Transcription from "./components/Transcription";
import Search from "./components/Search";
import QualityPerformance from "./components/QualityPerformance";
import RawDump from "./components/RawDump";
import RawDownload from "./components/RawDownload";
import Fatal from "./components/FatalAnalysis";
import Details from "./components/DetailAnalysis";
import Potential from "./components/Potential";

import Magical from "./components/Magical";
import Sales_dashboard from "./components/Sales_dashboard";
import Opportunity from "./components/Opportunity";
import Estimated from "./components/Estimated";
import DetailSales from "./components/DetailSales";
import RawSales from "./components/RawSales";
import UserDashboardSelection from "./components/UserDashboardSelection";
import Calling from "./components/Calling";

import UploadHelp from './pages/UploadHelp';
import ApiHelp from './pages/ApiHelp';
import PTPAnalysis from './components/PTPAnalysis'
import Insight from './components/Insight'
import Portfolio from './components/Portfolio'



import "./Pages.css";

const ProtectedRoute = ({ element, isLoggedIn }) => {
  return isLoggedIn ? element : <Navigate to="/" replace />;
};

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(
    localStorage.getItem("isLoggedIn") === "true"
  );



  const handleLogout = () => {
    setIsLoggedIn(false);
    localStorage.removeItem("isLoggedIn"); // Clear login state
    localStorage.removeItem("token");
    sessionStorage.removeItem("user");
    console.log("User logged out due to inactivity");

    setTimeout(() => {
      window.location.href = "/"; // Ensure full redirect
    }, 100);
  };


  let inactivityTimeout;
  const resetInactivityTimeout = () => {
    clearTimeout(inactivityTimeout);
    inactivityTimeout = setTimeout(handleLogout, 1200000); // 20 minutes
  };

  useEffect(() => {
    if (isLoggedIn) {
      resetInactivityTimeout(); // Start timeout on login

      window.addEventListener("mousemove", resetInactivityTimeout);
      window.addEventListener("keydown", resetInactivityTimeout);
      window.addEventListener("scroll", resetInactivityTimeout);
      window.addEventListener("click", resetInactivityTimeout);
    }

    return () => {
      clearTimeout(inactivityTimeout);
      window.removeEventListener("mousemove", resetInactivityTimeout);
      window.removeEventListener("keydown", resetInactivityTimeout);
      window.removeEventListener("scroll", resetInactivityTimeout);
      window.removeEventListener("click", resetInactivityTimeout);
    };
  }, [isLoggedIn]);

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={isLoggedIn ? <Navigate to="/dashboard" replace /> : <Login onLogin={() => setIsLoggedIn(true)} />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password/:token" element={<ForgotPassword />} />
        <Route path="/verify" element={<VerifyPassword />} />
        <Route path="/VerifyOtpSignUp" element={<VerifyOtpSignUp />} />
        <Route path="/ResetPassword" element={<ResetPassword />} />

        {/* Protected Routes */}
        <Route path="/dashboard" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Dashboard onLogout={handleLogout} />} />} />
        <Route path="/Recordings" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Recordings onLogout={handleLogout} />} />} />
        <Route path="/Transcription" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Transcription onLogout={handleLogout}/>} />} />
        <Route path="/prompt" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Prompt onLogout={handleLogout} />} />} />
        <Route path="/Settings" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Settings onLogout={handleLogout}/>} />} />
        <Route path="/APIKey" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<APIKey onLogout={handleLogout}/>} />} />

        <Route path="/Analysis" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Analysis onLogout={handleLogout}/>} />} />
        <Route path="/Search" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Search onLogout={handleLogout}/>} />} />
        <Route path="/QualityPerformance" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<QualityPerformance onLogout={handleLogout}/>} />} />
        <Route path="/RawDump" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<RawDump onLogout={handleLogout}/>} />} />
        <Route path="/RawDownload" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<RawDownload onLogout={handleLogout}/>} />} />
        <Route path="/FatalAnalysis" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Fatal onLogout={handleLogout}/>} />} />
        <Route path="/DetailAnalysis" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Details onLogout={handleLogout}/>} />} />
        <Route path="/Potential" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Potential onLogout={handleLogout}/>} />} />

        <Route path="/Magical" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Magical onLogout={handleLogout}/>} />} />
        <Route path="/Sales" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Sales_dashboard onLogout={handleLogout}/>} />} />
        <Route path="/Opportunity" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Opportunity onLogout={handleLogout}/>} />} />
        <Route path="/Estimated" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Estimated onLogout={handleLogout}/>} />} />
        <Route path="/DetailSales" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<DetailSales onLogout={handleLogout}/>} />} />
        <Route path="/RawSales" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<RawSales onLogout={handleLogout}/>} />} />
        <Route path="/UserDashboardSelection" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<UserDashboardSelection onLogout={handleLogout}/>} />} />
        <Route path="/Calling" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Calling onLogout={handleLogout}/>} />} />

        <Route path="/PTPAnalysis" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<PTPAnalysis onLogout={handleLogout}/>} />} />
        <Route path="/Insight" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Insight onLogout={handleLogout}/>} />} />
        <Route path="/Portfolio" element={<ProtectedRoute isLoggedIn={isLoggedIn} element={<Portfolio onLogout={handleLogout}/>} />} />



        <Route path="/upload-help" element={<UploadHelp />} />
        <Route path="/api-help" element={<ApiHelp />} />
        
        {/* Catch-all route (redirect unknown paths to login) */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
