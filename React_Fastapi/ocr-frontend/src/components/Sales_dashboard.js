import React, { useState, useEffect } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from "recharts";
import { FunnelChart, Funnel, LabelList } from "recharts";
import "./SalesDashboard.css"; // Import CSS
import Layout from "../layout";
import "../layout.css";
import { BASE_URL } from "./config";

export default function SalesDashboard() {
  //loading code start===>
  const [loading, setLoading] = useState(true);
  const [loading1, setLoading1] = useState(false);
  const [startDate, setStartDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [endDate, setEndDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [callSummary, setCallSummary] = useState({});
  const [rejectedData, setRejectedData] = useState([]);

  useEffect(() => {
    setTimeout(() => {
      setLoading(false);
    }, 2000);
  }, []);

  const fetchSalesData = async () => {

    setLoading1(true);
    try {
      const clientId = localStorage.getItem("client_id");
      const [summaryResponse, rejectedResponse] = await Promise.all([
        fetch(
          `${BASE_URL}/call_summary_sales?client_id=${clientId}&start_date=${startDate}&end_date=${endDate}`
        ),
        fetch(
          `${BASE_URL}/call_category_counts_sales?client_id=${clientId}&start_date=${startDate}&end_date=${endDate}`
        ),
      ]);

      if (!summaryResponse.ok || !rejectedResponse.ok) {
        throw new Error("Failed to fetch data");
      }

      const summaryResult = await summaryResponse.json();
      setCallSummary(summaryResult.call_summary);

      const rejectedResult = await rejectedResponse.json();
      setRejectedData([
        {
          name: "Opening Rejected",
          value: rejectedResult["Opening Rejected"] ?? 0,
          color: "#4CAF50",
        },
        {
          name: "Offering Rejected",
          value: rejectedResult["Offering Rejected"] ?? 0,
          color: "#FF5722",
        },
        {
          name: "Context Rejected",
          value: rejectedResult["Context Rejected"] ?? 0,
          color: "#FFC107",
        },
        {
          name: "Post Offer Rejected",
          value: rejectedResult["Post Offer Rejected"] ?? 0,
          color: "#2196F3",
        },
      ]);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading1(false);
    }
  };

  const cstFunnelData = [
    {
      name: "Total Calls",
      value: callSummary.total_calls ?? 0,
      color: "#4682B4",
    },
    {
      name: "Opening Pitched",
      value: callSummary.exclude_opening_rejected ?? 0,
      color: "#CD5C5C",
    },
    {
      name: "Context Pitched",
      value: callSummary.exclude_context_opening_offering_rejected ?? 0,
      color: "#3CB371",
    },
    {
      name: "Offer Pitched",
      value: callSummary?.exclude_context_opening_rejected ?? 0,
      color: "rgb(111 101 49)",
    },
    {
      name: "Sale Made",
      value: callSummary.sale_done_count ?? 0,

      color: "rgb(126 101 149)",
    },
  ];

  const crtFunnelData = [
    {
      name: "Opening Rejected",
      value: callSummary.include_opening_rejected ?? 0,
      color: "#4682B4",
    },
    {
      name: "Context Rejected",
      value: callSummary.include_context_rejected ?? 0,
      color: "#CD5C5C",
    },
    {
      name: "Offering Rejected",
      value: callSummary.offering_rejected_count ?? 0,
      color: "#3CB371",
    },
    {
      name: "POD",
      value: callSummary.post_offer_rejected_count ?? 0,
      color: "rgb(111 101 49)",
    },
  ];

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
  //loading code end==>
  return (
    <Layout heading="Title to be decided">
      <div className={`dashboard-container ${loading ? "blurred" : ""}`}>
        <div className="dashboard-container">
          <div className="header">
            <h5>AI-Enhanced Sales Strategy Dashboard</h5>
            <div className="salesheader">
              <label>
                <input
                  type="date"
                  name="start_date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  required
                />
              </label>
              <label>
                <input
                  type="date"
                  name="end_date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  required
                />
              </label>
              <label>
                <input
                  type="submit"
                  class="setsubmitbtn"
                  value="Submit"
                  onClick={fetchSalesData}
                />
              </label>
            </div>
          </div>

          {/* 1️⃣ Key Metrics */}
          <div className="metric-container">
            {/* CST Card */}
            <div className="metric-card green-met">
              <h3 style={{ fontSize: "16px" }}>
                CST</h3>
              <div className="metrics">
                <div style={{marginTop:"10px"}}>
                  <b>{callSummary?.total_calls ?? 0}</b>
                  <p>Total Calls</p>
                </div>
                <div style={{marginTop:"10px"}}>
                  <b>{callSummary?.exclude_opening_rejected ?? 0}</b>
                  <p>OPS</p>
                </div>
                <div style={{marginTop:"10px"}}>
                  <b>{callSummary?.exclude_context_opening_rejected ?? 0}</b>
                  <p>cps</p>
                </div>
                <div style={{marginTop:"10px"}}>
                  <b>
                    {callSummary?.exclude_context_opening_offering_rejected ?? 0}
                  </b>
                  <p>Offer Success</p>
                </div>
                <div style={{marginTop:"10px"}}>
                  <b>{callSummary?.sale_done_count ?? 0}</b>
                  <p>Sale Done</p>
                </div>
                <div style={{marginTop:"10px"}}>
                  <b>{callSummary?.sale_success_rate ?? 0}%</b>
                  <p>Success Rate</p>
                </div>
              </div>
            </div>

            {/* CRT Card */}
            <div className="metric-card blue-met">
              <h3 style={{ fontSize: "16px" }}>CRT</h3>
              <div className="metrics">
                <div style={{marginTop:"10px"}}>
                  <b>{callSummary?.include_opening_rejected ?? 0}</b>
                  <p>OR</p>
                </div>
                <div style={{marginTop:"10px"}}>
                  <b>{callSummary?.include_context_rejected ?? 0}</b>
                  <p>CR</p>
                </div>
                <div style={{marginTop:"10px"}}>
                  <b>{callSummary?.offering_rejected_count ?? 0}</b>
                  <p>OPR</p>
                </div>
                <div style={{marginTop:"10px"}}>
                  <b>{callSummary?.post_offer_rejected_count ?? 0}</b>
                  <p>POR</p>
                </div>
                <div style={{marginTop:"10px"}}>
                  <b>{callSummary?.failure_rate ?? 0}%</b>
                  <p>Failure Rate</p>
                </div>
              </div>
            </div>
          </div>

          {/* 2️⃣ Success Calls Breakdown */}
          {/* 2️⃣ Success Calls Breakdown (SCB) */}
          <div className="fullbodydiv">
            <div className="block1div">
              <div className="chart-container">
                <h2 className="scb_rcb_fontclass">
                  Success Calls Breakdown (SCB)
                </h2>
                <ResponsiveContainer width="100%" height={170}>
                  {rejectedData.length > 0 ? (
                    <PieChart > {/* Reduced height */}
                      <Pie
                        data={rejectedData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={60} // Reduced radius
                        label={({ percent }) => `${(percent * 100).toFixed(0)}%`}
                      >
                        {rejectedData.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  ) : (
                    <p style={{ textAlign: "center" }}>No data available</p>
                  )}
                </ResponsiveContainer>
                {/* 📌 Custom Legend with Bullet Points */}
                <ul className="legend">
                  {rejectedData.map((entry, index) => (
                    <li key={index}>
                      <span
                        className="bullet"
                        style={{ backgroundColor: entry.color }}
                      ></span>
                      {entry.name}
                    </li>
                  ))}
                </ul>
              </div>

              {/* 3️⃣ Rejected Calls Breakdown */}
              {/* 3️⃣ Rejected Calls Breakdown (RCB) */}
              <div className="chart-container">
                <h2 className="cst_crt_fontclass">CST Funnel</h2>
                <div className="funnel">
                  {cstFunnelData.map((item, index) => (
                    <div
                      key={index}
                      className="funnel-item"
                      style={{
                        backgroundColor: item.color,
                        width: `${100 - index * 12}%`, // Decreasing width for pyramid effect
                      }}
                    >
                      {item.name}: {item.value}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 4️⃣ CST Funnel */}
            <div className="block2div">
              {/* 3️⃣ Rejected Calls Breakdown (RCB) */}
              <div className="chart-container">
                <h2 className="scb_rcb_fontclass">
                  Rejected Calls Breakdown (RCB)
                </h2>
                <ResponsiveContainer width="100%" height={170}>
                  {rejectedData.length > 0 ? (
                    <PieChart >
                      <Pie
                        data={rejectedData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={60}
                        label={({ percent }) => `${(percent * 100).toFixed(0)}%`}
                      >
                        {rejectedData.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  ) : (
                    <p style={{ textAlign: "center" }}>No data available</p>
                  )}
                </ResponsiveContainer>

                {/* 📌 Custom Bullet Legend */}
                <ul className="legend">
                  {rejectedData.map((entry, index) => (
                    <li key={index}>
                      <span
                        className="bullet"
                        style={{ backgroundColor: entry.color }}
                      ></span>
                      {entry.name}
                    </li>
                  ))}
                </ul>
              </div>

              {/* 5️⃣ CRT Funnel */}
              <div className="chart-container">
                <h2 className="cst_crt_fontclass">CRT Funnel</h2>
                <div className="funnel">
                  {crtFunnelData.map((item, index) => (
                    <div
                      key={index}
                      className="funnel-item"
                      style={{
                        backgroundColor: item.color,
                        width: `${100 - index * 12}%`, // Decreasing width for pyramid effect
                      }}
                    >
                      {item.name}: {item.value}
                    </div>
                  ))}
                </div>
              </div>
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
}
