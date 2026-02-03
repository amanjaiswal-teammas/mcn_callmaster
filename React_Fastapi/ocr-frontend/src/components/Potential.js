import React, { useState, useEffect } from "react";
import { PieChart, Pie, Cell, Legend, Tooltip } from "recharts";
import Layout from "../layout";
import "../layout.css";
import "./Potential.css";
import { BASE_URL } from "./config";

const Potential = () => {
  const [clientId] = useState(localStorage.getItem("client_id"));
  const [startDate, setStartDate] = useState(new Date().toISOString().split("T")[0]);
  const [endDate, setEndDate] = useState(new Date().toISOString().split("T")[0]);
  const [escalations, setEscalations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loading1, setLoading1] = useState(false);
  const [pieChartData, setPieChartData] = useState([]);
  const [error, setError] = useState(null);

  // Pagination State (1 item per page)
  const [currentPage, setCurrentPage] = useState(1);

  const fetchCallQualityDetails = async () => {
    if (!clientId || !startDate || !endDate) {
      alert("Please enter Client ID and select Start and End dates.");
      return;
    }

    setLoading1(true);

    try {
      const response = await fetch(
        `${BASE_URL}/potential_data_summarry?client_id=${clientId}&start_date=${startDate}&end_date=${endDate}`
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.status}`);
      }

      const result = await response.json();
      console.log("Fetched data:", result);

      if (result.raw_dump && result.raw_dump.length > 0) {
        setEscalations(result.raw_dump);

        const {
          social_media_threat = 0,
          consumer_court_threat = 0,
          potential_scam = 0,
          abuse = 0,
          threat = 0,
          frustration = 0,
          slang = 0,
          sarcasm = 0
        } = result.counts;


        const topNegativeSignals = social_media_threat + consumer_court_threat;
        const socialMediaThreats = potential_scam + abuse + threat + frustration + slang + sarcasm;


        setPieChartData([
          { name: "Top Negative Signals", value: topNegativeSignals, color: "#82c6fc" },
          { name: "Social Media and Consumer Court Threat", value: socialMediaThreats, color: "#d3388d" }
        ]);
      } else {
        setEscalations([]);
        alert("No escalation data found for selected criteria.");
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      alert("Error fetching data. Check the console for details.");
    } finally {
      setLoading1(false);
    }
  };

  // **Pagination Logic (1 item per page)**
  const totalPages = escalations.length;
  const currentEscalation = escalations[currentPage - 1];

  // **Pagination Handlers**
  const nextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  useEffect(() => {
    if (!clientId) return; // ✅ Prevents running effect if clientId is missing

    setLoading(true);
    setError(null);

    const fetchCallQualityDetails = async () => {
      try {
        const response = await fetch(
          `${BASE_URL}/potential_data_summarry?client_id=${clientId}`
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch data: ${response.status}`);
        }

        const result = await response.json();
        console.log("Fetched data:", result);

        if (result.raw_dump && result.raw_dump.length > 0) {
          setEscalations(result.raw_dump);

          const {
            social_media_threat = 0,
            consumer_court_threat = 0,
            potential_scam = 0,
            abuse = 0,
            threat = 0,
            frustration = 0,
            slang = 0,
            sarcasm = 0
          } = result.counts || {};

          const topNegativeSignals = social_media_threat + consumer_court_threat;
          const socialMediaThreats = potential_scam + abuse + threat + frustration + slang + sarcasm;

          setPieChartData([
            { name: "Top Negative Signals", value: topNegativeSignals, color: "#82c6fc" },
            { name: "Social Media and Consumer Court Threat", value: socialMediaThreats, color: "#d3388d" }
          ]);
        } else {
          setEscalations([]);
          console.warn("No escalation data found for selected criteria.");
        }
      } catch (error) {
        console.error("Error fetching data:", error);
        setError(`Error fetching data: ${error.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchCallQualityDetails();
  }, [clientId]);

  if (loading) {
    return (
      <div className="zigzag-container">
        <div className="bar"></div>
        <div className="bar"></div>
        <div className="bar"></div>
        <div className="bar"></div>
        <div className="bar"></div>
      </div>
    );
  }

  return (
    <Layout heading="Title to be decided">
      <div className={`dashboard-container-po ${loading ? "blurred" : ""}`}>
        <header className="headerPo">
          <h3>DialDesk</h3>
          <div className="setheaderdivdetails">
            <label>
              <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
            </label>
            <label>
              <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
            </label>
            <input className="setsubmitbtn" type="button" value="Submit" onClick={fetchCallQualityDetails} />
          </div>
        </header>

        <div className="content">
          <div className="chart-container-po">
            <h3 className="Po-text">Recent Escalation</h3>
            <PieChart width={250} height={350}>
              <Pie data={pieChartData} dataKey="value" outerRadius={80} label>
                {pieChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend
                wrapperStyle={{
                  position: "absolute",
                  width: "210px",
                  left: "215px",
                  bottom: "115px",
                  fontSize: "13px",
                }}
              />
            </PieChart>

            {/* 🔹 Single Escalation Per Page */}
            <div className="scrollable-list">
              <h3 className="Po-text">Recent Escalations</h3>
              {escalations.length > 0 ? (
                <div className="escalation-list">
                  {escalations.map((item, index) => (
                    <div key={index} className="escalations-items">
                      <p>
                        <p><strong style={{ fontSize: "14px" }}>Call Date:</strong> {item.CallDate ? item.CallDate.split("T")[0] : "N/A"}</p>
                      </p>
                      <p>
                        <strong>Lead ID:</strong> {item.lead_id || "N/A"}
                      </p>
                      <p>
                        <strong>Campaign:</strong> {item.Campaign || "N/A"}
                      </p>
                      <p>
                        <strong>Negative Words:</strong>{" "}
                        {item.top_negative_words || "N/A"}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No escalations found.</p>
              )}
            </div>
          </div>

          {/* 🔹 Single Escalation Per Page - Table Format */}
          <div className="table-container">
            <h3 className="Po-text">Potential Escalation - Sensitive Cases</h3>
            {currentEscalation ? (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Category</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(currentEscalation).map(([key, value], index) => (
                      <tr key={`${currentPage}-${index}`}>
                        <td className="fields">{key.replace(/_/g, " ")}</td>
                        <td className="values">{value !== null ? String(value) : "N/A"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {/* Pagination Controls */}
                <div className="pagination-controls">
                  <button className="paging_btn" onClick={prevPage} disabled={currentPage === 1}>Previous</button>
                  <span> Page {currentPage} - {totalPages} </span>
                  <button className="paging_btn" onClick={nextPage} disabled={currentPage === totalPages}>Next</button>
                </div>
              </div>
            ) : (
              <p>No data available.</p>
            )}


          </div>
        </div>

        {loading1 && (
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

export default Potential;
