import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./dashboard.css";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { Check, Info } from "lucide-react";
import {
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import Layout from "./layout";
import "./layout.css";
import { BASE_URL } from "./components/config";
import axios from "axios";

const Dashboard = () => {
  const navigate = useNavigate();
  const [startDate, setStartDate] = useState(new Date().toISOString().split("T")[0]);
  const [endDate, setEndDate] = useState(new Date().toISOString().split("T")[0]);
  const [dateOption, setDateOption] = useState("Today");
  const [isCustom, setIsCustom] = useState(false);
  const [usagePieData, setUsagePieData] = useState([]);
  const firstname = localStorage.getItem("username");
  const username = firstname ? firstname.split(" ")[0] : "";
  const user_id = localStorage.getItem("id");
  const [totalMinutes, setTotalMinutes] = useState("00.00");
  const [dateRangeMinutes, setDateRangeMinutes] = useState("00.00");

  const handleLogout = () => {
    localStorage.removeItem("token");
    sessionStorage.removeItem("user");
    navigate("/");
  };

  const handleNavigation = (path) => {
    navigate(path);
  };

  const handleSubmit = async () => {


  try {
    const response = await axios.post(`${BASE_URL}/calculate_limit_date/`, {
      from_date: startDate,   // assuming these are already Date objects or strings like "2024-04-01"
      to_date: endDate,
      user_id: user_id,
    });

    const dateRangeUsed = parseFloat(response.data.total_minutes) || 0;
    const totalLimit = 30.0;
    const remaining = Math.max(totalLimit - dateRangeUsed, 0).toFixed(2);


    setUsagePieData([
      { name: "Used", value: dateRangeUsed },
      { name: "Remaining", value: parseFloat(remaining) },
    ]);

    setDateRangeMinutes(response.data.total_minutes);
  } catch (error) {
    console.error("Error in handleSubmit:", error);
  }

    // try {
    //   console.log("Fetching data for:", startDate, "to", endDate);

    //   const response = await fetch(`${BASE_URL}/get-audio-stats/`, {
    //     method: "POST",
    //     headers: {
    //       "Content-Type": "application/json",
    //     },
    //     body: JSON.stringify({
    //       from_date: startDate,
    //       to_date: endDate,
    //       user_id: user_id,
    //     }),
    //   });

    //   if (!response.ok) {
    //     throw new Error(`Failed to fetch data. Status: ${response.status}`);
    //   }

    //   const result = await response.json();

    //   if (result.status === "success") {
    //     console.log("Submit Response:", result.data);

    //     let totalUsed = 0;
    //     let totalRemaining = 0;

    //     result.data.forEach((item) => {
    //       totalUsed += item.used || 0;
    //       totalRemaining += item.remaining || 0;
    //     });



    //     setUsagePieData([
    //       { name: "Used", value: totalUsed },
    //       { name: "Remaining", value: totalRemaining },
    //     ]);

    //     setTotalMinutes(totalUsed.toFixed(2));
    //   } else {
    //     console.error("API Error:", result);
    //   }
    // } catch (error) {
    //   console.error("Error fetching submit data:", error);
    // }
  };

  const handleDateChange = (date, type) => {
    if (!date) return;

    const formattedDate = date.toISOString().split("T")[0];
    if (type === "start") setStartDate(formattedDate);
    else setEndDate(formattedDate);
  };

  const handleDateOptionChange = (event) => {
    const option = event.target.value;
    setDateOption(option);
    setIsCustom(option === "Custom");

    let today = new Date();
    let newStartDate = today;
    let newEndDate = today;

    if (option === "Today") {
      newStartDate = new Date();
      newEndDate = new Date();
    } else if (option === "Yesterday") {
      newStartDate = new Date();
      newStartDate.setDate(today.getDate() - 1);
      newEndDate = new Date();
    } else if (option === "Week") {
      newStartDate = new Date();
      newStartDate.setDate(today.getDate() - 7);
      newEndDate = new Date();
    } else if (option === "Month") {
      newStartDate = new Date();
      newStartDate.setMonth(today.getMonth() - 1);
      newEndDate = new Date();
    }

    setStartDate(newStartDate.toISOString().split("T")[0]);
    setEndDate(newEndDate.toISOString().split("T")[0]);
  };

  useEffect(() => {
  if (!user_id) return;

  const fetchData = async () => {
    try {
      const today = new Date().toISOString().split("T")[0];

      // First API (all time)
      const response = await axios.get(`${BASE_URL}/calculate_limit/`, {
        params: { user_id },
      });
      const totalUsed = parseFloat(response.data.total_minutes);
      setTotalMinutes(response.data.total_minutes);

      // Second API (date range)
      const responseDate = await axios.post(`${BASE_URL}/calculate_limit_date/`, {
        from_date: startDate || today,
        to_date: endDate || today,
        user_id,
      });
      const dateRangeUsed = parseFloat(responseDate.data.total_minutes);
      const totalLimit = 30.0;
      const remaining = Math.max(totalLimit - dateRangeUsed, 0).toFixed(2);

      setUsagePieData([
        { name: "Used", value: dateRangeUsed },
        { name: "Remaining", value: parseFloat(remaining) },
      ]);
    } catch (error) {
      console.error("Error fetching minutes:", error);
    }
  };

  fetchData();
}, [user_id]);




  return (
    <Layout heading="Your Transcription & Analysis Hub!">
      <div className="flex-container">
        <div className="upgrade-con">
          <h6 style={{ fontFamily: "Arial" }}>
            Upgrade now for unlimited transcriptions! Your current monthly data extraction limit is{" "}
            <span style={{ fontWeight: "bold" }}>30 minutes</span>, and you've already processed a total of{" "}
            <span style={{ fontWeight: "bold" }}> {totalMinutes} minutes. </span>
          </h6>
          <button className="upgrade-button">Upgrade to Pro</button>
          <button className="transcription-button" onClick={() => navigate("/Recordings")}>
            New Transcription
          </button>
        </div>

        <div className="main-content new123">
          <h1 className="new">Recording Transcription</h1>
          <p title="Transcribe Recording"> <Check size={16} className="icon"/>Transcribe Recording</p>
          <p title="Identify sales conversion roadblocks."><Check size={16} className="icon" /> Sales Performance Analysis </p>
          <p title="Get a comprehensive analysis of call quality based on key performance parameters and insights for improvement."><Check size={16} className="icon" /> Quality Assurance Audit </p>
          <p title="Gain customizable insights on potential fraud, escalations, and key trends based on your recordings. Tailored to your business needs"><Check size={16} className="icon" /> Smart Insights </p>
          <p title="Automatically categorize calls based on client requirements, eliminating manual errors and saving valuable time."><Check size={16} className="icon" /> Intelligent Auto-Tagging </p>
          
        </div>
        

        <div className="main-content new12">
          <h1 className="new">Addon’s API</h1>
          <button className="actionclick" onClick={() => console.log("Transcribe clicked")}>Transcribe</button>
          <button className="actionclick" onClick={() => console.log("Upload clicked")}>Upload</button>
          <button className="actionclick" onClick={() => console.log("Insights clicked")}>Insights</button>
        </div>

        <div className="main-content new1">
          <h1 className="new">Learn</h1>
          <button className="actionclick-learn" onClick={() => navigate("/upload-help")}>How to Upload</button>
          <button className="actionclick-learn" onClick={() => navigate("/api-help")}>API Usage</button>
          <button className="actionclick-learn" onClick={() => console.log("Analysis link")}>Analysis Insights</button>
        </div>

        <div className="activity-section activity">
          <h4>Usage Activity</h4>
          <select className="predate1" value={dateOption} onChange={handleDateOptionChange}>
            <option>Today</option>
            <option>Yesterday</option>
            <option>Week</option>
            <option>Month</option>
            <option>Custom</option>
          </select>

          <h4>Start Date</h4>
          <DatePicker
            className="datepic"
            selected={new Date(startDate)}
            onChange={(date) => handleDateChange(date, "start")}
            readOnly={!isCustom}
            dateFormat="yyyy-MM-dd"
            portalId="root"
          />

          <h4>End Date</h4>
          <DatePicker
            className="datepic"
            selected={new Date(endDate)}
            onChange={(date) => handleDateChange(date, "end")}
            readOnly={!isCustom}
            dateFormat="yyyy-MM-dd"
            portalId="root"
          />

          <button className="submit" onClick={handleSubmit}>
            Submit
          </button>
        </div>

        <div className="notifi">
          <h1 className="new">Notifications</h1>
          <p>We’re actively working on powerful updates to enhance your experience:</p>
          <ul style={{ paddingLeft: "20px", lineHeight: "1.8" }}>
            <li>A new workflow optimization feature is set to launch next month.</li>
            <li>System upgrades are underway to boost speed, accuracy, and usability.</li>
            <li>AI-powered enhancements will deliver deeper insights and smarter automation.</li>
            <li>We're also building advanced capabilities to support your evolving needs.</li>
          </ul>
          <p>Stay tuned — exciting changes are just around the corner! </p>
        </div>


        {usagePieData.length > 0 && (
          <div className="range-chart">
            <h1 className="r-text">Usage Charts</h1>
            <PieChart width={570} height={300} >
              <Pie
                data={usagePieData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={90}
                fill="#8884d8"
                dataKey="value"

                label={({ name, value }) => `${name}: ${value} mins`}


              >
                {usagePieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={index === 0 ? "#2196F3" : "#4CAF50"} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value, name) => [`${value} mins`, name]}
              />
              <Legend />
            </PieChart>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Dashboard;
