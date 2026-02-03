import React, { useState, useEffect } from "react";
import Layout from "../layout";
import "../layout.css";
import "./UserDashboardSelection.css";
import { BASE_URL } from "./config";

const UserDashboardSelection = () => {
    const users = ["user1@example.com", "user2@example.com", "user3@example.com"];
    const [dashboards, setDashboards] = useState([]);
    const [selectedUser, setSelectedUser] = useState("");
    const [selectedDashboards, setSelectedDashboards] = useState([]);
    const [expandedDashboards, setExpandedDashboards] = useState({ Service: false, Sales: false });

    useEffect(() => {
        fetch(`${BASE_URL}/menu`)
            .then((response) => response.json())
            .then((data) => {
                const allowedMenus = ["Home", "Recordings", "Transcription", "Prompt", "Settings", "API Key", "Service", "Sales"];
                const formattedDashboards = data
                    .filter(item => allowedMenus.includes(item.name))
                    .map((item) => ({
                        name: item.name,
                        subDashboards: item.submenu && (item.name === "Service" || item.name === "Sales") 
                            ? item.submenu.map(sub => sub.name) 
                            : []
                    }));
                setDashboards(formattedDashboards);
            })
            .catch((error) => console.error("Error fetching menu:", error));
    }, []);

    const toggleExpand = (dashboardName, e) => {
        e.stopPropagation();
        if (dashboardName === "Service" || dashboardName === "Sales") {
            setExpandedDashboards((prev) => ({
                ...prev,
                [dashboardName]: !prev[dashboardName]
            }));
        }
    };

    const handleDashboardChange = (dashboard) => {
        if (dashboard.subDashboards.length > 0) {
            const isAllSelected = dashboard.subDashboards.every(sub => selectedDashboards.includes(sub));
            setSelectedDashboards(prev =>
                isAllSelected ? prev.filter(d => !dashboard.subDashboards.includes(d)) : [...prev, ...dashboard.subDashboards]
            );
        } else {
            setSelectedDashboards(prev =>
                prev.includes(dashboard.name) ? prev.filter(d => d !== dashboard.name) : [...prev, dashboard.name]
            );
        }
    };

    const handleSubmit = () => {
        console.log("Selected User:", selectedUser);
        console.log("Selected Dashboards:", selectedDashboards);
    };

    return (
        <Layout heading="Title to be decided">
            <div className="user-maindashboard">
                <div className="db-con">
                    <div>
                        <span className="user-label">User Email:</span>
                        <select className="user-select" value={selectedUser} onChange={(e) => setSelectedUser(e.target.value)}>
                            <option value="">Select User</option>
                            {users.map((user) => (
                                <option key={user} value={user}>{user}</option>
                            ))}
                        </select>
                    </div>

                    <div className="us-scroller">
                        <h4 className="dashboard-title">Dashboards</h4>
                        {dashboards.map((dashboard) => (
                            <div key={dashboard.name} className="custom-checkbox">
                                <input
                                    type="checkbox"
                                    id={dashboard.name}
                                    checked={selectedDashboards.includes(dashboard.name)}
                                    onChange={() => handleDashboardChange(dashboard)}
                                />
                                <label htmlFor={dashboard.name} className="checkbox-label">
                                    {dashboard.name} {dashboard.subDashboards.length > 0 && (
                                        <span 
                                            onClick={(e) => toggleExpand(dashboard.name, e)} 
                                            style={{ cursor: "pointer", fontSize: "13px"}}
                                        >
                                            {expandedDashboards[dashboard.name] ? "▲" : "▼"}
                                        </span>
                                    )}
                                </label>

                                {dashboard.subDashboards.length > 0 && expandedDashboards[dashboard.name] && (
                                    <div className="sub-dashboard-container">
                                        {dashboard.subDashboards.map((subDashboard) => (
                                            <div key={subDashboard} className="custom-checkbox sub-checkbox">
                                                <input
                                                    type="checkbox"
                                                    id={subDashboard}
                                                    checked={selectedDashboards.includes(subDashboard)}
                                                    onChange={() => handleDashboardChange({ name: subDashboard, subDashboards: [] })}
                                                />
                                                <label htmlFor={subDashboard} className="checkbox-label">
                                                    {subDashboard}
                                                </label>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>

                    <div className="save1-btn" onClick={handleSubmit}>Save Selection</div>
                </div>
            </div>
        </Layout>
    );
};

export default UserDashboardSelection;