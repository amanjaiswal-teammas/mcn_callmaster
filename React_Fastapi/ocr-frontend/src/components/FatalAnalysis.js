// import React from "react";
import React, { useState, useEffect } from "react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import Layout from "../layout";
import "../layout.css";
import "./FatalAnalysis.css";
import { BASE_URL } from "./config";

const Fatal = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loading1, setLoading1] = useState(false);
  const [error, setError] = useState(null);
  const [startDate, setStartDate] = useState(new Date().toISOString().split("T")[0]);
  const [endDate, setEndDate] = useState(new Date().toISOString().split("T")[0]);
  const [topContributors, setTopContributors] = useState([]);
  const [dayWiseData, setDayWiseData] = useState([]);

  const [auditData, setAuditData] = useState([]);
  const client_id = localStorage.getItem("client_id");

  const totals = auditData.reduce(
    (acc, row) => ({
      auditCount: acc.auditCount + row.auditCount,
      cqScore: acc.cqScore + row.cqScore,
      fatalCount: acc.fatalCount + row.fatalCount,
      fatalPercentage: acc.fatalPercentage + parseFloat(row.fatalPercentage),
      belowAvgCall: acc.belowAvgCall + parseFloat(row.belowAvgCall),
      avgCalls: acc.avgCalls + parseFloat(row.avgCalls),
      goodCalls: acc.goodCalls + parseFloat(row.goodCalls),
      excellentCalls: acc.excellentCalls + parseFloat(row.excellentCalls),
    }),
    {
      auditCount: 0,
      cqScore: 0,
      fatalCount: 0,
      fatalPercentage: 0,
      belowAvgCall: 0,
      avgCalls: 0,
      goodCalls: 0,
      excellentCalls: 0,
    }
  );

  // const dayWiseData = [
  //   { date: "Feb 19, 2025", fatal: 11 },
  //   { date: "Feb 20, 2025", fatal: 5 },
  // ];

  // const topContributors = [
  //   { name: "Gaurav", audit: 53, fatal: 3, fatalPercent: "6%" },
  //   { name: "Vartika Mishra", audit: 28, fatal: 2, fatalPercent: "7%" },
  //   { name: "Karan Solanki", audit: 64, fatal: 2, fatalPercent: "3%" },
  //   { name: "Arushi", audit: 50, fatal: 2, fatalPercent: "4%" },
  //   { name: "Rekha Sharma", audit: 59, fatal: 2, fatalPercent: "3%" },
  // ];

  const scenarioData = [
    {
      date: "Feb-20",
      queryFatal: 36,
      complaintFatal: 19,
      requestFatal: 3,
      saleDoneFatal: 0,
      total: 3,
    },
    // {
    //   date: "Feb-19",
    //   queryFatal: 7,
    //   complaintFatal: 4,
    //   requestFatal: 0,
    //   saleDoneFatal: 0,
    //   total: 11,
    // },
  ];

  // Dummy data for Week & Scenario Wise Fatal Count
  const weekScenarioData = [
    {
      week: "Week 3",
      queryFatal: "50%",
      complaintFatal: "50%",
      requestFatal: "0%",
      saleDoneFatal: "0%",
      total: 16,
    },
  ];

  const data = [
    {
      agent: "Vartika Mishra",
      auditCount: 28,
      cqScore: 70,
      fatalCount: 2,
      fatalPercentage: "7%",
      belowAvgCall: "64%",
      avgCalls: "14%",
      goodCalls: "7%",
      excellentCalls: "14%",
    },
    {
      agent: "Gaurav",
      auditCount: 53,
      cqScore: 81,
      fatalCount: 3,
      fatalPercentage: "6%",
      belowAvgCall: "42%",
      avgCalls: "2%",
      goodCalls: "23%",
      excellentCalls: "34%",
    },
    {
      agent: "Arushi",
      auditCount: 50,
      cqScore: 80,
      fatalCount: 2,
      fatalPercentage: "4%",
      belowAvgCall: "42%",
      avgCalls: "2%",
      goodCalls: "14%",
      excellentCalls: "42%",
    },
    {
      agent: "Rekha Sharma",
      auditCount: 59,
      cqScore: 78,
      fatalCount: 2,
      fatalPercentage: "3%",
      belowAvgCall: "41%",
      avgCalls: "0%",
      goodCalls: "17%",
      excellentCalls: "39%",
    },
    {
      agent: "Pallavi Ray",
      auditCount: 30,
      cqScore: 71,
      fatalCount: 1,
      fatalPercentage: "3%",
      belowAvgCall: "60%",
      avgCalls: "13%",
      goodCalls: "10%",
      excellentCalls: "17%",
    },
    {
      agent: "Karan Solanki",
      auditCount: 64,
      cqScore: 81,
      fatalCount: 2,
      fatalPercentage: "3%",
      belowAvgCall: "47%",
      avgCalls: "3%",
      goodCalls: "11%",
      excellentCalls: "39%",
    },
    {
      agent: "Ashwani",
      auditCount: 71,
      cqScore: 72,
      fatalCount: 3,
      fatalPercentage: "3%",
      belowAvgCall: "58%",
      avgCalls: "1%",
      goodCalls: "8%",
      excellentCalls: "31%",
    },
    {
      agent: "Prashanjit Sarkar",
      auditCount: 48,
      cqScore: 83,
      fatalCount: 1,
      fatalPercentage: "2%",
      belowAvgCall: "42%",
      avgCalls: "0%",
      goodCalls: "10%",
      excellentCalls: "48%",
    },
    {
      agent: "Shweta",
      auditCount: 58,
      cqScore: 81,
      fatalCount: 1,
      fatalPercentage: "2%",
      belowAvgCall: "47%",
      avgCalls: "5%",
      goodCalls: "16%",
      excellentCalls: "33%",
    },
    {
      agent: "Manish",
      auditCount: 16,
      cqScore: 78,
      fatalCount: 0,
      fatalPercentage: "0%",
      belowAvgCall: "69%",
      avgCalls: "0%",
      goodCalls: "8%",
      excellentCalls: "23%",
    },
    {
      agent: "Sandhya Yadav",
      auditCount: 34,
      cqScore: 78,
      fatalCount: 0,
      fatalPercentage: "0%",
      belowAvgCall: "53%",
      avgCalls: "3%",
      goodCalls: "12%",
      excellentCalls: "32%",
    },
  ];

  const fetchData = async () => {
    try {

      setLoading1(true);
      setError(null);

      // Fetch all APIs in parallel
      const [
        topAgentsResponse,
        dayWiseResponse,
        auditSummaryResponse,
        fatalCountResponse, // ✅ Added missing API response
      ] = await Promise.all([

        fetch(
          `${BASE_URL}/top_agents_fatal_summary?client_id=${client_id}&start_date=${startDate}&end_date=${endDate}&limit=5`
        ),
        fetch(
          `${BASE_URL}/daywise_fatal_summary?client_id=${client_id}&start_date=${startDate}&end_date=${endDate}`
        ),
        fetch(
          `${BASE_URL}/agent_audit_summary?client_id=${client_id}&start_date=${startDate}&end_date=${endDate}`
        ),
        fetch(
          `${BASE_URL}/fatal_count?client_id=${client_id}&start_date=${startDate}&end_date=${endDate}`
        ),
      ]);


      if (
        !topAgentsResponse.ok ||
        !dayWiseResponse.ok ||
        !auditSummaryResponse.ok ||
        !fatalCountResponse.ok // ✅ Ensure it's checked
      ) {
        throw new Error(
          `API Error: 
          Top Agents: ${topAgentsResponse.status}, 
          Day Wise: ${dayWiseResponse.status}, 
          Audit Summary: ${auditSummaryResponse.status}, 
          Fatal Count: ${fatalCountResponse.status}`
        );
      }


      const [
        topAgentsData,
        dayWiseData,
        auditSummaryData,
        fatalCountData, // ✅ Ensure it's processed
      ] = await Promise.all([
        topAgentsResponse.json(),
        dayWiseResponse.json(),
        auditSummaryResponse.json(),
        fatalCountResponse.json(),
      ]);


      if (
        !Array.isArray(topAgentsData) ||
        !Array.isArray(dayWiseData) ||
        !Array.isArray(auditSummaryData)
      ) {
        throw new Error("Invalid data format received from API.");
      }


      const formattedTopContributors = topAgentsData.map((agent) => ({
        name: agent["Agent Name"] || "N/A",
        audit: agent["Audit Count"] || 0,
        fatal: agent["Fatal Count"] || 0,
        fatalPercent: agent["Fatal%"] || "0%",
      }));


      const formattedDayWiseData = dayWiseData.map((entry) => ({
        date: entry["CallDate"]
          ? new Date(entry["CallDate"]).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "2-digit",
          })
          : "Unknown",
        fatal: entry["Fatal Count"] || 0,
      }));


      const formattedAuditData = auditSummaryData.map((agent) => ({
        agent: agent["Agent Name"] || "N/A",
        auditCount: agent["Audit Count"] || 0,
        cqScore: parseFloat(agent["CQ Score%"]) || 0,
        fatalCount: agent["Fatal Count"] || 0,
        fatalPercentage: agent["Fatal%"] || "0%",
        belowAvgCall: agent["Below Average Calls"] || "0%",
        avgCalls: agent["Average Calls"] || "0%",
        goodCalls: agent["Good Calls"] || "0%",
        excellentCalls: agent["Excellent Calls"] || "0%",
      }));


      setTopContributors((prev) =>
        JSON.stringify(prev) !== JSON.stringify(formattedTopContributors)
          ? formattedTopContributors
          : prev
      );

      setDayWiseData((prev) =>
        JSON.stringify(prev) !== JSON.stringify(formattedDayWiseData)
          ? formattedDayWiseData
          : prev
      );

      setAuditData((prev) =>
        JSON.stringify(prev) !== JSON.stringify(formattedAuditData)
          ? formattedAuditData
          : prev
      );

      setStats(fatalCountData);

    } catch (err) {
      console.error("Fetch Error:", err);
      setError(err.message);
    } finally {
      setLoading1(false);
    }
  };



  useEffect(() => {
    const clientId = localStorage.getItem("client_id");

    const fetchStats = async () => {
      try {
        const response = await fetch(`${BASE_URL}/fatal_count?client_id=${clientId}`);
        if (!response.ok) throw new Error("Failed to fetch statistics");

        const data = await response.json();
        setStats(data);
      } catch (err) {
        setError(err.message);
      }
    };

    const fetchTopFive = async () => {
      try {
        const response = await fetch(
          `${BASE_URL}/top_agents_fatal_summary?client_id=${clientId}&limit=5`
        );
        if (!response.ok) throw new Error("Failed to fetch top agents");

        const data = await response.json();

        // Properly format the data before setting state
        const formattedTopContributors = data.map((agent) => ({
          name: agent["Agent Name"] || "N/A",
          audit: agent["Audit Count"] || 0,
          fatal: agent["Fatal Count"] || 0,
          fatalPercent: agent["Fatal%"] || "0%",
        }));

        setTopContributors(formattedTopContributors); // Use formatted data
      } catch (err) {
        console.error("Error fetching top agents:", err);
        setError(err.message);
      }
    };

    const fetchDayWise = async () => {
      try {
        setError(null);

        const clientId = localStorage.getItem("client_id"); // Make sure clientId is correctly assigned

        const response = await fetch(
          `${BASE_URL}/daywise_fatal_summary?client_id=${clientId}`
        );

        if (!response.ok) {
          throw new Error(
            `Failed to fetch daywise statistics: ${response.status} ${response.statusText}`
          );
        }

        const data = await response.json();

        const formattedDayWiseData = data.map((entry) => ({
          date: entry["CallDate"]
            ? new Date(entry["CallDate"]).toLocaleDateString("en-US", {
              year: "numeric",
              month: "short",
              day: "2-digit",
            })
            : "Unknown",
          fatal: entry["Fatal Count"] || 0,
        }));

        setDayWiseData((prev) =>
          JSON.stringify(prev) !== JSON.stringify(formattedDayWiseData)
            ? formattedDayWiseData
            : prev
        );

      } catch (err) {
        console.error("Error fetching daywise statistics:", err);
        setError(err.message);
      }
    };

    const fetchAuditData = async () => {
      try {
        setError(null); // Clear previous errors

        const clientId = localStorage.getItem("client_id"); // Ensure clientId is defined

        const response = await fetch(
          `${BASE_URL}/agent_audit_summary?client_id=${clientId}`
        );

        if (!response.ok) {
          throw new Error(
            `Failed to fetch audit data: ${response.status} ${response.statusText}`
          );
        }

        const data = await response.json();

        // Format the response data properly
        const formattedAuditData = data.map((agent) => ({
          agent: agent["Agent Name"] || "N/A",
          auditCount: agent["Audit Count"] || 0,
          cqScore: parseFloat(agent["CQ Score%"]) || 0,
          fatalCount: agent["Fatal Count"] || 0,
          fatalPercentage: agent["Fatal%"] || "0%",
          belowAvgCall: agent["Below Average Calls"] || "0%",
          avgCalls: agent["Average Calls"] || "0%",
          goodCalls: agent["Good Calls"] || "0%",
          excellentCalls: agent["Excellent Calls"] || "0%",
        }));

        // Update state only if the data has changed
        setAuditData((prev) =>
          JSON.stringify(prev) !== JSON.stringify(formattedAuditData)
            ? formattedAuditData
            : prev
        );

      } catch (err) {
        console.error("Error fetching audit data:", err);
        setError(err.message);
      }
    };




    const fetchData = async () => {
      setLoading(true);
      await Promise.all([fetchStats(), fetchTopFive(), fetchDayWise(), fetchAuditData()]); // Run both functions in parallel
      setLoading(false); // Set loading to false after both complete
    };

    fetchData();
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

  return (
    <Layout heading="Title to be decided">
      {/* <div className="dashboard-container"> */}
      <div className={`dashboard-container ${loading ? "blurred" : ""}`}>
        <header className="header" style={{backgroundColor:"rgb(15, 23, 42)",color:"grey"}}>
          {/* <div> */}
          <label>
            {" "}
            <h3>DialDesk</h3>
          </label>
          <div className="setheaderdiv">
            <label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </label>
            <label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </label>
            {/* <button onClick={fetchData}>Submit</button> */}
            <label>
              <input className="setsubmitbtn" onClick={fetchData} value={"Submit"} readOnly />
            </label>
          </div>
          {/* </div> */}
        </header>

        <div className="maincon">
          <div className="leftbody">
            <div className="stats">
              <div className="stat-box" style={{backgroundColor:"red",color:"white"}}>
                <h6>CQ Score%</h6>
                <p className="score">{stats?.cq_score || "N/A"}%</p>
              </div>
              <div className="stat-box" style={{backgroundColor:"rgb(30, 136, 229)",color:"white"}}>
                <h6>Audit Count</h6>
                <p className="score">{stats?.audit_cnt || "N/A"}</p>
              </div>
              <div className="stat-box" style={{backgroundColor:"rgb(67, 160, 71)",color:"white"}}>
                <h6>Fatal Count</h6>
                <p className="score">{stats?.fatal_count || "N/A"}</p>
              </div>
              <div className="stat-box" style={{backgroundColor:"orange",color:"white"}}>
                <h6>Fatal%</h6>
                <p className="score">{stats?.fatal_percentage || "N/A"}%</p>
              </div>
            </div>

            <div className="top-contributors">
              <h5 style={{ fontSize: "16px" }}>Top 5 Fatal Contributors</h5>
              <table>
                <thead>
                  <tr>
                    <th>Agent Name</th>
                    <th>Audit Count</th>
                    <th>Fatal Count</th>
                    <th>Fatal%</th>
                  </tr>
                </thead>
                <tbody>
                  {topContributors.map((agent, index) => (
                    <tr key={index}>
                      <td>{agent.name}</td>
                      <td>{agent.audit}</td>
                      <td>{agent.fatal}</td>
                      <td className="highlight">{agent.fatalPercent}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="chart-section">
              <h5 style={{ fontSize: "16px" }}>Day Wise Fatal%</h5>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={dayWiseData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="fatal" fill="#798e43" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rightbody">
            {/*  right code */}
            <div className="right-card">
              <h5 className="text-center"style={{ marginBottom: '8px' }}>Scenario Wise Fatal Count</h5>

              <div className="stats">
                <div className="stat-box" style={{backgroundColor:"orange",color:"white"}}>
                  <h6>Query Fatal</h6>
                  <p className="score">{stats?.query_fatal ?? "N/A"}</p>
                </div>
                <div className="stat-box"  style={{backgroundColor:"rgb(30, 136, 229)",color:"white"}}>
                  <h6>Complaint Fatal</h6>
                  <p className="score">{stats?.Complaint_fatal ?? "N/A"}</p>
                </div>
                <div className="stat-box" style={{backgroundColor:"rgb(67, 160, 71)",color:"white"}}>
                  <h6>Request Fatal</h6>
                  <p className="score">{stats?.Request_fatal ?? "N/A"}</p>
                </div>
                <div className="stat-box" style={{backgroundColor:"red",color:"white"}}>
                  <h6>Sale Done Fatal</h6>
                  <p className="score">{stats?.sale_fatal ?? "N/A"}</p>
                </div>
              </div>

              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Query Fatal</th>
                    <th>Complaint Fatal</th>
                    <th>Request Fatal</th>
                    <th>Sale Done Fatal</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {scenarioData.map((row, index) => (
                    <tr key={index}>
                      <td>{row.date}</td>
                      <td className={row.queryFatal > 0 ? "highlight" : ""}>
                        {row.queryFatal}
                      </td>
                      <td className={row.complaintFatal > 0 ? "highlight" : ""}>
                        {row.complaintFatal}
                      </td>
                      <td className={row.requestFatal > 0 ? "highlight" : ""}>
                        {row.requestFatal}
                      </td>
                      <td className={row.saleDoneFatal > 0 ? "highlight" : ""}>
                        {row.saleDoneFatal}
                      </td>
                      <td className="bold">{row.total}</td>
                    </tr>
                  ))}
                </tbody>

                <tfoot>
                  <tr>
                    <td>Grand Total</td>
                    <td className="bold">
                      {scenarioData.reduce((sum, row) => sum + row.queryFatal, 0)}
                    </td>
                    <td className="bold">
                      {scenarioData.reduce(
                        (sum, row) => sum + row.complaintFatal,
                        0
                      )}
                    </td>
                    <td className="bold">
                      {scenarioData.reduce(
                        (sum, row) => sum + row.requestFatal,
                        0
                      )}
                    </td>
                    <td className="bold">
                      {scenarioData.reduce(
                        (sum, row) => sum + row.saleDoneFatal,
                        0
                      )}
                    </td>
                    <td className="bold">
                      {scenarioData.reduce((sum, row) => sum + row.total, 0)}
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>

            {/* Week & Scenario Wise Fatal Count */}
            <div className="right-card">
              <h5 className="text-center">Week & Scenario Wise Fatal Count</h5>
              <table>
                <thead>
                  <tr>
                    <th>Week</th>
                    <th>Query Fatal</th>
                    <th>Complaint Fatal</th>
                    <th>Request Fatal</th>
                    <th>Sale Done Fatal</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {weekScenarioData.map((row, index) => (
                    <tr key={index}>
                      <td>{row.week}</td>
                      <td className={row.queryFatal !== "0%" ? "highlight" : ""}>
                        {row.queryFatal}
                      </td>
                      <td
                        className={row.complaintFatal !== "0%" ? "highlight" : ""}
                      >
                        {row.complaintFatal}
                      </td>
                      <td
                        className={row.requestFatal !== "0%" ? "highlight" : ""}
                      >
                        {row.requestFatal}
                      </td>
                      <td
                        className={row.saleDoneFatal !== "0%" ? "highlight" : ""}
                      >
                        {row.saleDoneFatal}
                      </td>
                      <td className="bold">{row.total}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <td>Grand Total</td>
                    <td className="bold">50%</td>
                    <td className="bold">50%</td>
                    <td className="bold">0%</td>
                    <td className="bold">0%</td>
                    <td className="bold">16</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>

        {/* footer */}

        <div className="full-width">
          <h4 style={{ fontSize: "16px" }}>Agent Wise Performance</h4>
          <table>
            <thead>
              <tr>
                <th>Agent Name</th>
                <th>Audit Count</th>
                <th>CQ Score%</th>
                <th>Fatal Count</th>
                <th>Fatal%</th>
                <th>Below Average Call</th>
                <th>Average Calls</th>
                <th>Good Calls</th>
                <th>Excellent Calls</th>
              </tr>
            </thead>
            <tbody>
              {auditData.map((row, index) => (
                <tr key={index}>
                  <td>{row.agent}</td>
                  <td>{row.auditCount}</td>
                  <td style={{ backgroundColor: row.cqScore < 70 ? "#d2b4de" : "#d4ac2e" }}>
                    {row.cqScore}
                  </td>
                  <td>{row.fatalCount}</td>
                  <td>{row.fatalPercentage}</td>
                  <td>{row.belowAvgCall}</td>
                  <td>{row.avgCalls}</td>
                  <td>{row.goodCalls}</td>
                  <td>{row.excellentCalls}</td>
                </tr>
              ))}
            </tbody>

          </table>
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

export default Fatal;
