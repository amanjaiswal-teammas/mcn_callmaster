import React, { useState } from "react";
import Layout from "../layout"; // Import layout component
import "../layout.css"; // Import styles
import "./RawDown.css";
import { BASE_URL } from "./config";
import * as XLSX from "xlsx";
const RawDownload = () => {
  const [leadId, setLeadId] = useState("");
  const [data, setData] = useState([]);
  const [dataExcel, setDataExcel] = useState([]);

  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());
  const [loading, setLoading] = useState(false);

  const formatDate = (date) => {
    return date.toISOString().split("T")[0]; // Convert Date to YYYY-MM-DD
  };

  const fetchCallQualityDetails = async () => {
    if (!startDate || !endDate) {
      alert("Please select both Start and End dates.");
      return;
    }

    setLoading(true);

    try {
      const clientId = localStorage.getItem("client_id");
      const response = await fetch(
        `${BASE_URL}/call_quality_assessments?client_id=${clientId}&start_date=${formatDate(
          startDate
        )}&end_date=${formatDate(endDate)}`
      );
      if (!response.ok) throw new Error("Failed to fetch data");

      const result = await response.json();

      const formattedData = result.map((item) => ({
        clientId: item.ClientId,
        callId: item.id,
        callDate: item.CallDate.split("T")[0],
        startEpoch: item.start_epoch,
        endEpoch: item.end_epoch,
        mobileNo: item.MobileNo,
        leadId: item.lead_id,
        agentName: item.User,
        campaign: item.Campaign,
        callDuration: item.length_in_sec,
        callAnsweredWithin5Sec: item.call_answered_within_5_seconds ?? "N/A",
        customerConcernAcknowledged: item.customer_concern_acknowledged,
        professionalismMaintained: item.professionalism_maintained,
        assuranceOrAppreciation: item.assurance_or_appreciation_provided,
        pronunciationAndClarity: item.pronunciation_and_clarity,
        enthusiasmNoFumbling: item.enthusiasm_and_no_fumbling,
        activeListening: item.active_listening,
        politenessNoSarcasm: item.politeness_and_no_sarcasm,
        properGrammar: item.proper_grammar,
        accurateIssueProbing: item.accurate_issue_probing,
        properHoldProcedure: item.proper_hold_procedure,
        properTransferAndLanguage: item.proper_transfer_and_language,
        deadAirUnder10Sec: item.dead_air_under_10_seconds ?? "N/A",
        caseEscalatedCorrectly: item.case_escalated_correctly ?? "N/A",
        addressRecordedCompletely: item.address_recorded_completely,
        correctCompleteInfo: item.correct_and_complete_information,
        upsellingOrOffersSuggested: item.upselling_or_offers_suggested ?? "N/A",
        furtherAssistanceOffered: item.further_assistance_offered ?? "N/A",
        properCallClosure: item.proper_call_closure,
        totalScore: item.total_score,
        maxScore: item.max_score,
        qualityPercentage: item.quality_percentage,
        expressEmpathy: item.express_empathy,
        areasForImprovement: item.areas_for_improvement
          ? item.areas_for_improvement.length > 20
            ? item.areas_for_improvement.substring(0, 20) + "..."
            : item.areas_for_improvement
          : "None",
        topPositiveWords: item.top_positive_words || "N/A",
        topNegativeWords: item.top_negative_words || "N/A",
        agentEnglishCussCount: item.agent_english_cuss_count,
        agentHindiCussCount: item.agent_hindi_cuss_count,
        customerEnglishCussCount: item.customer_english_cuss_count,
        customerHindiCussCount: item.customer_hindi_cuss_count,
        scenario: item.scenario,
        scenario1: item.scenario1,
        scenario2: item.scenario2,
        scenario3: item.scenario3,
        competitorName: item.Competitor_Name || "N/A",
        sensitiveWord: item.sensetive_word,
        dataTheftOrMisuse: item.data_theft_or_misuse,
        unprofessionalBehavior: item.unprofessional_behavior,
        systemManipulation: item.system_manipulation,
        financialFraud: item.financial_fraud,
        escalationFailure: item.escalation_failure,
        collusion: item.collusion,
        policyCommunicationFailure: item.policy_communication_failure,
        fraudPotentialityPercentage:
          item.fraud_potentiality_percentage || "N/A",
        sensitiveWordContext: item.sensitive_word_context || "None",
        transcript: item.Transcribe_Text
          ? item.Transcribe_Text.length > 20
            ? item.Transcribe_Text.substring(0, 20) + "..."
            : item.Transcribe_Text
          : "No Transcript Available",
      }));

      const formattedDataexcel = result.map((item) => ({
        clientId: item.ClientId,
        callId: item.id,
        callDate: item.CallDate.split("T")[0],
        startEpoch: item.start_epoch,
        endEpoch: item.end_epoch,
        mobileNo: item.MobileNo,
        leadId: item.lead_id,
        agentName: item.User,
        campaign: item.Campaign,
        callDuration: item.length_in_sec,
        callAnsweredWithin5Sec: item.call_answered_within_5_seconds ?? "N/A",
        customerConcernAcknowledged: item.customer_concern_acknowledged,
        professionalismMaintained: item.professionalism_maintained,
        assuranceOrAppreciation: item.assurance_or_appreciation_provided,
        pronunciationAndClarity: item.pronunciation_and_clarity,
        enthusiasmNoFumbling: item.enthusiasm_and_no_fumbling,
        activeListening: item.active_listening,
        politenessNoSarcasm: item.politeness_and_no_sarcasm,
        properGrammar: item.proper_grammar,
        accurateIssueProbing: item.accurate_issue_probing,
        properHoldProcedure: item.proper_hold_procedure,
        properTransferAndLanguage: item.proper_transfer_and_language,
        deadAirUnder10Sec: item.dead_air_under_10_seconds ?? "N/A",
        caseEscalatedCorrectly: item.case_escalated_correctly ?? "N/A",
        addressRecordedCompletely: item.address_recorded_completely,
        correctCompleteInfo: item.correct_and_complete_information,
        upsellingOrOffersSuggested: item.upselling_or_offers_suggested ?? "N/A",
        furtherAssistanceOffered: item.further_assistance_offered ?? "N/A",
        properCallClosure: item.proper_call_closure,
        totalScore: item.total_score,
        maxScore: item.max_score,
        qualityPercentage: item.quality_percentage,
        expressEmpathy: item.express_empathy,
        areasForImprovement: item.areas_for_improvement || "None",
        topPositiveWords: item.top_positive_words || "N/A",
        topNegativeWords: item.top_negative_words || "N/A",
        agentEnglishCussCount: item.agent_english_cuss_count,
        agentHindiCussCount: item.agent_hindi_cuss_count,
        customerEnglishCussCount: item.customer_english_cuss_count,
        customerHindiCussCount: item.customer_hindi_cuss_count,
        scenario: item.scenario,
        scenario1: item.scenario1,
        scenario2: item.scenario2,
        scenario3: item.scenario3,
        competitorName: item.Competitor_Name || "N/A",
        sensitiveWord: item.sensetive_word,
        dataTheftOrMisuse: item.data_theft_or_misuse,
        unprofessionalBehavior: item.unprofessional_behavior,
        systemManipulation: item.system_manipulation,
        financialFraud: item.financial_fraud,
        escalationFailure: item.escalation_failure,
        collusion: item.collusion,
        policyCommunicationFailure: item.policy_communication_failure,
        fraudPotentialityPercentage:
          item.fraud_potentiality_percentage || "N/A",
        sensitiveWordContext: item.sensitive_word_context || "None",
        transcript: item.Transcribe_Text || "No Transcript Available",
      }));

      setData(formattedData);
      setDataExcel(formattedDataexcel);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const downloadExcel = (dataExcel) => {
    if (dataExcel.length === 0) {
      alert("No data available to export.");
      return;
    }

    const worksheet = XLSX.utils.json_to_sheet(dataExcel);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Call Data");

    XLSX.writeFile(workbook, "call_data.xlsx");
  };

  return (
    <Layout heading="Title to be decided">
      <div className="Down-dashboard">
        <header className="header">
          <h3>DialDesk</h3>
          <div className="setheaderdivdetails" style={{marginLeft:"260px"}}>
            <label>
              <input
                type="date"
                value={formatDate(startDate)}
                onChange={(e) => setStartDate(new Date(e.target.value))}
              />
            </label>
            <label>
              <input
                type="date"
                value={formatDate(endDate)}
                onChange={(e) => setEndDate(new Date(e.target.value))}
              />
            </label>
            <label>
              <input
                className="setsubmitbtn"
                value={"Submit"}
                readOnly
                onClick={fetchCallQualityDetails}
              />
            </label>
            <label>
            {data.length > 0 && (
            <input
              className="setsubmitbtn"
              onClick={() => downloadExcel(dataExcel)}
              value={"Excel Export"}
              readOnly
              style={{
                cursor:"pointer",
                width: "110px"
              }}
            />
             
          )}
            </label>
          </div>
        </header>

        {/* Content Wrapper */}
        <div
          className={`content-wrapper ${loading ? "blurred" : ""}`}
          style={{ overflowY: "auto", maxHeight: "630px" }}
        >

          {/* Table */}
          <table>
            <thead
              style={{
                position: "sticky",
                top: 0,
                backgroundColor: "#fff",
                zIndex: 2,
              }}
            >
              <tr>
                {data.length > 0 &&
                  Object.keys(data[0]).map((key) => <th key={key}>{key}</th>)}
              </tr>
            </thead>
            <tbody>
              {data.length > 0 ? (
                data.map((row, index) => (
                  <tr key={index}>
                    {Object.values(row).map((value, i) => (
                      <td key={i}>{value !== null ? value : "N/A"}</td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="100%" style={{ textAlign: "center" }}>
                    No data found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {loading && (
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

export default RawDownload;
