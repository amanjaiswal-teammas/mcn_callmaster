import React, { useState,useEffect } from "react";
import Layout from "../layout";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import axios from "axios";
import { BASE_URL } from "./config";

const barrierColors = {
  low: "#3b82f6",     // blue
  medium: "#f97316",  // orange
  high: "#ef4444"     // red
};


const cardStyle = {
  backgroundColor: "#1f2937",
  borderRadius: "16px",
  padding: "16px",
  color: "white",
  boxShadow: "0 4px 12px rgba(0, 0, 0, 0.2)",
};

const gridStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
  gap: "16px",
};

const titleStyle = {
  fontSize: "18px",
  fontWeight: "600",
  marginBottom: "8px",
};

const sectionStyle = {
  backgroundColor: "#f9fafb",
  padding: "10px",
  borderRadius: "8px",
};

const Insight = () => {
  const [startDate, setStartDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [endDate, setEndDate] = useState(
    new Date().toISOString().split("T")[0]
  );

  const [ptpData, setPtpData] = useState([]);
  const [intentData, setIntentData] = useState([]);
  const [rootCauseData, setRootCauseData] = useState([]);
  const [data, setData] = useState([]);
  const [alertData, setAlertData] = useState([]);
  const [disputeData, setDisputeData] = useState([]);
  const [reasons, setReasons] = useState([]);
  const [behaviorData, setBehaviorData] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [funnelData, setFunnelData] = useState([]);

  const [loading1, setLoading1] = useState(false);




//  const data1 = [
//    { name: "Call 1", Calm: 40, Angry: 20 },
//    { name: "Call 2", Calm: 50, Angry: 30 },
//    { name: "Call 3", Calm: 45, Angry: 35 },
//    { name: "Call 4", Calm: 60, Angry: 25 },
//    { name: "Call 5", Calm: 55, Angry: 40 },
//  ];



  const ptpDataDispute = [
    { label: "Positive", value: 10, color: "#3b82f6" },
    { label: "Negative", value: 10, color: "#f97316" },
    { label: "Critical", value: 5, color: "#c7cf1a" },
    { label: "yellow", value: 10, color: "#c39b12" },
  ];

const fetchPtpData = async () => {
setLoading1(true);
  // 🔹 Fetch PTP Sentiment Distribution
  try {
    const sentimentResponse = await axios.post(`${BASE_URL}/dashboard3/ptp-sentiment-distribution`, {
      start_date: startDate,
      end_date: endDate,
      agent_name: null,
      team: null,
      region: null,
      campaign: null,
      min_confidence_score: 0,
      disposition: null,
    });

    const sentimentMap = {
      positive: { color: "#3b82f6", emoji: "🔵" },
      neutral: { color: "#a855f7", emoji: "🟣" },
      hesitant: { color: "#10b981", emoji: "🟢" },
      negative: { color: "#facc15", emoji: "🟡" },
      critical: { color: "#ef4444", emoji: "🔴" },
    };


    const formattedPtpData = sentimentResponse.data.map((item) => {
      const key = item.sentiment.toLowerCase();
      return {
        label: item.sentiment,
        value: item.count,
        color: sentimentMap[key]?.color || "#888",
        emoji: sentimentMap[key]?.emoji || "⚪",
      };
    });

    setPtpData(formattedPtpData);
  } catch (error) {
    console.error("Error fetching PTP sentiment data:", error);
    setPtpData([]);
  }

  // 🔹 Fetch PTP Intent Classification
  try {
    const intentResponse = await axios.post(`${BASE_URL}/dashboard3/ptp-intent-classification`, {
      start_date: startDate,
      end_date: endDate,
      agent_name: null,
      team: null,
      region: null,
      campaign: null,
      min_confidence_score: null,
      disposition: null,
    });

    setIntentData(intentResponse.data);
  } catch (error) {
    console.error("Error fetching intent classification:", error);
    setIntentData([]);
  }

  // 🔹 Fetch PTP Root Cause Detection
  try {
    const rootCauseResponse = await axios.post(`${BASE_URL}/dashboard3/ptp-root-cause-detection`, {
      start_date: startDate,
      end_date: endDate,
      agent_name: null,
      team: null,
      region: null,
      campaign: null,
      min_confidence_score: 0,
      disposition: null,
    });

    setRootCauseData(rootCauseResponse.data);
  } catch (error) {
    console.error("Error fetching root cause data:", error);
    setRootCauseData([]);
  }

  // 🔹 Fetch Agent Forced PTP by Weekday
  try {
    const response = await axios.post(
      `${BASE_URL}/dashboard3/ptp-agent-forced-by-weekday`,
      {
        start_date: startDate,
        end_date: endDate,
        agent_name: "string",
        team: "string",
        region: "string",
        campaign: "string",
        min_confidence_score: 0,
        disposition: "string",
      }
    );

    // Map API days to short day names in correct order
    const dayOrder = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const dayMap = {
      Sunday: "Sun",
      Monday: "Mon",
      Tuesday: "Tue",
      Wednesday: "Wed",
      Thursday: "Thu",
      Friday: "Fri",
      Saturday: "Sat",
    };

    const formattedData = dayOrder.map((shortDay) => {
      // Find the API day name that corresponds to this short day
      const apiDay = Object.keys(dayMap).find((key) => dayMap[key] === shortDay);
      const dayData = response.data.find((d) => d.day === apiDay);

      return {
        name: shortDay,
        value: dayData ? dayData.forced_ptps : 0,
      };
    });

    setData(formattedData);
  } catch (error) {
    console.error("Error fetching agent forced PTP data:", error);
    setData([]);
  }


  try {
      const response = await axios.post(`${BASE_URL}/dashboard3/escalation-risk-alerts`, {
        start_date: startDate,
        end_date: endDate,
        agent_name: "string",
        team: "string",
        region: "string",
        campaign: "string",
        min_confidence_score: 0,
        disposition: "string",
      });

      const colorMap = {
        "I'll complain": "#11d6ed",
        "going to consumer court": "#facc15",
        "social media": "#c39b12",
      };

      const formatted = response.data.map((item) => ({
        label: item.phrase,
        value: item.percentage,
        color: colorMap[item.phrase] || "#9ca3af",
      }));

      setAlertData(formatted);
    } catch (error) {
      console.error("Error fetching escalation alerts:", error);
      setAlertData([]);
    }


  try {
    const response = await axios.post(`${BASE_URL}/dashboard3/dispute-management`, {
      start_date: startDate,
      end_date: endDate,
      agent_name: "string",
      team: "string",
      region: "string",
      campaign: "string",
      min_confidence_score: 0,
      disposition: "string"
    });

    const percentage = response.data.dispute_percentage || 0;

    const chartData = [
      { label: "Disputes", value: percentage, color: "#e11d48" },
      { label: "Non-Disputes", value: 100 - percentage, color: "#16a34a" },
    ];

    setDisputeData(chartData);
    setReasons(response.data.reasons || []);

  } catch (error) {
    console.error("Error fetching dispute data:", error);
    setDisputeData([]);
    setReasons([]);
  }


  try {
    const response = await axios.post(`${BASE_URL}/dashboard3/agent-behavior-monitoring`, {
      start_date: startDate,
      end_date: endDate,
      agent_name: "string",
      team: "string",
      region: "string",
      campaign: "string",
      min_confidence_score: 0,
      disposition: "string"
    });

    const colors = ["#11d6ed", "#f97316", "#c39b12", "#3b82f6"];

    const formattedData = response.data.map((item, index) => ({
      label: item.behavior,
      value: item.percentage,
      color: colors[index % colors.length],
    }));

    setBehaviorData(formattedData);
  } catch (error) {
    console.error("Error fetching Agent Behavior Monitoring:", error);
    setBehaviorData([]);
  }


      try {
        const response = await axios.post(
          `${BASE_URL}/dashboard3/emotional-sentiment-analysis`,
          {
            start_date: startDate,
            end_date: endDate,
            agent_name: "string",
            team: "string",
            region: "string",
            campaign: "string",
            min_confidence_score: 0,
            disposition: "string",
          }
        );

        // Example: pretend the API returns multiple calls with emotions
        // You must replace this with real API data or adjust API backend if needed
        const apiResponse = response.data.timeline_trend_distribution;

        // Simulate dynamic calls if your API doesn't provide grouped data yet
        // Here, just an example for demonstration:
        const simulatedApiResponse = [
          {
            call: "Call 1",
            emotions: { Calm: 40, Angry: 20, Frustrated: 10, Resigned: 5 },
          },
          {
            call: "Call 2",
            emotions: { Calm: 50, Angry: 30, Frustrated: 20, Resigned: 10 },
          },
          {
            call: "Call 3",
            emotions: { Calm: 45, Angry: 35, Frustrated: 15, Resigned: 8 },
          },
        ];

        // Transform data dynamically
        const chartData = simulatedApiResponse.map(({ call, emotions }) => ({
          name: call,
          ...emotions,
        }));

        setChartData(chartData);
      } catch (error) {
        console.error("Error fetching emotional sentiment data:", error);
        setChartData([]);
      }


    try {
      const response = await axios.post(`${BASE_URL}/dashboard3/collection-funnel-optimization`, {
        start_date: startDate,
        end_date: endDate,
        agent_name: "string",
        team: "string",
        region: "string",
        campaign: "string",
        min_confidence_score: 0,
        disposition: "string"
      });

      setFunnelData(response.data.stages || []);
    } catch (error) {
      console.error("Failed to load collection funnel data", error);
      setFunnelData([]);
    }
     finally {
      setLoading1(false);
    }

};




  return (
    <Layout>
    <div className={` ${loading1 ? "blurred" : ""}`}>
      <div
        style={{
          backgroundColor: "#0f172a",
          minHeight: "100vh",
          padding: "16px",
        }}
      >
        <h4
          style={{
            fontSize: "20px",
            fontWeight: "600",
            color: "white",
            marginBottom: "16px",
          }}
        >
          AI Collections Analysis Dashboard
        </h4>

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

        <div style={gridStyle}>
          <Card title="Promise to Pay (PTP) Analysis">
            {ptpData.length === 0 || ptpData.every((item) => item.value === 0) ? (
              <div style={{ textAlign: "center", color: "#9ca3af", padding: "16px" }}>
                No data available
              </div>
            ) : (
              <>
                <PieChart data={ptpData} />
                <div
                  style={{ marginTop: "8px", fontSize: "14px", color: "#d1d5db" }}
                >
                  {ptpData.map((item, index) => {
                    const total = ptpData.reduce((sum, i) => sum + i.value, 0);
                    const percentage = ((item.value / total) * 100).toFixed(1);
                    return (
                      <p key={index}>
                        {item.emoji} {item.label} - {percentage}%
                      </p>
                    );
                  })}
                </div>
              </>
            )}
          </Card>

          <Card title="Intent Classification">
  <div style={{ maxWidth: "420px" }}>
    {intentData.length === 0 || intentData.every((item) => item.count === 0) ? (
      <div style={{ textAlign: "center", color: "#9ca3af", padding: "16px" }}>
        No data available
      </div>
    ) : (
      intentData.map((item, index) => {
        const total = intentData.reduce((sum, i) => sum + i.count, 0);
        const percent = total > 0 ? ((item.count / total) * 100).toFixed(1) : 0;

        const colorMap = {
          "Willing but Delayed": "#c39b12",
          "Unwilling": "#e74c3c",
          "Can't Pay": "#facc15",
        };

        return (
          <BarLabel
            key={index}
            label={item.intent}
            percent={percent}
            color={colorMap[item.intent] || "#6b7280"} // fallback gray
          />
        );
      })
    )}
  </div>
</Card>


          <Card title="Root Cause Detection">
  <div style={{ maxWidth: "420px" }}>
    {(() => {
      // Create a map of actual counts from API
      const countMap = {};
      rootCauseData.forEach((item) => {
        countMap[item.root_cause?.toLowerCase().trim()] = item.count;
      });

      // Define default causes
      const causes = [
        { label: "Cash Flow Issues", key: "cash flow issues", color: "#3b82f6" },
        { label: "Job Loss", key: "job loss", color: "#c39b12" },
        { label: "Dispute", key: "dispute", color: "#f97316" },
        { label: "Other", key: "other", color: "#f97316" },
      ];

      // Compute total count
      const total = causes.reduce((sum, cause) => sum + (countMap[cause.key] || 0), 0);

      // ✅ If no data available, show message
      if (total === 0) {
        return (
          <div style={{ textAlign: "center", color: "#9ca3af", padding: "16px" }}>
            No data available
          </div>
        );
      }

      // Render causes
      return causes.map((cause, index) => {
        const count = countMap[cause.key] || 0;
        const percent = total ? ((count / total) * 100).toFixed(1) : 0;

        return (
          <BarLabel
            key={index}
            label={cause.label}
            percent={percent}
            color={cause.color}
          />
        );
      });
    })()}
  </div>
</Card>






          <Card title="Detect agent-forced PTPs">
            <AgentForcedPTPChart />
          </Card>

          <Card title="Escalation Risk Alerts">
  {alertData.length === 0 ? (
    <div style={{ textAlign: "center", color: "#9ca3af", padding: "16px" }}>
      No data available
    </div>
  ) : (
    <>
      {alertData.map((item, index) => (
        <BarLabel
          key={index}
          label={item.label}
          percent={item.value}
          color={item.color}
        />
      ))}


    </>
  )}
</Card>


          <Card title="Dispute Management">
  {disputeData.length === 0 ? (
    <div style={{ textAlign: "center", color: "#9ca3af", padding: "16px" }}>
      No data available
    </div>
  ) : (
    <>
      <PieChart data={disputeData} />
      <ul style={{ fontSize: "14px", color: "#d1d5db", marginTop: "8px" }}>
        {reasons.map((item, index) => (
          <li key={index}>{item.reason} ({item.count})</li>
        ))}
      </ul>
    </>
  )}
</Card>


          <Card title="Agent Behavior Monitoring">
  {behaviorData.length === 0 ? (
    <div style={{ textAlign: "center", color: "#9ca3af", padding: "16px" }}>
      No data available
    </div>
  ) : (
    <>
      {behaviorData.map((item, index) => (
        <BarLabel
          key={index}
          label={item.label}
          percent={item.value}
          color={item.color}
        />
      ))}
    </>
  )}
</Card>



          <Card title="Emotional & Sentiment Analysis">
      {chartData.length === 0 ? (
        <div style={{ textAlign: "center", color: "#9ca3af", padding: "16px" }}>
          No data available
        </div>
      ) : (
        <>
          <div style={{ width: "100%", height: "200px", marginTop: "16px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid stroke="#374151" strokeDasharray="3 3" />
                <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
                <YAxis stroke="#9ca3af" fontSize={12} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="Calm"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="Frustrated"
                  stroke="#facc15"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="Angry"
                  stroke="#ef4444"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="Resigned"
                  stroke="#9ca3af"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div
            style={{
              fontSize: "12px",
              marginTop: "8px",
              color: "#9ca3af",
              textAlign: "center",
            }}
          >
            Calm, Frustrated, Angry, Resigned
          </div>
        </>
      )}
    </Card>

          <Card title="Collection Funnel Optimization">
  {funnelData.length === 0 ? (
    <div style={{ textAlign: "center", color: "#9ca3af", padding: "16px" }}>
      No data available
    </div>
  ) : (
    <HeatmapStages stages={funnelData} />
  )}
</Card>

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

const Card = ({ title, children }) => (
  <div style={cardStyle}>
    <h2 style={titleStyle}>{title}</h2>
    {children}
  </div>
);

const BarLabel = ({ label, percent, color }) => {
  const [hover, setHover] = useState(false);

  return (
    <div
      style={{ marginBottom: "16px" }}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: "14px",
          color: "#d1d5db",
          marginBottom: "4px",
        }}
      >
        <span>{label}</span>
        {hover && <span>{percent}%</span>}
      </div>
      <div
        style={{
          width: "100%",
          height: "24px",
          backgroundColor: "#374151",
          borderRadius: "12px",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${percent}%`,
            height: "100%",
            backgroundColor: color,
            borderRadius: "12px 0 0 12px",
            transition: "width 0.3s",
          }}
        />
      </div>
    </div>
  );
};

const PieChart = ({ data }) => {
  const [hoveredIndex, setHoveredIndex] = useState(null);
  const total = data.reduce((sum, item) => sum + item.value, 0);

  const getCoordinatesForPercent = (percent) => {
    const x = Math.cos(2 * Math.PI * percent);
    const y = Math.sin(2 * Math.PI * percent);
    return [x, y];
  };

  let cumulativePercent = 0;

  return (
    <div
      style={{
        width: "160px",
        height: "160px",
        margin: "0 auto",
        position: "relative",
      }}
    >
      <svg
        width="160"
        height="160"
        viewBox="-1 -1 2 2"
        style={{ transform: "rotate(-90deg)" }}
      >
        {data.map((slice, index) => {
          const percent = slice.value / total;
          const [startX, startY] = getCoordinatesForPercent(cumulativePercent);
          cumulativePercent += percent;
          const [endX, endY] = getCoordinatesForPercent(cumulativePercent);
          const largeArcFlag = percent > 0.5 ? 1 : 0;

          const pathData = `
            M ${startX} ${startY}
            A 1 1 0 ${largeArcFlag} 1 ${endX} ${endY}
            L 0 0
          `;

          return (
            <path
              key={index}
              d={pathData}
              fill={slice.color}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
              style={{ cursor: "pointer" }}
            />
          );
        })}
      </svg>

      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          backgroundColor: "#1f2937",
          borderRadius: "50%",
          width: "80px",
          height: "80px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "white",
          fontWeight: "bold",
          fontSize: "14px",
          textAlign: "center",
        }}
      >
        {hoveredIndex !== null ? (
          <>
            <div>
              {data[hoveredIndex].label}
              <br />
              {((data[hoveredIndex].value / total) * 100).toFixed(1)}%
            </div>
          </>
        ) : (
          "100%"
        )}
      </div>
    </div>
  );
};

const AgentForcedPTPChart = ({ startDate, endDate }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.post(
          `${BASE_URL}/dashboard3/ptp-agent-forced-by-weekday`,
          {
            start_date: startDate,
            end_date: endDate,
            agent_name: "string",
            team: "string",
            region: "string",
            campaign: "string",
            min_confidence_score: 0,
            disposition: "string",
          }
        );

        // API returns something like:
        // [{ day: "Sunday", forced_ptps: 0 }, ...]

        // Map days to short names and structure data for recharts
        const dayOrder = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
        const dayMap = {
          Sunday: "Sun",
          Monday: "Mon",
          Tuesday: "Tue",
          Wednesday: "Wed",
          Thursday: "Thu",
          Friday: "Fri",
          Saturday: "Sat",
        };

        const formattedData = dayOrder.map((shortDay) => {
          // find data from API for this short day
          const apiDay = Object.keys(dayMap).find(
            (key) => dayMap[key] === shortDay
          );
          const dayData = response.data.find((d) => d.day === apiDay);

          return {
            name: shortDay,
            value: dayData ? dayData.forced_ptps : 0,
          };
        });

        setData(formattedData);
      } catch (error) {
        console.error("Error fetching agent forced PTP data:", error);
        setData([]);
      }
    };

    fetchData();
  }, [startDate, endDate]);

  return (
    <div style={{ width: "100%", height: "200px", marginTop: "16px" }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid stroke="#374151" strokeDasharray="3 3" />
          <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
          <YAxis stroke="#9ca3af" fontSize={12} />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#ef4444"
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};



const HeatmapStages = ({ stages }) => (
  <div
    style={{
      display: "grid",
      gridTemplateColumns: `repeat(${stages.length}, 1fr)`,
      gap: "8px",
      marginTop: "8px",
    }}
  >
    {stages.map((stage, i) => (
      <div
        key={i}
        style={{
          height: "60px",
          borderRadius: "6px",
          backgroundColor: barrierColors[stage.barrier] || "#9ca3af",
          color: "#fff",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "14px",
          fontWeight: "bold"
        }}
      >
        <div>{stage.name}</div>
        <div>{stage.value}%</div>
      </div>
    ))}
  </div>
);

export default Insight;