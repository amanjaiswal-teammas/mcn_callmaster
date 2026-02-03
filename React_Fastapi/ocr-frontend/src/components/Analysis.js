import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Analysis.css";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
// import "./Analysis.css";
import Layout from "../layout"; // Import layout component
import "../layout.css"; // Import styles
import { Doughnut } from "react-chartjs-2";
import "chart.js/auto";
import { BASE_URL } from "./config";
const Analysis = () => {
  const navigate = useNavigate();
  const handleLogout = () => {
    localStorage.removeItem("token");
    sessionStorage.removeItem("user");
    navigate("/");
  };
  const handleNavigation = (path) => {
    navigate(path);
  };

  const pieData1 = [
    { name: "Top Negative Signals", value: 2, color: "rgb(52, 211, 153)" },
  ];

  // const topNegativeSignals = [
  //   { category: "Abuse", count: 0 },
  //   { category: "Threat", count: 0 },
  //   { category: "Frustration", count: 2 },
  //   { category: "Slang", count: 0 },
  // ];

  // const barDatanew = [
  //   { date: "Feb 8, 2025", Target: 95, Score: 76 },
  //   { date: "Feb 9, 2025", Target: 95, Score: 82 },
  //   { date: "Feb 10, 2025", Target: 95, Score: 76 },
  //   { date: "Feb 11, 2025", Target: 95, Score: 76 },
  //   { date: "Feb 12, 2025", Target: 95, Score: 78 },
  //   { date: "Feb 13, 2025", Target: 95, Score: 79 },
  //   { date: "Feb 14, 2025", Target: 95, Score: 80 }
  // ];

  const data = [
    { name: "Frustration", value: 2, color: "#B71C1C" }, // Dark Red
    { name: "Abuse", value: 0, color: "#E57373" }, // Light Red
    { name: "Threat", value: 0, color: "#FF9800" }, // Orange
    { name: "Slang", value: 0, color: "#64B5F6" }, // Blue
    { name: "Sarcasm", value: 0, color: "#81C784" }, // Green
  ];

  const [dateRange, setDateRange] = useState({
    from: "Feb 8, 2025",
    to: "Feb 14, 2025",
  });

  const barChartData = {
    labels: ["Feb 25", "Jan 25", "Dec 24"],
    datasets: [
      {
        label: "Frustration",
        backgroundColor: "orange",
        data: [123, 167, 33],
      },
      {
        label: "Threat",
        backgroundColor: "blue",
        data: [57, 92, 39],
      },
    ],
  };

  // const monthWiseData = [
  //   {
  //     name: "Dec '24",
  //     Frustration: 33,
  //     Threat: 39,
  //     Slang: 3,
  //     Abuse: 0,
  //     Sarcasm: 0,
  //   },
  //   {
  //     name: "Jan '25",
  //     Frustration: 167,
  //     Threat: 92,
  //     Slang: 29,
  //     Abuse: 0,
  //     Sarcasm: 3,
  //   },
  //   {
  //     name: "Feb '25",
  //     Frustration: 123,
  //     Threat: 57,
  //     Slang: 1,
  //     Abuse: 0,
  //     Sarcasm: 0,
  //   },
  // ];
  // const lastTwoDaysData = [
  //   { name: "Feb 17, 2025", Frustration: 9, Threat: 1 },
  //   { name: "Feb 18, 2025", Frustration: 1, Threat: 1 },
  // ];

  // const doughnutChartData = {
  //   labels: ["Amazon", "Flipkart", "BuyZone Attwin", "Smiths", "Cuemath"],
  //   datasets: [
  //     {
  //       data: [21, 14, 7, 7, 14],
  //       backgroundColor: ["blue", "green", "red", "purple", "orange"],
  //     },
  //   ],
  // };

  // api connect

  const [auditData, setAuditData] = useState(null);
  const [pieData, setPieData] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loading1, setLoading1] = useState(false);
  const [scores, setScores] = useState(null);
  const [performers, setPerformers] = useState([]);
  const [barData, setBarData] = useState([]);
  const [potentialEscalations, setPotentialEscalations] = useState([]); // ✅ For /potential_escalations_data/
  const [negativeData, setNegativeData] = useState([]); // ✅ For /negative_data/
  const [complaintData, setComplaintData] = useState([]);
  const [rawComplaintData, setRawComplaintData] = useState([]);
  const [monthWiseData, setMonthWiseData] = useState([]);
  const [lastTwoDaysData, setLastTwoDaysData] = useState([]);
  const [competitorData, setCompetitorData] = useState([]);
  const client_id = localStorage.getItem("client_id");

  const [doughnutChartData, setDoughnutChartData] = useState({
    labels: [],
    datasets: [
      {
        data: [],
        backgroundColor: [
          "blue",
          "green",
          "red",
          "purple",
          "orange",
          "cyan",
          "yellow",
        ],
      },
    ],
  });

  const [topNegativeSignals, setTopNegativeSignals] = useState([
    { category: "Abuse", count: 0 },
    { category: "Threat", count: 0 },
    { category: "Frustration", count: 0 },
    { category: "Slang", count: 0 },
  ]);

  const [escalationData, setEscalationData] = useState({
    social_media_threat: 0,
    consumer_court_threat: 0,
    potential_scam: 0,
  });

  const today = new Date().toISOString().split("T")[0];
  const [formData, setFormData] = useState({
    // client_id: "375",
    start_date: "",
    end_date: "",
  });

  useEffect(() => {
    setFormData({
      // client_id: "375",
      client_id: localStorage.getItem("client_id"),

      start_date: today,
      end_date: today,
    });
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading1(true);

    try {
      const { client_id, start_date, end_date } = formData;

      const urls = [
        `${BASE_URL}/potential_escalation?client_id=${client_id}&start_date=${start_date}&end_date=${end_date}`,
        `${BASE_URL}/agent_scores?client_id=${client_id}&start_date=${start_date}&end_date=${end_date}`,
        `${BASE_URL}/top_performers?client_id=${client_id}&start_date=${start_date}&end_date=${end_date}`,
        `${BASE_URL}/potential_escalations_data/?client_id=${client_id}&start_date=${start_date}&end_date=${end_date}`,
        `${BASE_URL}/negative_data/?client_id=${client_id}&start_date=${start_date}&end_date=${end_date}`,
        `${BASE_URL}/competitor_data/?client_id=${client_id}&start_date=${start_date}&end_date=${end_date}`, // ✅ Fetch competitor data
        `${BASE_URL}/audit_count?client_id=${client_id}&start_date=${start_date}&end_date=${end_date}`, // ✅ Added Audit Count API
        `${BASE_URL}/call_length_categorization?client_id=${client_id}&start_date=${start_date}&end_date=${end_date}`, // ✅ Added Call Length Categorization API
      ];

      const responses = await Promise.all(urls.map((url) => fetch(url)));

      if (responses.some((response) => !response.ok)) {
        throw new Error("Failed to fetch one or more datasets");
      }

      const [
        escalationData,
        scoresData,
        performersData,
        potentialEscalationsData,
        negativeDataResponse,
        competitorDataResponse,
        auditData, // ✅ Audit Count Response
        callLengthData, // ✅ Call Length Categorization Response
      ] = await Promise.all(responses.map((response) => response.json()));

      console.log("Competitor Data API Response:", competitorDataResponse);
      console.log("Audit Count API Response:", auditData);
      console.log("Call Length Categorization API Response:", callLengthData);

      setCompetitorData(competitorDataResponse);
      setAuditData(auditData);
      setCategories(callLengthData);

      const labels = competitorDataResponse.map((item) => item.Competitor_Name);
      const counts = competitorDataResponse.map((item) => item.Count);
      setDoughnutChartData({
        labels: labels,
        datasets: [
          {
            data: counts,
            backgroundColor: [
              "blue",
              "green",
              "red",
              "purple",
              "orange",
              "cyan",
              "yellow",
            ],
          },
        ],
      });

      setEscalationData({
        social_media_threat:
          escalationData?.potential_escalation?.social_media_threat || 0,
        consumer_court_threat:
          escalationData?.potential_escalation?.consumer_court_threat || 0,
        potential_scam:
          escalationData?.potential_escalation?.potential_scam || 0,
      });

      setTopNegativeSignals([
        {
          category: "Abuse",
          count: escalationData?.negative_signals?.abuse || 0,
        },
        {
          category: "Threat",
          count: escalationData?.negative_signals?.threat || 0,
        },
        {
          category: "Frustration",
          count: escalationData?.negative_signals?.frustration || 0,
        },
        {
          category: "Slang",
          count: escalationData?.negative_signals?.slang || 0,
        },
      ]);

      // ✅ Update pie chart dynamically with audit data
      setPieData([
        {
          name: "Excellent",
          value: auditData.excellent || 0,
          color: "#4CAF50",
        },
        { name: "Good", value: auditData.good || 0, color: "#2d9179" },
        { name: "Average", value: auditData.avg_call || 0, color: "rgb(250, 204, 21)" },
        {
          name: "Below Average",
          value: auditData.b_avg || 0,
          color: "rgb(52, 211, 153)",
        },
      ]);

      setScores(scoresData);
      setPerformers(performersData?.top_performers || []);
      setPotentialEscalations(potentialEscalationsData);
      setNegativeData(negativeDataResponse);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading1(false);
    }
  };

  useEffect(() => {
    const fetchAuditData = async () => {
      try {
        const response = await fetch(
          `${BASE_URL}/negative_data_summary?client_id=${client_id}`
        );
        if (!response.ok) throw new Error("Failed to fetch negative data");

        const data = await response.json();

        // Group by month
        const monthDataMap = {};
        data.last_3_months.forEach(({ month, negative_word }) => {
          if (!monthDataMap[month]) {
            monthDataMap[month] = {
              Frustration: 0,
              Threat: 0,
              Slang: 0,
              Abuse: 0,
              Sarcasm: 0,
            };
          }

          const words = negative_word.toLowerCase().split(", ");
          if (words.includes("frustration"))
            monthDataMap[month].Frustration += 1;
          if (words.includes("threatened") || words.includes("threatens"))
            monthDataMap[month].Threat += 1;
          if (words.includes("slang")) monthDataMap[month].Slang += 1;
          if (words.includes("abusive") || words.includes("abuse"))
            monthDataMap[month].Abuse += 1;
          if (words.includes("sarcasm")) monthDataMap[month].Sarcasm += 1;
        });

        // Convert to array format
        const formattedMonthWiseData = Object.entries(monthDataMap).map(
          ([month, values]) => ({
            name: new Date(month + "-01").toLocaleString("en-US", {
              month: "short",
              year: "2-digit",
            }),
            ...values,
          })
        );

        // Process last 2 days
        const lastTwoDaysFormatted = data.last_2_days.map(
          ({ date, negative_word }) => {
            const words = negative_word.toLowerCase().split(", ");
            return {
              name: new Date(date).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
              }),
              Frustration: words.includes("frustration") ? 1 : 0,
              Threat: words.includes("threatened") ? 1 : 0,
            };
          }
        );

        setMonthWiseData(formattedMonthWiseData);
        setLastTwoDaysData(lastTwoDaysFormatted);
      } catch (error) {
        console.error("Error fetching negative data:", error);
      }
    };

    const fetchAuditCount = async () => {
      try {
        // const clientId = 375;
        const response = await fetch(
          `${BASE_URL}/audit_count?client_id=${client_id}`
        );
        if (!response.ok) throw new Error("Failed to fetch audit count");

        const data = await response.json();
        setAuditData(data);

        // Update pie chart data dynamically
        setPieData([
          { name: "Excellent", value: data.excellent, color: "#4CAF50" },
          { name: "Good", value: data.good, color: "#2d9179" },
          { name: "Average", value: data.avg_call, color: "rgb(250, 204, 21)" },
          { name: "Below Average", value: data.b_avg, color: "rgb(52, 211, 153)" },
        ]);
      } catch (error) {
        console.error("Error fetching audit data:", error);
      }
    };

    const fetchCQTrendData = async () => {
      try {
        const response = await fetch(
          `${BASE_URL}/target_vs_cq_trend?client_id=${client_id}`
        );
        if (!response.ok) throw new Error("Failed to fetch CQ trend data");

        const data = await response.json();

        if (!data.trend || !Array.isArray(data.trend)) {
          console.error("Invalid trend data:", data.trend);
          return;
        }

        // Convert API response into bar chart format
        const formattedData = data.trend.map((item) => ({
          date: new Date(item.date).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
          }),
          score: Math.round(item.cq_score),
          target: item.target,
        }));

        setBarData(formattedData);
      } catch (error) {
        console.error("Error fetching CQ trend data:", error);
      }
    };

    const fetchCategories = async () => {
      try {
        // const clientId = 375;
        const response = await fetch(
          `${BASE_URL}/call_length_categorization?client_id=${client_id}`
        );
        if (!response.ok)
          throw new Error("Failed to fetch call length categorization");

        const data = await response.json();
        setCategories(data);
      } catch (error) {
        console.error("Error fetching call length data:", error);
      }
    };

    const fetchComplaintData = async () => {
      try {
        const response = await fetch(
          `${BASE_URL}/complaints_by_date?client_id=${client_id}`
        );
        if (!response.ok) throw new Error("Failed to fetch complaint data");

        const data = await response.json();

        if (!data.summary || !Array.isArray(data.summary)) {
          console.error("Invalid complaints data:", data.summary);
          return;
        }

        setComplaintData(data.summary);
        setRawComplaintData(data.raw_data);
      } catch (error) {
        console.error("Error fetching complaints data:", error);
      }
    };

    const fetchAgentScores = async () => {
      // const clientId = 375;
      try {
        const response = await fetch(
          `${BASE_URL}/agent_scores?client_id=${client_id}`
        );
        if (!response.ok) throw new Error("Failed to fetch agent scores");

        const data = await response.json();
        setScores(data); // Make sure you have a state variable for agent scores
      } catch (error) {
        console.error("Error fetching agent scores:", error);
      }
    };

    const fetchTopPerformers = async () => {
      // const clientId = 375;

      try {
        const response = await fetch(
          `${BASE_URL}/top_performers?client_id=${client_id}`
        );
        if (!response.ok) throw new Error("Failed to fetch agent scores");

        const data = await response.json();

        setPerformers(data?.top_performers || []); // ✅ Corrected: Set fetched data properly
      } catch (error) {
        console.error("Error fetching agent scores:", error);
      }
    };

    const fetchPotentialEscalations = async () => {
      // const clientId = 375;

      try {
        const response = await fetch(
          `${BASE_URL}/potential_escalation?client_id=${client_id}`
        );
        if (!response.ok) throw new Error("Failed to fetch escalation data");

        const data = await response.json();

        setEscalationData({
          social_media_threat:
            data?.potential_escalation?.social_media_threat || 0,
          consumer_court_threat:
            data?.potential_escalation?.consumer_court_threat || 0,
          potential_scam: data?.potential_escalation?.potential_scam || 0,
        });

        setTopNegativeSignals([
          {
            category: "Abuse",
            count: data?.negative_signals?.abuse || 0,
          },
          {
            category: "Threat",
            count: data?.negative_signals?.threat || 0,
          },
          {
            category: "Frustration",
            count: data?.negative_signals?.frustration || 0,
          },
          {
            category: "Slang",
            count: data?.negative_signals?.slang || 0,
          },
        ]);
      } catch (error) {
        console.error("Error fetching escalation data:", error);
      }
    };

    const fetchPotentialEscalationsData = async () => {
      // const clientId = 375;

      try {
        const response = await fetch(
          `${BASE_URL}/potential_escalations_data?client_id=${client_id}`
        );
        if (!response.ok) throw new Error("Failed to fetch agent scores");

        const data = await response.json();

        setPotentialEscalations(data); // ✅ Corrected: Set fetched data properly
      } catch (error) {
        console.error("Error fetching agent scores:", error);
      }
    };

    const fetchNegativeData = async () => {
      // const clientId = 375;

      try {
        const response = await fetch(
          `${BASE_URL}/negative_data?client_id=${client_id}`
        );
        if (!response.ok) throw new Error("Failed to fetch agent scores");

        const data = await response.json();

        setNegativeData(data);
      } catch (error) {
        console.error("Error fetching agent scores:", error);
      }
    };

    const fetchCompetitorData = async () => {
      // const clientId = 375;

      try {
        const response = await fetch(
          `${BASE_URL}/competitor_data?client_id=${client_id}`
        );
        if (!response.ok) throw new Error("Failed to fetch agent scores");

        const data = await response.json();

        setCompetitorData(data);

        const labels = data.map((item) => item.Competitor_Name);
        const counts = data.map((item) => item.Count);
        setDoughnutChartData({
          labels: labels,
          datasets: [
            {
              data: counts,
              backgroundColor: [
                "blue",
                "green",
                "red",
                "purple",
                "orange",
                "cyan",
                "yellow",
              ],
            },
          ],
        });
      } catch (error) {
        console.error("Error fetching agent scores:", error);
      }
    };

    const fetchData = async () => {
      try {
        await Promise.all([
          fetchCompetitorData(),
          fetchNegativeData(),
          fetchPotentialEscalationsData(),
          fetchPotentialEscalations(),
          fetchTopPerformers(),
          fetchAgentScores(),
          fetchAuditData(),
          fetchAuditCount(),
          fetchCategories(),
          fetchCQTrendData(),
          fetchComplaintData(),
        ]);
      } catch (error) {
        console.error("Error in fetchData:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Show loading message until all data is fetched
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
          <h3>DialDesk</h3>
          {/* <div className="date-picker">Feb 19, 2025 - Feb 20, 2025</div> */}
          <div className="setdate">
            <form className="setdatewidth" onSubmit={handleSubmit}>
              <label>
                <input
                  type="date"
                  name="start_date"
                  value={formData.start_date}
                  onChange={handleChange}
                  required
                />
              </label>
              <label>
                <input
                  type="date"
                  name="end_date"
                  value={formData.end_date}
                  onChange={handleChange}
                  required
                />
              </label>
              <label>
                <input type="submit" class="" style={{backgroundColor:"rgb(251, 191, 36)"}} value="Submit" />
              </label>
            </form>
          </div>
        </header>
        <div className="callandache">
          <div className="categorization">
            <div className="cqscore">
              <div className="card-container">
                {[
  {
    title: "CQ Score",
    value: `${auditData.cq_score}%`,
    textColor: "text-red-600",
  },
//  {
//    title: "Fatal CQ Score",
//    value: "84%",
//    textColor: "text-green-600",
//  },
  {
    title: "Audit Count",
    value: auditData.audit_cnt,
    textColor: "text-blue-600",
  },
//  {
//    title: "Excellent Call",
//    value: auditData.excellent,
//    textColor: "text-purple-600",
//  },
  {
    title: "Good Call",
    value: auditData.good,
    textColor: "text-green-600",
  },
  {
    title: "Average Call",
    value: auditData.avg_call,
    textColor: "text-yellow-600",
  },
  {
    title: "Below Call",
    value: auditData.b_avg,
    textColor: "text-gray-600",
  },
].map((card, index) => {
  let bgColor = "";

  if (card.title === "Average Call") {
    bgColor = "orange";
  } else if (card.title === "Below Call") {
    bgColor = "red";
  } else if (card.title === "Good Call") {
    bgColor = "#4bd9f0";
  }
//  else if (card.title === "Excellent Call") {
//    bgColor = "rgb(52, 211, 153)";
//  }

  else if (card.title === "Audit Count") {
    bgColor = "rgb(67, 160, 71)";
  }

//  else if (card.title === "Fatal CQ Score") {
//    bgColor = "rgb(250, 204, 21)";
//  }

  else if (card.title === "CQ Score") {
    bgColor = "rgb(30, 136, 229)";
  }

   else {
    bgColor = "white";
  }

              return (
                <div key={index} className="card" style={{ backgroundColor: bgColor }}>
                  <h6>{card.title}</h6>
                  <p className={`text-2xl font-bold ${card.textColor}`}>
                    {card.value}
                  </p>
                </div>
              );
            })}

              </div>
            </div>

            <div className="catoopening">
              <div className="cato">
                <p>Acht Categorization</p>
                <table className="performer">
                  <thead>
                    <tr>
                      <th>Category</th>
                      <th>Audit Count</th>
                      <th>Fatal%</th>
                      <th>CQ Score%</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categories.map((item, index) => (
                      <tr
                        key={index}
                        className={
                          item["ACH Category"] === "Grand Total"
                            ? "font-bold"
                            : ""
                        }
                      >
                        <td>{item["ACH Category"]}</td>
                        <td>{item["Audit Count"]}</td>
                        <td
                          style={{
                            backgroundColor:
                              parseFloat(item["Fatal%"]) > 50.0
                                ? "#ef2d2d"
                                : "#d2b4de",
                          }}
                        >
                          {item["Fatal%"]}
                        </td>
                        <td>{item["Score%"]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="opening">
                {/* Soft Skills Scores */}
                {scores && Object.keys(scores).length > 0 ? (
                  <div className="soft-skills-container softskill">
                    {[
                      { title: "Opening", value: `${scores.opening}%` },
                      { title: "Soft Skills", value: `${scores.soft_skills}%` },
                      {
                        title: "Hold Procedure",
                        value: `${scores.hold_procedure}%`,
                      },
                      { title: "Resolution", value: `${scores.resolution}%` },
                      { title: "Closing", value: `${scores.closing}%` },
                      { title: "Average Score", value: `${scores.avg_score}%` },
                    ].map((skill, index) => (
                      <div key={index} className="soft-skill-row">
                        <span className="soft-skill-title">{skill.title}</span>
                        <span className="soft-skill-value">{skill.value}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <table className="performer1">
                    <tbody>
                      <tr>
                        <td colSpan="5">No data available</td>
                      </tr>
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          </div>

          <div className="callwise">
            <h3 style={{ fontSize: '20px' }}
            >Call Wise</h3>
            <PieChart width={400} height={300}>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label
              >
                {pieData.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </div>
        </div>

        {/* performer and target */}

        <div className="performertarget">
          <div className="topperformer">
            <p style={{color:"white"}}>Top 5 Performers</p>
            <table className="performer1">
              <thead>
                <tr>
                  <th>Agent Name</th>
                  <th>Audit Count</th>
                  <th>CQ%</th>
                  <th>Fatal Count</th>
                  <th>Fatal%</th>
                </tr>
              </thead>
              <tbody>
                {performers.length > 0 ? (
                  performers.map((performer, index) => (
                    <tr key={index}>
                      <td>{performer.User}</td>
                      <td>{performer.audit_count}</td>
                      <td>{performer.cq_percentage}%</td>
                      <td>{performer.fatal_count}</td>
                      <td style={{ backgroundColor: "#d2b4de" }}>
                        {performer.fatal_percentage}%
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5">No data available</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="targetwize">
            <div className="chart-box graph">
              <ResponsiveContainer width="100%" height={300}>
                <ComposedChart
                  data={barData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[0, 'auto']} tickCount={5} />
                  <Tooltip />
                  <Legend />

                  {/* FIX: Corrected "score" and "target" */}
                  <Bar dataKey="score" fill="#798e43" barSize={30} />
                  <Line
                    type="monotone"
                    dataKey="target"
                    stroke="#b765bd"
                    strokeWidth={2}
                    dot={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="potensialtop">
          <div className="potensial">
            <div className="left-section">

              <div className="escalation-box">
                <p>Potential Escalation - Sensitive Cases</p>
                <div className="escalation-item">
                  <span>Social Media</span>
                  <span className="count">
                    {escalationData.social_media_threat}
                  </span>
                </div>
                <div className="escalation-item">
                  <span>Consumer Court Threat</span>
                  <span className="count">
                    {escalationData.consumer_court_threat}
                  </span>
                </div>
                <div className="escalation-item">
                  <span>Potential Scam</span>
                  <span className="count">{escalationData.potential_scam}</span>
                </div>
              </div>


              <div className="chart-containernew">
                <p>Recent Escalation</p>
                <PieChart width={300} height={300}>
                  <Pie
                    data={pieData1}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#d32f2f"
                    dataKey="value"
                    label
                  >
                    {pieData1.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </div>
            </div>
          </div>
          <div className="topclass">
            <div className="right-section">
              <div className="one-12">
                <p>Top Negative Signals</p>
                <div className="negative-signals">
                  {topNegativeSignals.map((item, index) => (
                    <div key={index} className="signal-box">
                      <span>{item.category}</span>
                      <span className="count">{item.count}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="one-123">

                <p>Social Media and Consumer Court Threat</p>
                <div className={potentialEscalations.length > 0 ? "tablescrollbarnew" : "tablescrollbar"}>

                  <table className="negative-signals-table">
                    <thead>
                      <tr>
                        <th>Scenario</th>
                        <th>Scenario1</th>
                        <th>Sensitive Word</th>
                      </tr>
                    </thead>
                    <tbody>
                      {potentialEscalations.length > 0 ? (
                        potentialEscalations.map((item, index) => (
                          <tr key={index}>
                            <td>{item.scenario}</td>
                            <td>{item.scenario1}</td>
                            <td>{item.sensetive_word}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="3">No data available</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="one-124">
                <p>Top Negative Signals</p>
                <div className={negativeData.length > 0 ? "tablescrollbarnew" : "tablescrollbar"}>
                  <table className="negative-signals-table">
                    <thead>
                      <tr>
                        <th>Scenario</th>
                        <th>Scenario1</th>
                        <th>Sensitive Words</th>
                      </tr>
                    </thead>
                    <tbody>
                      {negativeData.length > 0 ? (
                        negativeData.map((item, index) => (
                          <tr key={index}>
                            <td>{item.scenario}</td>
                            <td>{item.scenario1}</td>
                            <td>{item.sensetive_word}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="3">No data available</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>


            </div>
          </div>
        </div>

        <div className="social-media">
          <div className="section-box" style={{display:"none"}}>
            <h5>Social Media and Consumer Court Threat</h5>
            <div className="section-content">
              <div className="alert-box setalertbox">
                {rawComplaintData.length > 0 ? (
                  rawComplaintData.map((item, index) => (
                    <p key={index}>
                      <b>
                        {new Date(item.date).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                        })}
                      </b>{" "}
                      - Scenario: {item.scenario} ({item.sub_scenario}) -
                      Customer mentioned "{item.sensitive_word}".
                    </p>
                  ))
                ) : (
                  <p>No alerts available.</p>
                )}
              </div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Call Date</th>
                    <th>Social Media</th>
                    <th>Consumer Court</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {complaintData.length > 0 ? (
                    complaintData.map((item, index) => (
                      <tr key={index}>
                        <td>
                          {new Date(item.date).toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                          })}
                        </td>
                        <td>{item.social_media_threat}</td>
                        <td>{item.consumer_court_threat}</td>
                        <td>{item.total}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4">No data available</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div className="partialscan">
          <div className="section-box">
            <h5>Potential Scam</h5>
            <div className="section-content">
              <div className="alert-box">
                <p>
                  <b>Feb 10</b> - Lead ID (987654) - Customer reported
                  fraudulent activity.
                </p>
                <p>
                  <b>Feb 09</b> - Lead ID (456789) - Suspicious transaction
                  flagged.
                </p>
              </div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Call Date</th>
                    <th>System Manipulation</th>
                    <th>Financial Fraud</th>
                    <th>Collusion</th>
                    <th>Policy Communication</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Feb 10, 2025</td>
                    <td>2</td>
                    <td>1</td>
                    <td>0</td>
                    <td>1</td>
                    <td>4</td>
                  </tr>
                  <tr>
                    <td>Feb 09, 2025</td>
                    <td>0</td>
                    <td>1</td>
                    <td>1</td>
                    <td>0</td>
                    <td>2</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="topnegative">
          <div className="section">
            <div className="alerts">
              <h5>Top Negative Signals</h5>
              <div className="setscroll">
                {negativeData.length > 0 ? (
                  negativeData.map((item, index) => (
                    <div key={index} className="alert-box">
                      {item.sensetive_word} (Lead ID: {item.lead_id}) -{" "}
                      {item.call_date}
                    </div>
                  ))
                ) : (
                  <div className="alert-box">No alerts available</div>
                )}
              </div>
            </div>
          </div>

          <div className="chart-box1">
            <h5>Month Wise</h5>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthWiseData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Frustration" stackId="a" fill="#FF7F50" />
                <Bar dataKey="Threat" stackId="a" fill="#1E90FF" />
                <Bar dataKey="Slang" stackId="a" fill="#32CD32" />
                <Bar dataKey="Abuse" stackId="a" fill="#8B0000" />
                <Bar dataKey="Sarcasm" stackId="a" fill="#FF1493" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-box2">
            <h5>Last 2 Days</h5>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={lastTwoDaysData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Frustration" stackId="a" fill="#FF7F50" />
                <Bar dataKey="Threat" stackId="a" fill="#1E90FF" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="Competitordiv">
          <div className="competitor-table">
            <h5>Competitor Analysis</h5>
            <table>
              <thead>
                <tr>
                  <th>Competitor</th>
                  <th>Count</th>
                </tr>
              </thead>
              <tbody>
                {competitorData.map((competitor, index) => (
                  <tr key={index}>
                    <td>{competitor.Competitor_Name}</td>
                    <td>{competitor.Count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="section">
            <div className="chart-container-ana">
              <Doughnut data={doughnutChartData} />
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

export default Analysis;





