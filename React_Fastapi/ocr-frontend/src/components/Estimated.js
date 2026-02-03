import React, { useState, useEffect } from "react";
import {
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import Layout from "../layout";
import "../layout.css";
import "./Estimated.css";

export default function Estimated() {
  const npsData = [{ value: 15.55 }];
  const csatData = [{ value: 67.2 }];

  const gaugeColors = ["#FF6B6B", "#FFD93D", "#3FC1C9"];

  const pieData = [
    { name: "Positive", value: 39.1, color: "#0088FE" },
    { name: "Negative", value: 39.8, color: "#FF4081" },
    { name: "Neutral", value: 21.1, color: "#FFA500" },
  ];

  const trendData = [
    { date: "Mar 1, 2025", NPS: 20.47, CSAT: 70.1 },
    { date: "Mar 2, 2025", NPS: 14.27, CSAT: 66.1 },
    { date: "Mar 3, 2025", NPS: 11.92, CSAT: 65.5 },
];


  //loading code start===>
  const [loading, setLoading] = useState(true);
  const [startDate, setStartDate] = useState(new Date().toISOString().split("T")[0]);
  const [endDate, setEndDate] = useState(new Date().toISOString().split("T")[0]);

  useEffect(() => {
    setTimeout(() => {
      setLoading(false);
    }, 2000);
  }, []);

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
              <input type="submit" class="setsubmitbtn" value="Submit" />
            </label>
          </div>
        </div>
        <h4 style={{fontSize:"16px"}}>Estimated NPS & CSAT</h4>

        <div className="dashboard-grid">
          {/* NPS Gauge Chart */}
          <div className="widget">
            <h5 className="leftside">Net Promoter Score (NPS)</h5>
            <ResponsiveContainer width="100%" height={150}>
              <PieChart>
                <Pie
                  data={npsData}
                  dataKey="value"
                  cx="50%"
                  cy="100%"
                  innerRadius={60}
                  outerRadius={100}
                  startAngle={180}
                  endAngle={0}
                >
                  <Cell fill={gaugeColors[0]} />
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <p className="gauge-label">{npsData[0].value}</p>
          </div>

          {/* CSAT Gauge Chart */}
          <div className="widget">
            <h5 className="leftside">Customer Satisfaction (CSAT)</h5>
            <ResponsiveContainer width="100%" height={150}>
              <PieChart>
                <Pie
                  data={csatData}
                  dataKey="value"
                  cx="50%"
                  cy="100%"
                  innerRadius={60}
                  outerRadius={100}
                  startAngle={180}
                  endAngle={0}
                >
                  <Cell fill={gaugeColors[2]} />
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <p className="gauge-label">{csatData[0].value}%</p>
          </div>

          {/* Feedback Breakdown */}
          <div className="widget">
            <h5 className="leftside">Feedback Status Breakdown</h5>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ name, percent }) =>
                    ` ${(percent * 100).toFixed(1)}%`
                  } // Shows labels inside the graph
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>

            {/* Display Legend as List */}
            <ul className="feedback-legend">
              {pieData.map((item, index) => (
                <li key={index} style={{ color: item.color }}>
                  <span
                    className="legend-box"
                    style={{ backgroundColor: item.color }}
                  ></span>
                  {item.name}
                </li>
              ))}
            </ul>
          </div>

          {/* NPS and CSAT Analysis Table */}
          <div className="widget full-width" style={{ width: "100%" }}>
            <h3 className="leftside">NPS and CSAT Analysis</h3>
            <table>
              <thead>
                <tr>
                  <th>Call Date</th>
                  <th>Detractor Count</th>
                  <th>Passive Count</th>
                  <th>Promoter Count</th>
                  <th>NPS Score</th>
                  <th>CSAT Score</th>
                  <th>Total Feedback</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Mar 3, 2025</td>
                  <td className="detractor">689</td>
                  <td className="passive">381</td>
                  <td className="promoter">927</td>
                  <td className="nps">11.92</td>
                  <td className="csat">65.5%</td>
                  <td className="total-feedback">1,997</td>
                </tr>
                <tr>
                  <td>Mar 2, 2025</td>
                  <td className="detractor">635</td>
                  <td className="passive">445</td>
                  <td className="promoter">1,187</td>
                  <td className="nps">14.27</td>
                  <td className="csat">66.1%</td>
                  <td className="total-feedback">2,467</td>
                </tr>
                <tr>
                  <td>Mar 1, 2025</td>
                  <td className="detractor">778</td>
                  <td className="passive">511</td>
                  <td className="promoter">1,310</td>
                  <td className="nps">20.47</td>
                  <td className="csat">70.1%</td>
                  <td className="total-feedback">2,599</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* NPS and CSAT Trend */}
          <div className="widget full-width" style={{ width: "100%" }}>
            <h3 className="leftside">NPS and CSAT Day Wise Trend</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={trendData}>
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="NPS"
                  stroke="#FF0000"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="CSAT"
                  stroke="#FFA500"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </Layout>
  );
}
