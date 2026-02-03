import React, { useState } from "react";
import Layout from "../layout";
import "../layout.css";
import "./Settings.css"

export default function Settings() {
  const [organizationName, setOrganizationName] = useState("");
  const [paymentInfo, setPaymentInfo] = useState("UPI");
  const [ratePerMin, setRatePerMin] = useState("");
  const [limit, setLimit] = useState("");

  const handleSave = () => {
    const settingsData = {
      organizationName,
      paymentInfo,
      ratePerMin,
      limit,
    };
    console.log("Saved Settings:", settingsData);
    alert("Settings saved successfully!");
  };

  return (
    <Layout heading="Title to be decided">
      <h4>Settings Center</h4>
      <h6>Manage organization and billing preferences</h6>
      <div className="settings-container">
        <div className="org-box">
          <label>Organization Name:</label>
          <input
            type="text"
            value={organizationName}
            onChange={(e) => setOrganizationName(e.target.value)}
            placeholder="e.g. MAS Callnet Pvt. Ltd."
          />

          <label>Payment Info:</label>
          <select value={paymentInfo} onChange={(e) => setPaymentInfo(e.target.value)}>
            <option value="UPI">UPI</option>
            <option value="Networking">NetBanking</option>
            <option value="Free">Free</option>
          </select>
        </div>
        <div className="org-box12">
          <label>Rate/Min:</label>
          <input
            className="box-label"
            type="number"
            value={ratePerMin}
            onChange={(e) => setRatePerMin(e.target.value)}
            placeholder="Enter rate per minute"
          />

          <label>Limit:</label>
          <input
            className="box-label2"
            type="number"
            value={limit}
            onChange={(e) => setLimit(e.target.value)}
            placeholder="eg. 1000 min"
          />
        </div>

        <button className="save-btn" onClick={handleSave}>Save</button>
      </div>
    </Layout>
  );
}
