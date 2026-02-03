import React, { useState,useEffect } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar, ResponsiveContainer,
} from 'recharts';
import "./Portfolio.css";
import Layout from "../layout";
import "../layout.css";
import { BASE_URL } from "./config";
import axios from "axios";

const Portfolio = () => {
 const [startDate, setStartDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [endDate, setEndDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [data, setData] = useState(null);
  const [ptpData, setPtpData] = useState([]);
  const [ptpByAgent, setPtpByAgent] = useState([]);
  const [customerData, setCustomerData] = useState([]);


  const formatValue = (val) => (val != null ? val : "-");


const sectionStyle = {
  backgroundColor: "#f9fafb",
  padding: "10px",
  borderRadius: "8px",
};





const fetchPtpData = async () => {
  try {
    const summaryRes = await axios.post(`${BASE_URL}/dashboard3/ptp-summary-stats`, {
      start_date: startDate,
      end_date: endDate,
      agent_name: "string",
      team: "string",
      region: "string",
      campaign: "string",
      min_confidence_score: 0,
      disposition: "string"
    });
    setData(summaryRes.data);
  } catch (error) {
    console.error("Failed to fetch PTP summary stats:", error);
  }


try {
      const trendsRes = await axios.post(`${BASE_URL}/dashboard3/ptp-rtp-monthly-trends`, {
        start_date: startDate,
        end_date: endDate,
        agent_name: "string",
        team: "string",
        region: "string",
        campaign: "string",
        min_confidence_score: 0,
        disposition: "string"
      });
      setPtpData(trendsRes.data || []);
    } catch (error) {
      console.error("Failed to fetch monthly trends:", error);
    }

    try {
      const response = await fetch(`${BASE_URL}/dashboard3/ptp-by-agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_date: startDate,
          end_date: endDate,
          agent_name: 'string',
          team: 'string',
          region: 'string',
          campaign: 'string',
          min_confidence_score: 0,
          disposition: 'string'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const ptpByAgentData = data.agents.map((name, i) => ({
        name,
        ptp: data.ptp_amounts[i] || 0
      }));

      setPtpByAgent(ptpByAgentData);
    } catch (error) {
      console.error("Failed to fetch PTP by agent:", error);
    }



    try {
    const response = await axios.post(`${BASE_URL}/dashboard3/ptp-fulfillment-table`, {
      start_date: startDate,
      end_date: endDate,
      agent_name: "string",
      team: "string",
      region: "string",
      campaign: "string",
      min_confidence_score: 0,
      disposition: "string"
    });

    const apiData = response.data?.data || [];

    const formattedData = apiData.map((item, index) => ({
      id: item.customer_id || `C${index}`,
      agent: item.agent || "Unknown",
      date: item.call_date || "-",
      amount: item.promised_amount ? `$${item.promised_amount.toLocaleString()}` : "-",
      status: item.status || "-"
    }));

    setCustomerData(formattedData);
  } catch (error) {
    console.error("Failed to fetch customer data:", error);
  }

};


useEffect(() => {
    const fetchPTPSummaryStats = async () => {
      try {
        const response = await axios.post(
          `${BASE_URL}/dashboard3/ptp-summary-stats`,
          {
            start_date: startDate,
            end_date: endDate,
            agent_name: "string",
            team: "string",
            region: "string",
            campaign: "string",
            min_confidence_score: 0,
            disposition: "string"
          }
        );
        setData(response.data);
      } catch (error) {
        console.error("Failed to fetch PTP summary stats:", error);
      }
    };

    fetchPTPSummaryStats();
  }, []);

  return (
  <Layout heading="Title to be decided">
    <div className="dashboard">
      <h1>Collection Calls Portfolio Analysis</h1>

      <div
          style={{
            display: "flex",
            gap: "35px",
            marginBottom: "20px",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", gap: "30px" }}>
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

          <select style={sectionStyle}>
            <option>Agent</option>
          </select>
          <select style={sectionStyle}>
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
            onClick={fetchPtpData }
          >
            Apply Filters
          </button>
        </div>

      <div className="cards">
        <Card title="Total Calls" value={formatValue(data?.total_calls)} />
        <Card title="PTP Fulfillment %" value={formatValue(data?.ptp_count)} />
        <Card title="PTP Amount" value={formatValue(data?.ptp_amount)} />
        <Card title="Total RTP" value={formatValue(data?.rtp_count)} />
        <Card title="RTP Amount" value={formatValue(data?.rtp_amount)} />
      </div>


      <div className="charts">
        <div className="chart-box">
          <h2>PTP and RTP Trends</h2>
          {ptpData.length === 0 || ptpData.every(d => d.PTP === 0 && d.RTP === 0) ? (
            <div style={{ textAlign: "center", padding: "20px", color: "#888" }}>
              No data available
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={ptpData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="PTP" stroke="#007bff" />
                <Line type="monotone" dataKey="RTP" stroke="#28a745" />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>


        <div className="chart-box">
              <h2>PTP by Agent</h2>
              {ptpByAgent.length === 0 || ptpByAgent.every(d => d.ptp === 0) ? (
                <div style={{ textAlign: "center", padding: "20px", color: "#888" }}>
                  No data available
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={ptpByAgent} layout="vertical">
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" />
                    <Tooltip />
                    <Bar dataKey="ptp" fill="#007bff" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

      </div>

      <div className="table-section">
      <h2>Customer Data</h2>
      <table>
        <thead>
          <tr>
            <th>Customer ID</th>
            <th>Agent</th>
            <th>Call Date</th>
            <th>Promised Amount</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {customerData.length === 0 ? (
            <tr>
              <td colSpan="5" style={{ textAlign: "center", padding: "20px", color: "#888" }}>
                No data available
              </td>
            </tr>
          ) : (
            customerData.map((row) => (
              <tr key={row.id + row.call_date}> {/* Ensure unique key */}
                <td>{row.id || "-"}</td>
                <td>{row.agent}</td>
                <td>{row.date}</td>
                <td>{row.amount}</td>
                <td>
                  <span className={`status ${row.status.toLowerCase()}`}>
                    {row.status}
                  </span>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>

    </div>
    </Layout>
  );
};

const Card = ({ title, value }) => {
  let backgroundColor = "rgb(251, 140, 0)";

  if (title === "Total Calls") {
    backgroundColor = "rgb(67, 160, 71)";
  }
  if (title === "PTP Fulfillment %") {
    backgroundColor = "rgb(229, 57, 53)";
  }
  if (title ==="RTP Amount")
  {
    backgroundColor="rgb(30, 136, 229)";
  }
  if (title === "PTP Amount")
  {
    backgroundColor="#504ad1";
  }

  return (
    <div className="card" style={{ backgroundColor }}>
      <p className="card-title" style={{ color: "black" }}>{title}</p>
      <p className="card-value">{value}</p>
    </div>
  );
};


export default Portfolio;

