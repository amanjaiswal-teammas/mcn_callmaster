// src/pages/UploadHelp.jsx
import React from 'react';
import Layout from "../layout";
import "../layout.css";

const UploadHelp = () => {
    return (
        <Layout >
            <div style={{ padding: '20px', maxWidth: '700px', fontSize:"16px" }}>
                <h4>🎧 How to Upload an Audio File (Step-by-Step)</h4>

                <h5>✅ 1. Select Options</h5>
                <p>From the dropdowns at the top:</p>
                <ul>
                    <li>Choose the <strong>Language</strong> (e.g., English, Hindi, etc.).</li>
                    <li>Choose the <strong>Category</strong> (e.g., Sales, Service).</li>
                </ul>

                <h5>✅ 2. Upload Audio File</h5>
                <p>You have two ways to upload:</p>

                <h5>🔹 Option A: Drag & Drop</h5>
                <ul>
                    <li>Drag your <code>.mp3</code>, <code>.wav</code>, or other audio file from your computer.</li>
                    <li>Drop it on the cloud icon area labeled "Drag and Drop audio files here".</li>
                </ul>

                <h5>🔹 Option B: Click to Upload</h5>
                <ul>
                    <li>Click on the upload box (anywhere inside the border).</li>
                    <li>Select your audio file using the file picker, then click <strong>Open</strong>.</li>
                </ul>

                <h5>✅ 3. Wait for Upload</h5>
                <ul>
                    <li>Success message: “File uploaded successfully”.</li>
                    <li>If quota is reached: “<span style={{ color: 'red' }}>Limit exceeded! Upgrade your plan.</span>”</li>
                </ul>

                <h5>📝 Notes</h5>
                <ul>
                    <li>Supported formats: <code>.mp3</code>, <code>.wav</code>, etc.</li>
                    <li>If you see the "Limit exceeded" message, contact support or upgrade your plan.</li>
                </ul>
            </div>
        </Layout>
    );
};

export default UploadHelp;
