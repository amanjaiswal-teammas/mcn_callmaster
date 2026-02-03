import React, { useState, useEffect } from "react";
import Layout from "../layout";
import "../layout.css";
import "./APIKey.css";
import axios from "axios";
import { BASE_URL } from "./config";
import TooltipHelp from "./TooltipHelp";


const API_BASE_URL = process.env.REACT_APP_API_URL || `${BASE_URL}`;

export default function APIKey() {
  const [apiKeys, setApiKeys] = useState([]);
  const [generatedKey, setGeneratedKey] = useState("");
  const [uploadMessage, setUploadMessage] = useState("");
  const [copiedKey, setCopiedKey] = useState(null); // New state

  const userid = localStorage.getItem("id"); // Get user ID from local storage

  // Fetch keys from backend
  const fetchAPIKeys = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/get-keys`);
      if (response.data.length > 0) {
        const sortedKeys = response.data.sort(
          (a, b) => new Date(b.created_at) - new Date(a.created_at)
        );
        const latestActiveKey = sortedKeys.find((key) => key.status === "Active");

        const updatedKeys = sortedKeys.map((key) =>
          latestActiveKey && key.api_key === latestActiveKey.api_key
            ? key
            : { ...key, status: "Inactive" }
        );
        setApiKeys(updatedKeys);
      } else {
        setApiKeys([]);
      }
    } catch (error) {
      console.error("Error fetching API keys:", error);
    }
  };

  // Delete key via FastAPI
  const handleDelete = async (apiKey) => {
    const confirmDelete = window.confirm("Are you sure you want to delete this API key?");
    if (!confirmDelete) return;

    try {
      const response = await axios.post(`${API_BASE_URL}/delete-key/${apiKey}`);
      alert(response.data.message);
      fetchAPIKeys();
    } catch (error) {
      if (error.response) {
        alert(`Error: ${error.response.data.detail}`);
      } else {
        alert("An error occurred while deleting the key.");
      }
      console.error("Error deleting API key:", error);
    }
  };

  // Generate key for current user
  const handleGenerateKey = async () => {
    if (!userid) {
      setUploadMessage("User ID not found. Please log in.");
      return;
    }

    try {
      setUploadMessage("");
      const response = await axios.post(
        `${API_BASE_URL}/generate-key/`,
        { user_id: userid },
        { headers: { "Content-Type": "application/json" } }
      );

      setGeneratedKey(response.data.key);
      setUploadMessage("API key generated successfully!");

      setTimeout(() => {
        fetchAPIKeys();
      }, 500);
    } catch (error) {
      setUploadMessage("Failed to generate key.");
      console.error("Key generation failed:", error);
    }
  };

  useEffect(() => {
    fetchAPIKeys();
  }, [generatedKey]);

  return (
    <Layout heading="API Key Management">
      <h4>API Key Management</h4>
      <h6>Generate, view, and manage your secure API keys.</h6>

      {uploadMessage && <p>{uploadMessage}</p>}

      <div className="search-btn-contain">
        <div style={{ width: "430px" }}>
          <input
            type="text"
            placeholder="Generated key will appear here"
            value={generatedKey}
            readOnly
          />

        </div>
        <span style={{ marginLeft: "5px", marginTop: "8px" }}>
            <TooltipHelp message="You can generate a new API key using the Generate Key button" />
          </span>
        <button className="Generatekey-btn" onClick={handleGenerateKey} title=" Generate Key">
          
          Generate Key
        </button>
      </div>

      <div style={{ marginTop: "15px" }}>
        <table>
          <thead>
            <tr>
              <th>Key</th>
              <th>Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {apiKeys.length > 0 ? (
              apiKeys.map((key, index) => (
                <tr key={index}>
                  <td>{key.api_key}</td>
                  <td>{new Date(key.created_at).toLocaleString()}</td>
                  <td>{key.status}</td>
                  <td>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(key.api_key);
                        setCopiedKey(key.api_key);
                        setTimeout(() => setCopiedKey(null), 1500); // Reset after 1.5 sec
                      }}
                      style={{
                        marginLeft: "5px",
                        padding: "4px 8px",
                        cursor: "pointer",
                        width: "50px",
                        borderRadius: "10px",

                      }}
                      title="Copy key"
                    >

                      Copy
                    </button>

                    {copiedKey === key.api_key && (
                      <span style={{ marginLeft: "8px", color: "green", fontSize: "12px" }}>
                        Copied!
                      </span>
                    )}
                    <button
                      onClick={() => handleDelete(key.api_key)}
                      style={{
                        marginLeft: "5px",
                        padding: "4px 8px",
                        cursor: "pointer",
                        backgroundColor: "#979797",
                        color: "white",
                        width: "55px",
                        borderRadius: "10px",
                      }}
                      title="Delete key"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4">No API keys found</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}
