import React, { useState,useEffect } from "react";
import Layout from "../layout";
import "../layout.css";
import { BASE_URL } from "./config";
const contact_number = localStorage.getItem("contact_number");
const agent_no = `31${contact_number}`;




const sections = [
  { name: "Sales", icon: "📈", color: "#3b82f6" },
  { name: "Services", icon: "🛠️", color: "#10b981" },
  { name: "Collection", icon: "💳", color: "#f59e0b" },
];

const Calling = () => {
  const [selectedSection, setSelectedSection] = useState(null);
  const [phoneNumbers, setPhoneNumbers] = useState({
    Sales: "",
    Services: "",
    Collection: "",
  });
  const [callStatus, setCallStatus] = useState("");
//  const [callVar, setCallVar] = useState(null);

  const [auditData, setAuditData] = useState({});
  const [transcribeData, setTranscribeData] = useState("");
   const [leadid, setLeadid] = useState("");

const handleCall = () => {
  const contact_number = localStorage.getItem("contact_number");
  const param1 = phoneNumbers[selectedSection];
  const param3 = selectedSection;

  if (!param1 || !contact_number || !param3) {
    alert("Missing required information.");
    return;
  }

  const url = `${BASE_URL}/click2dial?param1=${encodeURIComponent(
    param1
  )}&param2=${encodeURIComponent(contact_number)}&param3=${encodeURIComponent(
    param3
  )}`;

  fetch(url)
    .then((response) => {
      if (!response.ok) throw new Error("API call failed");
      return response.json();
    })
    .then((data) => {
      console.log("API call success:", data);
      setCallStatus("Call in progress.");
//      setCallVar(data.data.var)
    })
    .catch((error) => {
      console.error("API call error:", error);
    });

  setSelectedSection(null);
};


  const handleInputChange = (e) => {
    const value = e.target.value;
    if (/^\d{0,10}$/.test(value)) {
      setPhoneNumbers((prev) => ({
        ...prev,
        [selectedSection]: value,
      }));
    }
  };




useEffect(() => {
  if (!contact_number || !agent_no) return;

  let interval;

  const fetchData = async () => {
    try {
      await fetch(`${BASE_URL}/run_scheduler`);
      // Step 1: Fetch leadid
      const leadidRes = await fetch(`${BASE_URL}/get-leadid?contact_number=${contact_number}`);
      const leadidResult = await leadidRes.json();

      if (leadidResult.status === "success" && leadidResult.leadid) {
        setLeadid(leadidResult.leadid);

        // Step 2: Fetch audit and transcribe using the leadid
        const auditRes = await fetch(
          `${BASE_URL}/dashboard3/latest-transcribe-audit?agent_no=${agent_no}&leadid=${leadidResult.leadid}`
        );
        const auditResult = await auditRes.json();

        if (auditResult.status === "success") {
          setAuditData(auditResult.audit || {});
          setTranscribeData(auditResult.transcribe || "");
          console.log("Audit:", auditResult.audit);
          console.log("Transcribe:", auditResult.transcribe);
        } else {
          setAuditData({});
          setTranscribeData("");
        }
      } else {
        console.warn("Lead ID not found");
        setLeadid(null);
        setAuditData({});
        setTranscribeData("");
      }
    } catch (err) {
      console.error("Error fetching leadid/audit/transcribe:", err);
      setAuditData({});
      setTranscribeData("");
    }
  };

  fetchData(); // initial fetch
  interval = setInterval(fetchData, 5000);

  return () => clearInterval(interval);
}, [contact_number, agent_no]);


  return (
    <Layout heading="Smart Calling Center">


      <div
        style={{
          padding: "2rem",
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          backgroundColor: "rgb(117 129 145)",
        }}
      >

          {callStatus && (
              <div className="call-status" style={{ marginTop: "10px", color: "white" }}>
                {callStatus}
              </div>
            )}


        {/* Top Section Buttons */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "10rem",
            flexWrap: "wrap",
            marginBottom: "3rem",
          }}
        >



          {sections.map(({ name, icon, color }) => (
            <div
              key={name}
              onClick={() => setSelectedSection(name)}
              style={{
                background: "#fff",
                borderRadius: "1.5rem",
                boxShadow: "0 8px 24px rgba(0, 0, 0, 0.1)",
                padding: "1.5rem",
                textAlign: "center",
                cursor: "pointer",
                border: `2px solid ${color}`,
                width: "160px",
                transition: "transform 0.2s",
              }}
            >
              <div style={{ fontSize: "2.2rem", marginBottom: "0.5rem" }}>
                {icon}
              </div>
              <h3 style={{ fontSize: "1.2rem", fontWeight: "bold", color }}>
                {name}
              </h3>
              <p style={{ color: "#6b7280", fontSize: "0.9rem" }}>
                Tap to dial
              </p>
            </div>
          ))}
        </div>

        {/* Transcribe & Audit Section */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "2rem",
            flexWrap: "wrap",
            width: "100%",
          }}
        >
          {/* Transcribe */}
          <div
            style={{
              flex: "1 1 400px",
              backgroundColor: "rgba(255, 255, 255, 0.85)",
              borderRadius: "1.5rem",
              padding: "1.5rem",
              boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
              backdropFilter: "blur(6px)",
            }}
          >
            <h4
              style={{
                textAlign: "center",
                color: "#111827",
                marginBottom: "0.5rem",
              }}
            >
              📝 Transcribe
            </h4>
            <div
              style={{
                background: "#f9fafb",
                borderRadius: "0.75rem",
                padding: "1rem",
                minHeight: "250px",
                boxShadow: "inset 0 1px 4px rgba(0,0,0,0.1)",
                fontSize: "1.05rem",
                color: "#1e293b",
                height:"320px",
                overflowY: "auto",
              }}
            >
              {transcribeData || "No transcription available"}
            </div>
          </div>

          {/* Audit */}
          <div
            style={{
              flex: "1 1 400px",
              backgroundColor: "rgba(255, 255, 255, 0.85)",
              borderRadius: "1.5rem",
              padding: "1.5rem",
              boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
              backdropFilter: "blur(6px)",
            }}
          >
            <h4
              style={{
                textAlign: "center",
                color: "#111827",
                marginBottom: "0.5rem",
              }}
            >
              📝 Audit
            </h4>
            <div
              style={{
                background: "#f9fafb",
                borderRadius: "0.75rem",
                padding: "1rem",
                minHeight: "250px",
                boxShadow: "inset 0 1px 4px rgba(0,0,0,0.1)",
                fontSize: "1.05rem",
                color: "#1e293b",
                height:"320px",
                overflowY: "auto",
              }}
            >
             {Object.keys(auditData).length > 0
                ? renderKeyValue(auditData)
                : "No audit data available"}


            </div>
          </div>
        </div>

        {/* Call Modal */}
        {selectedSection && (
          <div
            onClick={() => setSelectedSection(null)}
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              height: "100%",
              width: "100%",
              background: "rgba(0, 0, 0, 0.5)",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              zIndex: 1000,
            }}
          >
            <div
              onClick={(e) => e.stopPropagation()}
              style={{
                background: "#ffffff",
                borderRadius: "1.5rem",
                padding: "2rem",
                width: "90%",
                maxWidth: "400px",
                maxHeight: "400px",
                overflowY: "auto",
                boxShadow: "0 12px 32px rgba(0, 0, 0, 0.2)",
                textAlign: "center",
              }}
            >
              <h2 style={{ marginBottom: "1rem", fontSize: "1.5rem" }}>
                📞 Call {selectedSection}
              </h2>
              <input
                type="tel"
                placeholder="Enter phone number"
                value={phoneNumbers[selectedSection]}
                onChange={handleInputChange}
                style={{
                  width: "100%",
                  padding: "0.75rem",
                  borderRadius: "1rem",
                  fontSize: "1rem",
                  border: "1px solid #94a3b8",
                  marginBottom: "1.2rem",
                }}
              />
              <button
                onClick={handleCall}
                style={{
                  background: "linear-gradient(to right, #22c55e, #16a34a)",
                  color: "#fff",
                  border: "none",
                  padding: "0.75rem 1.5rem",
                  borderRadius: "1rem",
                  fontSize: "1rem",
                  fontWeight: "bold",
                  cursor: "pointer",
                }}
              >
                Start Call
              </button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

const renderKeyValue = (data, indent = 0) => {
  if (typeof data !== "object" || data === null) {
    return <span>{String(data)}</span>;
  }

  return (
    <ul style={{ paddingLeft: `${indent + 12}px`, listStyle: "none" }}>
      {Object.entries(data).map(([key, value]) => (
        <li key={key} style={{ marginBottom: "4px" }}>
          {key}:{" "}
          {typeof value === "object" && value !== null ? (
            renderKeyValue(value, indent + 16)
          ) : (
            <span>{String(value)}</span>
          )}
        </li>
      ))}
    </ul>
  );
};


export default Calling;
