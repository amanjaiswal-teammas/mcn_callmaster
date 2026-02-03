
import React from "react";
import ReactDOM from "react-dom/client"; // Use "react-dom/client" for React 18
import App from "./App";
import "bootstrap/dist/css/bootstrap.min.css"; // Import Bootstrap

const root = ReactDOM.createRoot(document.getElementById("root")); // Use createRoot
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
