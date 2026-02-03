// APIDocumentation.js
import React from 'react';
import ReactMarkdown from 'react-markdown';
import Layout from "../layout";
import "../layout.css";

const markdown = `
## 📘 Welcome to Your API Documentation

This guide will help you get started with using our API, understanding authentication, endpoints, rate limits, and how to integrate it into your system with examples.

---

## 🚀 What Can You Do with the API?

With our API, you can:

- Upload audio files (MP3/WAV)
- Record voice notes directly in the browser
- Manage and categorize audio by language and category
- Track your usage and limits
- Get file lists and usage history

---

## 🔐 Authentication

All requests require an API key for authentication.

### 🔑 Get Your API Key

You’ll receive an API key after signing up. Keep this key **secure**.

---

## 📦 Usage

Include your API key in the request headers:

\`\`\`http
Authorization: Bearer YOUR_API_KEY
\`\`\`

---

## 📌 Endpoints Overview

### 1. Upload Audio

\`\`\`http
POST /api/audio/upload
\`\`\`

**Headers:**
\`\`\`http
Authorization: Bearer YOUR_API_KEY  
Content-Type: multipart/form-data
\`\`\`

**Body Parameters:**

| Field    | Type   | Required | Description                 |
|----------|--------|----------|-----------------------------|
| file     | File   | ✅       | Audio file (.mp3, .wav)     |
| language | String | ✅       | Language code (e.g., "en")  |
| category | String | ✅       | Tag for file (e.g., "news") |

**Example (cURL):**
\`\`\`bash
curl -X POST https://yourapi.com/api/audio/upload \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -F "file=@/path/audio.mp3" \\
  -F "language=en" \\
  -F "category=interview"
\`\`\`

---

### 2. Get Uploaded Files

\`\`\`http
GET /api/audio/files
\`\`\`

Returns: A list of uploaded audio files with metadata.

---

### 3. Get Usage Info

\`\`\`http
GET /api/usage
\`\`\`

**Returns:**
\`\`\`json
{
  "uploads_this_month": 10,
  "monthly_quota": 50,
  "quota_remaining": 40
}
\`\`\`





---



## 💡 Pro Tips

- ✅ Always check your quota before uploading  
- ✅ Use appropriate tags for language/category  
- ✅ Contact support for bulk upload or enterprise access
`;

const ApiHelp = () => {
    return (
        <Layout>
            <div className="markdown-docs">
                <ReactMarkdown children={markdown} />
            </div>
        </Layout>
    );
};

export default ApiHelp;
