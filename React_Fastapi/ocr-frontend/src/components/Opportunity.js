import React, { useState, useEffect } from "react";
import Layout from "../layout"; // Import layout component
import "../layout.css"; // Import styles
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import "./Opportunity.css";
import axios from "axios";
import { BASE_URL } from "./config";


export default function Opportunity() {
  //loading code start===>
  const [loading, setLoading] = useState(true);
  const [loading1, setLoading1] = useState(false);
  const [startDate, setStartDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [endDate, setEndDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [moBreakdownData, setMoBreakdownData] = useState([]);
  const [moBreakupData, setMoBreakupData] = useState([]);
  const [nedEdBreakdown, setNedEdBreakdown] = useState([]);
  const [data, setData] = useState({});
  const [error, setError] = useState("");

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

  const fetchData = async () => {
    const clientId = localStorage.getItem("client_id");

    if (!clientId || !startDate || !endDate) {
      setError("Please fill in all fields.");
      return;
    }

    setError("");
    setLoading1(true);

    try {
      // Fetch both APIs concurrently
      const [moResponse, nedEdResponse] = await Promise.all([
        axios.get(`${BASE_URL}/get_mo_breakdown`, {
          params: {
            client_id: clientId,
            start_date: startDate,
            end_date: endDate,
          },
        }),
        axios.get(`${BASE_URL}/get_ned_ed_breakdown`, {
          params: {
            client_id: clientId,
            start_date: startDate,
            end_date: endDate,
          },
        }),
      ]);

      // Process MO Breakdown
      const moData = moResponse.data;
      setData(moData);

      setMoBreakdownData([
        {
          name: "Non Workable",
          value: moData["Non Workable%"] || 0,
          color: "#ff1493",
        },
        { name: "Workable", value: moData["Workable%"] || 0, color: "#ff4500" },
      ]);

      // Process NED/ED Breakdown
      const nedEdData = nedEdResponse.data;
      setNedEdBreakdown(nedEdData["NED/ED Breakdown"] || []);

      // Generate random colors
      const getRandomColor = () =>
        "#" + Math.floor(Math.random() * 16777215).toString(16);

      // Map NED/ED Breakdown to moBreakupData
      const formattedMoBreakupData = (nedEdData["NED/ED Breakdown"] || []).map(
        (item) => ({
          name: item["NED/ED Category"],
          value: item["Contribution"],
          count: item["Count"],
          color: getRandomColor(),
        })
      );

      setMoBreakupData(formattedMoBreakupData);
    } catch (error) {
      console.error("Error fetching data:", error);
      setError("Failed to fetch data. Please try again.");
    } finally {
      setLoading1(false);
    }
  };

  return (
    <Layout heading="Title to be decided">
      <div className={`dashboard-container ${loading1 ? "blurred" : ""}`}>
        <div className="dashboard-container-opportunity">
          <div className="header">
            <h4>AI-Enhanced Sales Strategy Dashboard</h4>
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
                  onClick={fetchData}
                />
              </label>
            </div>
          </div>


          <div className="firstdivno">
            <div className="graphdiv">
              <div className="set-con">
                <h5 style={{ fontSize: "16px" }}>Missed Opportunity Analysis (MOA)</h5>
                <div className="divide">
                  <div className="metric-card white">
                    <h5 style={{ fontSize: "13px" }}>Total Opportunities</h5>
                    <b style={{ fontWeight: "100" }}>
                      {data["Total Opportunities"]
                        ? data["Total Opportunities"].toLocaleString()
                        : "0"}
                    </b>
                  </div>
                  <div className="metric-card white">
                    <h5 style={{ fontSize: "13px" }}>MO Count</h5>
                    <b style={{ fontWeight: "100" }}>
                      {data["MO Count"] ? data["MO Count"].toLocaleString() : "0"}
                    </b>
                  </div>
                </div>
              </div>
              {/* Charts Section */}
              <div className="charts-containermew">
                {/* MO Breakdown */}
                <div className="chart-containernew1">
                  <h5 style={{ fontSize: "16px" }}>MO Breakdown</h5>
                  <ResponsiveContainer width="100%" height={210}>
                    <PieChart >
                      <Pie
                        data={moBreakdownData}
                        dataKey="value"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                      >
                        {moBreakdownData.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>

                  {/* Bullet Legend List */}
                  <ul className="chart-legend">
                    {moBreakdownData.map((entry, index) => (
                      <li key={index}>
                        <span
                          className="legend-bullet"
                          style={{ backgroundColor: entry.color }}
                        ></span>
                        {entry.name} ({entry.value})
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              <div className="chart-containernew1">
                <h3 style={{ fontSize: "16px" }}>MO Breakup</h3>

                <>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={moBreakupData}
                        dataKey="value"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                      >
                        {moBreakupData.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>

                  {/* Bullet Legend List */}
                  <ul className="chart-legend">
                    {moBreakupData.map((entry, index) => (
                      <li
                        key={index}
                        aria-label={`${entry.name}: ${entry.value}`}
                      >
                        <span
                          className="legend-bullet"
                          style={{ backgroundColor: entry.color }}
                        ></span>
                        {entry.name} ({entry.value})
                      </li>
                    ))}
                  </ul>
                </>
              </div>
            </div>

            <div className="tablediv">
              <div className="tables-container1">
                {/* First Table - MO Category */}
                <div className="table-container1">
                  {/* <h3>MO Category</h3> */}
                  <table className="tablebody">
                    <thead
                      style={{
                        position: "sticky",
                        top: 0,
                        backgroundColor: "#fff",
                        zIndex: 2,
                      }}
                    >
                      <tr>
                        <th>MO Category</th>
                        <th>Observations & Insights</th>
                        <th>Count</th>
                        <th>Contr%</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data["MO Breakdown"] &&
                        data["MO Breakdown"].length > 0 ? (
                        data["MO Breakdown"].map((item, index) => (
                          <tr key={index}>
                            <td>{item["MO Category"]}</td>
                            <td>{item["Observations & Insights"]}</td>
                            <td>{item["Count"].toLocaleString()}</td>
                            <td>{item["Contr%"]}%</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td
                            colSpan="4"
                            style={{ textAlign: "center", padding: "10px" }}
                          >
                            No data available
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="table-container2">
                {/* <h3>NED/ED Category</h3> */}
                <table className="tablebodysec">
                  <thead
                    style={{
                      position: "sticky",
                      top: 0,
                      backgroundColor: "#fff",
                      zIndex: 2,
                    }}>
                    <tr>
                      <th>NED/ED Category</th>
                      <th>NED/ED-QS</th>
                      <th>NED/ED Status</th>
                      <th>Count</th>
                      <th>Contr%</th>
                    </tr>
                  </thead>
                  <tbody>
                    {nedEdBreakdown && nedEdBreakdown.length > 0 ? (
                      nedEdBreakdown.map((item, index) => (
                        <tr key={index}>
                          <td>{item["NED/ED Category"]}</td>
                          <td>{item["NED/ED-QS"] || "N/A"}</td>
                          <td>{item["NED/ED Status"] || "N/A"}</td>
                          <td>{item["Count"].toLocaleString()}</td>
                          <td>{item["Contribution"]}%</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="5" style={{ textAlign: "center" }}>
                          No data available
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
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
