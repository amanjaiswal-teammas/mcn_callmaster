import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import Layout from "../layout";
import "../layout.css";
import "./Transcription.css";
import { BASE_URL } from "./config";
import axios from "axios";
import { Download } from 'lucide-react';


const Transcription = ({ onLogout }) => {
  const navigate = useNavigate();
  const [startDate, setStartDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [endDate, setEndDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [dateOption, setDateOption] = useState("Today");
  const [isCustom, setIsCustom] = useState(false);
  const [dateBy, setDateBy] = useState("Document Date");
  const [bucket, setBucket] = useState("Active");
  const [data, setData] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 6;
  const audioRef = useRef(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedTranscript, setSelectedTranscript] = useState("");
  const [selectedItems, setSelectedItems] = useState([]); // Store selected IDs
  const [selectAll, setSelectAll] = useState(false); // Track "Select All" state
  const [isEditing, setIsEditing] = useState(false);
  const [selectedAudioId, setSelectedAudioId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loading1, setLoading1] = useState(false);
  const Id = parseInt(localStorage.getItem("id"));


  const openModal = (transcript, id) => {
    setSelectedTranscript(transcript);
    setSelectedAudioId(id);
    setShowModal(true);
  };

  // const closeModal = () => {
  //   setShowModal(false);
  //   setSelectedTranscript("");
  // };
  const closeModal = () => {
    setShowModal(false);
    setSelectedTranscript("");
    setIsEditing(false); // <-- reset edit mode when closing
  };



  const firstname = localStorage.getItem("username");
  const username = firstname ? firstname.split(" ")[0] : "";

  const handleLogout = () => {
    localStorage.removeItem("token");
    sessionStorage.removeItem("user");
    onLogout();
    navigate("/");
  };

  useEffect(() => {
  setLoading(true);
  const fetchRecordings = async () => {
    try {
      const userId = Number(localStorage.getItem("id"));
      const response = await fetch(`${BASE_URL}/recordings/?user_id=${userId}`);
      const result = await response.json();
      setData(result);
      setTotalPages(Math.ceil(result.length / itemsPerPage));
    } catch (error) {
      console.error("Error fetching recordings:", error);
    } finally {
      setLoading(false);
    }
  };

  fetchRecordings();
}, []);


  useEffect(() => {
    setTotalPages(Math.ceil(data.length / itemsPerPage));
    setPage(1);// reset to page 1 on new data
  }, [data]);

  const nextPage = () => {
    if (page < totalPages) {
      setPage(page + 1);
    }
  };

  const prevPage = () => {
    if (page > 1) {
      setPage(page - 1);
    }
  };

  const startIndex = (page - 1) * itemsPerPage;
  // const currentItems = data.slice(startIndex, startIndex + itemsPerPage);
  const currentItems = Array.isArray(data)
    ? data.slice(startIndex, startIndex + itemsPerPage)
    : [];

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

  const handleView = async () => {
  setLoading1(true);
  const userId = Number(localStorage.getItem("id")); // Get user_id from localStorage

  console.log("Fetching data from", startDate, "to", endDate, "for user:", userId);

  try {
    const response = await fetch(
      `${BASE_URL}/recordings_datewise/?start_date=${startDate}&end_date=${endDate}&user_id=${userId}`
    );
    const result = await response.json();
    setData(result);
  } catch (error) {
    console.error("Error fetching filtered recordings:", error);
  } finally {
    setLoading1(false);
  }
};


  const handleCheckboxChange = (id) => {
    setSelectedItems((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  // Toggle "Select All" checkbox
  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedItems([]); // Uncheck all
    } else {
      setSelectedItems(currentItems.map((item) => item.id)); // Check all
    }
    setSelectAll(!selectAll);
  };

  const downloadFile = async (caseType) => {
    try {
      let requestBody = {};

      if (caseType === "selected") {
        requestBody = { ids: selectedItems };
      } else {
        requestBody = { ids: currentItems.map((item) => item.id) };
      }

      const response = await fetch(`${BASE_URL}/download_transcription/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) throw new Error("Failed to download file");

      // Convert response to Blob and trigger download
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "transcriptions.txt"; // Set download filename
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading file:", error);
    }
  };

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
      <div className={` ${loading ? "blurred" : ""}`}>
        <div className="dateboard">
          <div className="date-page1">
            <h1 className="word">Pre Set</h1>
            <select
              className="predate"
              value={dateOption}
              onChange={handleDateOptionChange} // Enable date pickers when "Custom" is selected
            >
              <option>Today</option>
              <option>Yesterday</option>
              <option>Week</option>
              <option>Month</option>
              <option>Custom</option>
            </select>

            <h1 className="word1">Start Date</h1>
            <DatePicker
              className="datepic1"
              selected={startDate}
              onChange={(date) => handleDateChange(date, "start")}
              disabled={!isCustom} // Enable only if "Custom" is selected
              dateFormat="yyyy-MM-dd"
              portalId="root"
            />

            <h1 className="word1">End Date</h1>
            <DatePicker
              className="datepic1"
              selected={endDate}
              onChange={(date) => handleDateChange(date, "end")}
              disabled={!isCustom}
              dateFormat="yyyy-MM-dd"
              portalId="root"
            />

            <h1 className="word">Date by</h1>
            <select
              className="predate"
              value={dateBy}
              onChange={(e) => setDateBy(e.target.value)}
            >
              <option>Document Date</option>
              <option>Created Date</option>
            </select>

            <h1 className="word">Bucket</h1>
            <select
              className="predate"
              value={bucket}
              onChange={(e) => setBucket(e.target.value)}
            >
              <option>Active</option>
              <option>Not Viewed</option>
              <option>Archived</option>
              <option>All</option>
            </select>

            <button
              className="view"
              // style={{ marginLeft: "10px", height: "30px" }}
              onClick={handleView}
            >
              View
            </button>
          </div>

          <div className="table-containers1">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>

                    <input
                      type="checkbox"
                      name="selectAll"
                      checked={selectAll}
                      onChange={handleSelectAll}
                      id="selectAll"
                      title="Select/Deselect All"
                    />

                  </th>

                  {/* <th>Preview</th> */}
                  <th>Recording Date</th>
                  <th>Recording File</th>
                  <th>Category</th>
                  <th>Language</th>
                  <th>Call Duration</th>
                  <th>Transcript</th>
                </tr>
              </thead>
              <tbody>
                {currentItems.map((item, index) => (
                  <tr key={index}>
                    <td>
                      <input
                        type="checkbox"
                        name="select"
                        value={item.id}
                        checked={selectedItems.includes(item.id)}
                        onChange={() => handleCheckboxChange(item.id)}
                        title="Select/Deselect All"
                      />
                    </td>
                    {/* <td>{item.preview}</td> */}
                    <td>{item.recordingDate}</td>
                    <td>
                      <audio className="audio-controls" controls>
                        <source
                          src={`/audio/${item.file}`}
                          type={
                            item.file.endsWith(".wav")
                              ? "audio/mpeg"
                              : "audio/wav"
                          }
                        />
                        Your browser does not support the audio element.
                      </audio>
                    </td>
                    <td>{item.category}</td>
                    <td>{item.language}</td>
                    <td>
                      {isNaN(Number(item.minutes)) || item.minutes === "N/A" ? (
                        "N/A"
                      ) : Number(item.minutes) < 1 ? (
                        `${Math.round(Number(item.minutes) * 60)} sec`
                      ) : (
                        `${item.minutes} min`
                      )}
                    </td>



                    <td>
                      <div className="transcript-short">
                        {item.Transcript.length > 50
                          ? item.Transcript.substring(0, 50) + "..."
                          : item.Transcript}
                      </div>
                      {item.Transcript.length > 50 && (
                        <button
                          className="show-more"
                          onClick={() => openModal(item.Transcript, item.id)}

                        >
                          Show More
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Modal */}
            {showModal && (
              <div className="modal-overlay" onClick={closeModal}>
                <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                  <span className="close-button" onClick={closeModal} title="Close">
                    &times;
                  </span>

                  <span
                    className="edit-pencil"
                    onClick={() => setIsEditing(true)}
                    title="Edit"
                  >
                    ✏️
                  </span>

                  <h4>Full Transcript</h4>

                  {isEditing ? (
                    <>
                      <textarea
                        className="transcript-textarea"
                        value={selectedTranscript}
                        onChange={(e) => setSelectedTranscript(e.target.value)}
                        rows={10}
                      />
                      <button
                        className="save-button"
                        onClick={async () => {
                          try {
                            await axios.put(`${BASE_URL}/update_transcript/`, {
                              audio_id: selectedAudioId, // make sure you store selected ID
                              transcript: selectedTranscript,
                            });
                            setIsEditing(false); // Exit edit mode after save
                            alert("Transcript saved successfully");
                          } catch (error) {
                            console.error("Error saving transcript:", error);
                          }
                        }}
                      >
                        Save
                      </button>
                    </>
                  ) : (
                    <p>{selectedTranscript}</p>
                  )}
                </div>
              </div>
            )}


            {currentItems.length > 0 && (
              <div style={{ width: "100%", gap: "6px" }}>
                {/* Download Buttons */}
                <button className=" down-all" onClick={() => downloadFile("all")}>
                  Download All
                </button>
                <button
                  className=" down-all"
                  onClick={() => downloadFile("selected")}
                  disabled={selectedItems.length === 0}
                >
                  <Download style={{ marginRight: "8px" }} />
                  Download Selected
                </button>
              </div>
            )}
          </div>

          {currentItems.length > 0 && (
            <div className="pagination">
              <button
                onClick={prevPage}
                disabled={page === 1}
                className="pagination-button"
              >
                Previous
              </button>
              <span className="page-info">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={nextPage}
                disabled={page === totalPages}
                className="pagination-button"
              >
                Next
              </button>
            </div>
          )}
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

export default Transcription;
