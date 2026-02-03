import React, { useState,useEffect } from "react";
import Layout from "../layout";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import axios from "axios";
import { BASE_URL } from "./config";

const PTPAnalysis = () => {
  const [startDate, setStartDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [endDate, setEndDate] = useState(
    new Date().toISOString().split("T")[0]
  );

  const [summary, setSummary] = useState(null);

   const [barData, setBarData] = useState([
    { confidence: "0-25", count: 0 },
    { confidence: "26-50", count: 0 },
    { confidence: "51-75", count: 0 },
    { confidence: "76-100", count: 0 },
  ]);

  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split("T")[0];
  }


  const [pieData, setPieData] = useState([
  { name: "hesitations", value: 0 },
  { name: "confidents", value: 0 },
]);

const [insightData, setInsightData] = useState([]);
const [agentAccuracyData, setAgentAccuracyData] = useState([]);
const [loading1, setLoading1] = useState(false);


  const containerStyle = {
    backgroundColor: "#0f1b2b",
    color: "white",
    minHeight: "100vh",
    padding: "24px",
    fontFamily: "sans-serif",
  };

  const cardStyle = (bgColor) => ({
    backgroundColor: bgColor,
    padding: "16px",
    borderRadius: "8px",
    textAlign: "center",
  });

  const sectionStyle = {
    backgroundColor: "rgb(31, 41, 55)",
    padding: "16px",
    borderRadius: "8px",
    color: "white",
  };

  const sectionStylenew = {
    backgroundColor: "#f9fafb",
    padding: "16px",
    borderRadius: "8px",
    color: "black",
  };

  const sectionStylestyle = {
    backgroundColor: "rgb(31, 41, 55)",
    padding: "16px",
    borderRadius: "8px",
    color: "white",
    height: "350px",
    overflowX: "auto",
  };

  const tableStyle = {
    width: "100%",
    borderCollapse: "collapse",
    color: "#1d2024",
    fontSize: "14px",
  };

  const thTdStyle = {
    borderBottom: "1px solid #374151",
    padding: "5px",
    textAlign: "left",
  };



  const barColors = ["#f87171", "#fbbf24", "#34d399", "#60a5fa"];



  const pieColors = ["#34d399", "#facc15", "#f87171"];




  useEffect(() => {
const today = new Date().toISOString().split("T")[0];

  const fetchSummary = async () => {
    try {
      const res = await axios.post(`${BASE_URL}/dashboard3/summary`, {
        start_date: today,
        end_date: today,
        agent_name: "string",
        team: "string",
        region: "string",
        campaign: "string",
        min_confidence_score: 0,
        disposition: "string"
      });
      setSummary(res.data);
    } catch (err) {
      console.error("API fetch error:", err);
    }
  };

  const fetchDistribution = async () => {
    try {
      const response = await axios.post(
        `${BASE_URL}/dashboard3/ptp-distribution`,
        {
          start_date: today,
          end_date: today,
          agent_name: null,
          team: null,
          region: null,
          campaign: null,
          min_confidence_score: null,
          disposition: null,
        }
      );

      const rawData = response.data;

      const countMap = {
        "0-25": 0,
        "26-50": 0,
        "51-75": 0,
        "76-100": 0,
      };

      rawData.forEach((item) => {
        const label = item.range_label;
        const value = parseInt(label.split("-")[0]);

        if (value <= 25) countMap["0-25"] += item.count;
        else if (value <= 50) countMap["26-50"] += item.count;
        else if (value <= 75) countMap["51-75"] += item.count;
        else countMap["76-100"] += item.count;
      });

      const finalData = Object.entries(countMap).map(([key, value]) => ({
        confidence: key,
        count: value,
      }));

      setBarData(finalData);
    } catch (err) {
      console.error("Error fetching distribution:", err);
    }



  };

  fetchSummary();
  fetchDistribution();
}, [startDate, endDate]);






const fetchDistribution = async () => {
setLoading1(true);
  try {
    // Common request body
    const payload = {
      start_date: startDate,
      end_date: endDate,
      agent_name: null,
      team: null,
      region: null,
      campaign: null,
      min_confidence_score: null,
      disposition: null,
    };

    // 1. Fetch bar chart (distribution)
    const distributionResponse = await axios.post(
      `${BASE_URL}/dashboard3/ptp-distribution`,
      payload
    );

    const rawData = distributionResponse.data;

    const countMap = {
      "0-25": 0,
      "26-50": 0,
      "51-75": 0,
      "76-100": 0,
    };

    rawData.forEach((item) => {
      const label = item.range_label;
      const value = parseInt(label.split("-")[0]);

      if (value <= 25) countMap["0-25"] += item.count;
      else if (value <= 50) countMap["26-50"] += item.count;
      else if (value <= 75) countMap["51-75"] += item.count;
      else countMap["76-100"] += item.count;
    });

    const finalDistributionData = Object.entries(countMap).map(
      ([key, value]) => ({
        confidence: key,
        count: value,
      })
    );

    setBarData(finalDistributionData);

    // 2. Fetch pie chart data
    const pieResponse = await axios.post(
      `${BASE_URL}/dashboard3/sentiment-pie-distribution`,
      payload
    );

    const pieDataRaw = pieResponse.data;

    let hesitationsCount = 0;
    let confidentsCount = 0;

    pieDataRaw.forEach((item) => {
      if (item.category.toLowerCase() === "confident") {
        confidentsCount += item.count;
      } else if (item.category.toLowerCase() === "hesitation") {
        hesitationsCount += item.count;
      }
    });

    setPieData([
      { name: "hesitations", value: hesitationsCount },
      { name: "confidents", value: confidentsCount },
    ]);

    // 3. Fetch insights table data
    const insightsResponse = await axios.post(
      `${BASE_URL}/dashboard3/ptp-insights-detailed`,
      payload
    );

    setInsightData(insightsResponse.data);

    // 4. Fetch agent-wise accuracy table data
    const accuracyResponse = await axios.post(
      `${BASE_URL}/dashboard3/agent-wise-accuracy`,
      payload
    );

    setAgentAccuracyData(accuracyResponse.data);

  } catch (error) {
    console.error("Error fetching data:", error);

    // Set fallback values
    setBarData([
      { confidence: "0-25", count: 0 },
      { confidence: "26-50", count: 0 },
      { confidence: "51-75", count: 0 },
      { confidence: "76-100", count: 0 },
    ]);

    setPieData([
      { name: "hesitations", value: 0 },
      { name: "confidents", value: 0 },
    ]);

    setInsightData([]);
    setAgentAccuracyData([]);
  }
  try {
      const res = await axios.post(`${BASE_URL}/dashboard3/summary`, {
        start_date: startDate,
        end_date: endDate,
        agent_name: "string",
        team: "string",
        region: "string",
        campaign: "string",
        min_confidence_score: 0,
        disposition: "string"
      });
      setSummary(res.data);
    } catch (err) {
      console.error("API fetch error:", err);
    }

  finally {
      setLoading1(false);
    }
};




  return (
    <Layout>
    <div className={` ${loading1 ? "blurred" : ""}`}>
      <div style={containerStyle}>
        <h2
          style={{ fontSize: "20px", fontWeight: "bold", marginBottom: "16px" }}
        >
          PTP Analysis Dashboard
        </h2>

        {/* Filters */}
        {/* <div style={{ display: "flex", gap: "12px", marginBottom: "20px" }}>
          <select style={sectionStyle}>
            <option>Date Range</option>
          </select>
          <select style={sectionStyle}>
            <option>Agent</option>
          </select>
          <select style={sectionStyle}>
            <option>Region</option>
          </select>
          <select style={sectionStyle}>
            <option>Confidence Score</option>
          </select>
          <button
            style={{
              backgroundColor: "#fbbf24",
              color: "black",
              fontWeight: "600",
              padding: "10px",
              borderRadius: "8px",
              border: "none",
            }}
          >
            Apply Filters
          </button>
        </div> */}
        <div
          style={{
            display: "flex",
            gap: "12px",
            marginBottom: "20px",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", gap: "8px" }}>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              style={{
                padding: "10px",
                borderRadius: "8px",
                border: "1px solid #ccc",
                backgroundColor: "#f9fafb",
                fontWeight: "500",
              }}
            />
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              style={{
                padding: "10px",
                borderRadius: "8px",
                border: "1px solid #ccc",
                backgroundColor: "#f9fafb",
                fontWeight: "500",
              }}
            />
          </div>

          <select style={sectionStylenew}>
            <option>Agent</option>
          </select>
          <select style={sectionStylenew}>
            <option>Region</option>
          </select>

          <button
            style={{
              backgroundColor: "#fbbf24",
              color: "black",
              fontWeight: "600",
              padding: "10px",
              borderRadius: "8px",
              border: "none",
            }}
            onClick={fetchDistribution}
          >
            Apply Filters
          </button>
        </div>

        {/* Stats */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: "16px",
            marginBottom: "20px",
          }}
        >
          <div style={cardStyle("#1e88e5")}>
            <div style={{ fontSize: "24px", fontWeight: "bold" }}>{summary?.total_ptps ?? 0}</div>
            <div>Total PTPs Collected</div>
          </div>
          <div style={cardStyle("#e53935")}>
            <div style={{ fontSize: "24px", fontWeight: "bold" }}>{summary?.low_confidence ?? 0}</div>
            <div>
              High-Risk PTPs
              <br />
              (Low Confidence)
            </div>
          </div>
          <div style={cardStyle("#43a047")}>
            <div style={{ fontSize: "24px", fontWeight: "bold" }}>{summary?.high_confidence ?? 0}</div>
            <div>
              Genuine PTPs
              <br />
              (High Confidence)
            </div>
          </div>
          <div style={cardStyle("#fb8c00")}>
            <div style={{ fontSize: "24px", fontWeight: "bold" }}>{summary?.follow_up_cases ?? 0}</div>
            <div>
              Follow-Up Call
              <br />
              Priority Cases
            </div>
          </div>
        </div>

        {/* Charts */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(2, 1fr)",
            gap: "16px",
            marginBottom: "20px",
          }}
        >
          <div style={sectionStyle}>
            <div style={{ fontWeight: "600", marginBottom: "8px" }}>
              PTP Confidence Distribution
            </div>
            <div
  style={{
    height: "265px",
    backgroundColor: "#374151",
    borderRadius: "6px",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  }}
>
  {barData.length === 0 || barData.every((item) => item.count === 0) ? (
    <div style={{ color: "white", fontSize: "16px" }}>No data available</div>
  ) : (
    <BarChart width={350} height={200} data={barData}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="confidence" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="count">
        {barData.map((entry, index) => (
          <Cell
            key={`cell-${index}`}
            fill={barColors[index % barColors.length]}
          />
        ))}
      </Bar>
    </BarChart>
  )}
</div>

          </div>
          <div style={sectionStyle}>
            <div style={{ fontWeight: "600", marginBottom: "8px" }}>
              Sentiment & Language Insights
            </div>
            <div
  style={{
    height: "265px",
    backgroundColor: "#374151",
    borderRadius: "6px",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  }}
>
  {pieData.length === 0 || pieData.every((item) => item.value === 0) ? (
    <div style={{ color: "white", fontSize: "16px" }}>No data available</div>
  ) : (
    <PieChart width={350} height={262}>
      <Pie
        data={pieData}
        cx="50%"
        cy="50%"
        labelLine={false}
        outerRadius={70}
        fill="#8884d8"
        dataKey="value"
        label
      >
        {pieData.map((entry, index) => (
          <Cell
            key={`cell-${index}`}
            fill={pieColors[index % pieColors.length]}
          />
        ))}
      </Pie>
      <Legend />
    </PieChart>
  )}
</div>

          </div>
        </div>

        {/* Tables */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(2, 1fr)",
            gap: "16px",
          }}
        >
          <div style={sectionStylestyle}>
            <div style={{ fontWeight: "600", marginBottom: "8px" }}>
              Detailed AI-Powered PTP Insights
            </div>
            <table style={tableStyle}>
              <thead>
                <tr>
                  <th style={thTdStyle}>Date</th>
                  <th style={thTdStyle}>Agent</th>
                  <th style={thTdStyle}>Customer Name</th>
                  <th style={thTdStyle}>Sentiment</th>
                  <th style={thTdStyle}>Confidence</th>
                </tr>
              </thead>
              <tbody>
                  {insightData.length > 0 ? (
                    insightData.map((item, index) => (
                      <tr key={index}>
                        <td style={thTdStyle}>{item.date}</td>
                        <td style={thTdStyle}>{item.agent}</td>
                        <td style={thTdStyle}>{item.customer_name}</td>
                        <td style={thTdStyle}>{item.sentiment}</td>
                        <td style={thTdStyle}>{item.confidence}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" style={thTdStyle}>No data available</td>
                    </tr>
                  )}
                </tbody>
            </table>
          </div>

          {/* Agent-Wise PTP Accuracy Table */}
          <div style={sectionStylestyle}>
            <div style={{ fontWeight: "600", marginBottom: "8px" }}>
              Agent-Wise PTP Accuracy
            </div>
            <table style={tableStyle}>
              <thead>
                <tr>
                  <th style={thTdStyle}>Agent</th>
                  <th style={thTdStyle}>Total PTPs</th>
                  <th style={thTdStyle}>Avg Confidence</th>
                  <th style={thTdStyle}>Failed PTPs</th>
                  <th style={thTdStyle}>accuracy Pct</th>
                </tr>
              </thead>
              <tbody>
                {agentAccuracyData.length > 0 ? (
                  agentAccuracyData.map((item, index) => (
                    <tr key={index}>
                      <td style={thTdStyle}>{item.agent}</td>
                      <td style={thTdStyle}>{item.total_ptps}</td>
                      <td style={thTdStyle}>{item.avg_confidence}%</td>
                      <td style={thTdStyle}>{item.failed_ptps}</td>
                      <td style={thTdStyle}>{item.accuracy_pct}%</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td style={thTdStyle} colSpan="5" align="center">
                      No data available
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
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

export default PTPAnalysis;
