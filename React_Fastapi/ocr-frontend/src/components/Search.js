import React, { useState } from "react";
import Layout from "../layout"; // Import layout component
import "../layout.css"; // Import styles
import "./Search.css";
import { BASE_URL } from "./config";
const Search = () => {
  const [leadId, setLeadId] = useState(""); // Input field state
  const [data, setData] = useState(null); // Store API response
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const client_id = localStorage.getItem("client_id");

  // Fetch call quality details from API
  const fetchCallQualityDetails = async () => {
    if (!leadId) {
      alert("Please enter a Lead ID.");
      return;
    }

    setLoading(true);
    setError(null);

    try {

      const response = await fetch(
        `${BASE_URL}/call_quality_details/?client_id=${client_id}&lead_id=${leadId}`
      );
      if (!response.ok) throw new Error("Failed to fetch call quality details");

      const apiData = await response.json();

      // Format API response to match UI requirements
      const formattedData = {
        "Call Date": apiData.call_date,
        "Lead ID": apiData.lead_id,
        "Agent Name": apiData.user,
        "Competitor Name": apiData.competitor_name || "",
        "Customer Concern Acknowledged": apiData.customer_concern_acknowledged ? "true" : "false",
        "Professionalism Maintained": apiData.professionalism_maintained ? "true" : "false",
        "Assurance Or Appreciation Provided": apiData.assurance_or_appreciation_provided ? "true" : "false",
        "Express Empathy": apiData.express_empathy ? "true" : "false",
        "Pronunciation And Clarity": apiData.pronunciation_and_clarity ? "true" : "false",
        "Enthusiasm And No Fumbling": apiData.enthusiasm_and_no_fumbling ? "true" : "false",
        "Active Listening": apiData.active_listening ? "true" : "false",
        "Politeness And No Sarcasm": apiData.politeness_and_no_sarcasm ? "true" : "false",
        "Proper Grammar": apiData.proper_grammar ? "true" : "false",
        "Accurate Issue Probing": apiData.accurate_issue_probing ? "true" : "false",
        "Proper Hold Procedure": apiData.proper_hold_procedure ? "true" : "false",
        "Proper Transfer And Language": apiData.proper_transfer_and_language ? "true" : "false",
        "Address Recorded Completely": apiData.address_recorded_completely ? "true" : "false",
        "Correct And Complete Information": apiData.correct_and_complete_information ? "true" : "false",
        "Proper Call Closure": apiData.proper_call_closure ? "true" : "false",
        "Sensitive Word Used": apiData.sensitive_word_used || "None",
        "Quality Percentage": `${apiData.quality_percentage}%`,
        "Areas for Improvement": apiData.areas_for_improvement || "None",
      };

      setData(formattedData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Show loading message until all data is fetched
  // if (loading) {
  //   return (
  //     <div className="loader-container">
  //       <div className="windows-spinner"></div>
  //       <p className="Loading">Loading...</p>
  //     </div>
  //   );
  // }

  return (
    <Layout heading="Title to be decided">
      {/* <div className="containers"> */}
      <div className={`containers ${loading ? "blurred" : ""}`}>
        {/* Header Section */}
        <header className="header">
          <h3>DialDesk</h3>

          <div className="search-container-se">
            <input
              type="text"
              className="search-bar"
              placeholder="Search Lead Id..."
              value={leadId}
              onChange={(e) => {
                const value = e.target.value;
                if (/^\d*$/.test(value)) {
                  setLeadId(value); // Only update state if value is an integer
                }
              }}
            />
            <button class="setsubmitbtn1" onClick={fetchCallQualityDetails}>
              Search
            </button>
          </div>
        </header>

        {/* Table Section */}
        <div className="tables-container">
          {/* {loading && <p>Loading...</p>} */}
          {error && <p style={{ color: "red" }}>{error}</p>}

          {data && (
            <table>
              <tbody>
                {Object.entries(data).map(([key, value]) => (
                  <tr key={key}>
                    <td className="field">{key}</td>
                    <td className="value">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        {loading && (
          <div className="loader-overlay">
            <div className="bar"></div>
            <div className="bar"></div>
            <div className="bar"></div>
            <div className="bar"></div>
            <div className="bar"></div>

          </div>
        )}
      </div>
    </Layout>
  );
};

export default Search;
