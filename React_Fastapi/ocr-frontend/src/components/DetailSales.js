import React, { useState, useEffect } from "react";
import Layout from "../layout"; // Import layout component
import "../layout.css"; // Import styles
import "./DetailSales.css";
import { BASE_URL } from "./config";

export default function DetailSales() {
  //loading code start===>
  const [loading, setLoading] = useState(true);
  const [loading1, setLoading1] = useState(false);
  const [startDate, setStartDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [endDate, setEndDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [callSummary, setCallSummary] = useState({});
  const [contactAnalysisData, setContactAnalysisData] = useState([]);
  const [contactData, setContactData] = useState([]);
  const [discountData, setdiscountData] = useState([]);
  

  useEffect(() => {
    setTimeout(() => {
      setLoading(false);
    }, 2000);
  }, []);

  const fetchSalesData = async () => {
    setLoading1(true);
    try {
      const clientId = localStorage.getItem("client_id");

      // Fetch Call Summary
      const summaryRes = await fetch(
        `${BASE_URL}/call_summary_sales?client_id=${clientId}&start_date=${startDate}&end_date=${endDate}`
      );
      if (!summaryRes.ok) throw new Error("Failed to fetch call summary");
      const summaryResult = await summaryRes.json();
      setCallSummary(summaryResult.call_summary || {});

      // Fetch Opening Pitch Analysis
      const opRes = await fetch(
        `${BASE_URL}/op_analysis_sales?client_id=${clientId}&start_date=${startDate}&end_date=${endDate}`
      );
      if (!opRes.ok) throw new Error("Failed to fetch OP analysis");
      const opResult = await opRes.json();
      setContactAnalysisData(opResult || []);

      const contactRes = await fetch(
        `${BASE_URL}/contact_analysis_sales?client_id=${clientId}&start_date=${startDate}&end_date=${endDate}`
      );
      if (!contactRes.ok) throw new Error("Failed to fetch OP analysis");
      const contactResult = await contactRes.json();
      setContactData(contactResult || []);

      const contdiscount = await fetch(
        `${BASE_URL}/discount_analysis_sales?client_id=${clientId}&start_date=${startDate}&end_date=${endDate}`
      );
      if (!contdiscount.ok) throw new Error("Failed to fetch OP analysis");
      const Resultdiscount = await contdiscount.json();
      setdiscountData(Resultdiscount || []);

    } catch (error) {
      console.error("Error fetching sales data:", error);
      setCallSummary({});
      setContactAnalysisData([]);
      setContactData([]);
      setdiscountData([]);
    } finally {
      setLoading1(false);
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
  //loading code end==>

  return (
    <Layout heading="Title to be decided">
      <div className={`dashboard-container ${loading ? "blurred" : ""}`}>
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
              <input
                type="submit"
                class="setsubmitbtn"
                value="Submit"
                onClick={fetchSalesData}
              />
            </label>
          </div>
        </div>

        <div className="metric-container">
          {/* CST Card */}
          <div className="metric-card green-met">
            <h3 style={{ fontSize: "16px" }}>CST</h3>
            <div className="metricschanges">
              <div style={{marginTop:"10px"}}>
                <b>{callSummary?.total_calls ?? 0}</b>
                <p>Total Calls</p>
              </div>
              <div style={{marginTop:"10px"}}>
                <b>{callSummary?.exclude_opening_rejected ?? 0}</b>
                <p>OPS</p>
              </div>
              <div style={{marginTop:"10px"}}>
                <b>{callSummary?.exclude_context_opening_rejected ?? 0}</b>
                <p>cps</p>
              </div>
              <div style={{marginTop:"10px"}}>
                <b>
                  {callSummary?.exclude_context_opening_offering_rejected ?? 0}
                </b>
                <p>Offer Success</p>
              </div>
              <div style={{marginTop:"10px"}}>
                <b>{callSummary?.sale_done_count ?? 0}</b>
                <p>Sale Done</p>
              </div>
              <div style={{marginTop:"10px"}}>
                <b>{callSummary?.sale_success_rate ?? 0}%</b>
                <p>Success Rate</p>
              </div>
            </div>
          </div>

          {/* CRT Card */}
          <div className="metric-card blue-met">
            <h3 style={{ fontSize: "16px" }}>CRT</h3>
            <div className="metricschanges">
              <div style={{marginTop:"10px"}}>
                <b>{callSummary?.include_opening_rejected ?? 0}</b>
                <p>OR</p>
              </div>
              <div style={{marginTop:"10px"}}>
                <b>{callSummary?.include_context_rejected ?? 0}</b>
                <p>CR</p>
              </div>
              <div style={{marginTop:"10px"}}>
                <b>{callSummary?.offering_rejected_count ?? 0}</b>
                <p>OPR</p>
              </div>
              <div style={{marginTop:"10px"}}>
                <b>{callSummary?.post_offer_rejected_count ?? 0}</b>
                <p>POR</p>
              </div>
              <div style={{marginTop:"10px"}}>
                <b>{callSummary?.failure_rate ?? 0}%</b>
                <p>Failure Rate</p>
              </div>
            </div>
          </div>
        </div>

        {/* OP Analysis Section */}
        <div className="sales-section" style={{height:"450px",overflowY:"auto"}}>
          <h2 className="sales-title">OP Analysis</h2>
          <h3 className="sales-subtitle">OP Category Wise Success</h3>
          <table className="sales-table">
            <thead>
              <tr>
                <th>Opening Pitch Category</th>
                <th>Total Calls</th>
                <th>OPS Count</th>
                <th>OPS%</th>
                <th>OR Count</th>
                <th>OR%</th>
                <th>Sale Count</th>
                <th>Conversion%</th>
              </tr>
            </thead>

            {contactAnalysisData && contactAnalysisData.length > 0 ? (
              <>
                <tbody>
                  {contactAnalysisData
                    .filter(
                      (row) => row["Opening Pitch Category"] !== "Grand Total"
                    )
                    .map((row, idx) => (
                      <tr key={idx}>
                        <td>{row["Opening Pitch Category"]}</td>
                        <td>{row["Total Calls"]}</td>
                        <td>{row["OPS Count"]}</td>
                        <td>{row["OPS%"]}%</td>
                        <td>{row["OR Count"]}</td>
                        <td>{row["OR%"]}%</td>
                        <td>{row["Sale Count"]}</td>
                        <td>{row["Conversion%"]}%</td>
                      </tr>
                    ))}
                </tbody>

                <tfoot>
                  {contactAnalysisData
                    .filter(
                      (row) => row["Opening Pitch Category"] === "Grand Total"
                    )
                    .map((total, idx) => (
                      <tr key={`contact-total-${idx}`}>
                        <td>Grand Total</td>
                        <td>{total["Total Calls"]}</td>
                        <td>{total["OPS Count"]}</td>
                        <td>{total["OPS%"]}%</td>
                        <td>{total["OR Count"]}</td>
                        <td>{total["OR%"]}%</td>
                        <td>{total["Sale Count"]}</td>
                        <td>{total["Conversion%"]}%</td>
                      </tr>
                    ))}
                </tfoot>
              </>
            ) : (
              <tbody>
                <tr>
                  <td
                    colSpan="8"
                    style={{ textAlign: "center", color: "#888" }}
                  >
                    No data available
                  </td>
                </tr>
              </tbody>
            )}
          </table>
        </div>

        {/* Context Setting Analysis */}
        <div className="sales-section" style={{height:"450px",overflowY:"auto"}}>
          <h3 className="sales-subtitle">Context Setting Analysis</h3>
          <table className="sales-table">
            <thead>
              <tr>
                <th>Contact Pitch Category</th>
                <th>Total Calls</th>
                <th>OPS Count</th>
                <th>OPS%</th>
                <th>OR Count</th>
                <th>OR%</th>
                <th>Sale Count</th>
                <th>Conversion%</th>
              </tr>
            </thead>
            {contactData.length > 0 ? (
              <>
                <tbody>
                  {contactData
                    .filter(
                      (row) => row["Contact Pitch Category"] !== "Grand Total"
                    )
                    .map((row, idx) => (
                      <tr key={idx}>
                        <td>{row["Contact Pitch Category"]}</td>
                        <td>{row["Total Calls"]}</td>
                        <td>{row["OPS Count"]}</td>
                        <td>{row["OPS%"]}%</td>
                        <td>{row["OR Count"]}</td>
                        <td>{row["OR%"]}%</td>
                        <td>{row["Sale Count"]}</td>
                        <td>{row["Conversion%"]}%</td>
                      </tr>
                    ))}
                </tbody>
                <tfoot>
                  {contactData
                    .filter(
                      (row) => row["Contact Pitch Category"] === "Grand Total"
                    )
                    .map((total, idx) => (
                      <tr key={`contact-total-${idx}`}>
                        <td>Grand Total</td>
                        <td>{total["Total Calls"]}</td>
                        <td>{total["OPS Count"]}</td>
                        <td>{total["OPS%"]}%</td>
                        <td>{total["OR Count"]}</td>
                        <td>{total["OR%"]}%</td>
                        <td>{total["Sale Count"]}</td>
                        <td>{total["Conversion%"]}%</td>
                      </tr>
                    ))}
                </tfoot>
              </>
            ) : (
              <tbody>
                <tr>
                  <td
                  colSpan="8"
                  style={{ textAlign: "center", color: "#888" }}
                  >
                    No data available
                  </td>
                </tr>
              </tbody>
            )}
          </table>
        </div>

        {/* Offered Pitch Analysis */}
        <div className="sales-section" style={{height:"450px",overflowY:"auto"}}>
          <h2 className="sales-title">Offered Pitch Analysis</h2>
          <table className="sales-table">
            <thead>
              <tr>
                <th>Discount Type</th>
                <th>Total Calls</th>
                <th>OPS Count</th>
                <th>OPS%</th>
                <th>OR Count</th>
                <th>OR%</th>
                <th>Sale Count</th>
                <th>Conversion%</th>
              </tr>
            </thead>
            {discountData.length > 0 ? (
              <>
                <tbody>
                  {discountData
                    .filter(
                      (row) => row["Discount Type"] !== "Grand Total"
                    )
                    .map((row, idx) => (
                      <tr key={idx}>
                        <td>{row["Discount Type"]}</td>
                        <td>{row["Total Calls"]}</td>
                        <td>{row["OPS Count"]}</td>
                        <td>{row["OPS%"]}%</td>
                        <td>{row["OR Count"]}</td>
                        <td>{row["OR%"]}%</td>
                        <td>{row["Sale Count"]}</td>
                        <td>{row["Conversion%"]}%</td>
                      </tr>
                    ))}
                </tbody>
                <tfoot>
                  {discountData
                    .filter(
                      (row) => row["Discount Type"] === "Grand Total"
                    )
                    .map((total, idx) => (
                      <tr key={`contact-total-${idx}`}>
                        <td>Grand Total</td>
                        <td>{total["Total Calls"]}</td>
                        <td>{total["OPS Count"]}</td>
                        <td>{total["OPS%"]}%</td>
                        <td>{total["OR Count"]}</td>
                        <td>{total["OR%"]}%</td>
                        <td>{total["Sale Count"]}</td>
                        <td>{total["Conversion%"]}%</td>
                      </tr>
                    ))}
                </tfoot>
              </>
            ) : (
              <tbody>
                <tr>
                  <td
                  colSpan="8"
                  style={{ textAlign: "center", color: "#888" }}
                  >
                    No data available
                  </td>
                </tr>
              </tbody>
            )}
          </table>
        </div>

        {/* Customer Objection Analysis */}
        <div className="sales-section">
          <h2 className="sales-title">Customer Objection Analysis</h2>
          <h3 className="sales-subtitle">POS Breakdown</h3>
          <table className="sales-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
      <tr>
        <th style={{ position: 'sticky', top: 0, zIndex: 1 }}>
          Main Objection
        </th>
        <th style={{ position: 'sticky', top: 0, zIndex: 1 }}>
          Total Count
        </th>
        <th style={{ position: 'sticky', top: 0, zIndex: 1 }}>
          Failed Rebuttal %
        </th>
        <th style={{ position: 'sticky', top: 0, zIndex: 1 }}>
          Failed Rebuttal
        </th>
        <th style={{ position: 'sticky', top: 0, zIndex: 1 }}>
          Successful Rebuttal %
        </th>
        <th style={{ position: 'sticky', top: 0, zIndex: 1 }}>
          Successful Rebuttal
        </th>
        <th style={{ position: 'sticky', top: 0, zIndex: 1 }}>
          Conversion %
        </th>
        <th style={{ position: 'sticky', top: 0, zIndex: 1 }}>
          data %
        </th>
      </tr>
    </thead>
            <tbody>
              <tr>
                <td>Not Interested in Perfumes</td>
                <td>Provide Other Product Variety</td>
                <td className="greenclr">390</td>
                <td className="red-cell">96%</td>
                <td>375</td>
                <td className="green-cell">4%</td>
                <td>15</td>
                <td className="green-cell">4%</td>
              </tr>

              <tr>
              <td>Price Too High</td>
              <td>Offer Discounts</td>
              <td className="greenclr">420</td>
              <td className="red-cell">89%</td>
              <td>400</td>
              <td className="green-cell">6%</td>
              <td>20</td>
              <td className="green-cell">5%</td>
            </tr>
            <tr>
              <td>Product Not Long-Lasting</td>
              <td>Improve Product Quality</td>
              <td className="greenclr">350</td>
              <td className="red-cell">82%</td>
              <td>320</td>
              <td className="green-cell">10%</td>
              <td>30</td>
              <td className="green-cell">8%</td>
            </tr>
            <tr>
              <td>Customer Service Delay</td>
              <td>Faster Support Response</td>
              <td className="greenclr">275</td>
              <td className="red-cell">91%</td>
              <td>250</td>
              <td className="green-cell">6%</td>
              <td>25</td>
              <td className="green-cell">3%</td>
            </tr>
            <tr>
              <td>Delivery Takes Too Long</td>
              <td>Speed Up Logistics</td>
              <td className="greenclr">310</td>
              <td className="red-cell">85%</td>
              <td>280</td>
              <td className="green-cell">10%</td>
              <td>30</td>
              <td className="green-cell">5%</td>
            </tr>
            <tr>
              <td>Packaging Not Attractive</td>
              <td>Enhance Product Design</td>
              <td className="greenclr">198</td>
              <td className="red-cell">78%</td>
              <td>180</td>
              <td className="green-cell">12%</td>
              <td>18</td>
              <td className="green-cell">10%</td>
            </tr>

            </tbody>
          </table>
        </div>

        {/* POS Breakdown */}
        <div className="sales-section">
          <h3 className="sales-subtitle">POS Subcategory Breakdown</h3>
          <table className="sales-table">
            <thead>
              <tr>
                <th>Objection Subcategory</th>
                <th>Objection Count</th>
                <th>Failed Rebuttal %</th>
                <th>Failed Rebuttal</th>
                <th>Successful Rebuttal %</th>
                <th>Successful Rebuttal</th>
                <th>Conversion %</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Already has too many perfumes</td>
                <td className="greenclr">1,180</td>
                <td className="red-cell">94%</td>
                <td>1,108</td>
                <td className="green-cell">6%</td>
                <td>72</td>
                <td className="green-cell">6%</td>
              </tr>

              <tr>
              <td>Prefers Natural Scents</td>
              <td className="greenclr">980</td>
              <td className="red-cell">91%</td>
              <td>892</td>
              <td className="green-cell">9%</td>
              <td>88</td>
              <td className="green-cell">9%</td>
            </tr>
            <tr>
              <td>Allergic to Strong Fragrances</td>
              <td className="greenclr">765</td>
              <td className="red-cell">87%</td>
              <td>665</td>
              <td className="green-cell">13%</td>
              <td>100</td>
              <td className="green-cell">13%</td>
            </tr>
            <tr>
              <td>Uses Only Specific Brands</td>
              <td className="greenclr">1,050</td>
              <td className="red-cell">92%</td>
              <td>966</td>
              <td className="green-cell">8%</td>
              <td>84</td>
              <td className="green-cell">8%</td>
            </tr>
            <tr>
              <td>Dislikes Online Shopping</td>
              <td className="greenclr">640</td>
              <td className="red-cell">88%</td>
              <td>563</td>
              <td className="green-cell">12%</td>
              <td>77</td>
              <td className="green-cell">12%</td>
            </tr>
            <tr>
              <td>Worried About Authenticity</td>
              <td className="greenclr">710</td>
              <td className="red-cell">90%</td>
              <td>639</td>
              <td className="green-cell">10%</td>
              <td>71</td>
              <td className="green-cell">10%</td>
            </tr>

            </tbody>
          </table>
        </div>

        {/* Rebuttal Breakdown */}
        <div className="sales-section">
          <h3 className="sales-subtitle">Rebuttal Breakdown</h3>
          <table className="sales-table">
            <thead>
              <tr>
                <th>Agent Rebuttal Pitch</th>
                <th>Objection Count</th>
                <th>Failed Rebuttal %</th>
                <th>Failed Rebuttal</th>
                <th>Successful Rebuttal %</th>
                <th>Successful Rebuttal</th>
                <th>Conversion %</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Old Pitch</td>
                <td className="greenclr">1,742</td>
                <td className="red-cell">91%</td>
                <td>1,591</td>
                <td className="green-cell">9%</td>
                <td>151</td>
                <td className="green-cell">9%</td>
              </tr>

              <tr>
              <td>Wrong Timing</td>
              <td className="greenclr">1,215</td>
              <td className="red-cell">89%</td>
              <td>1,082</td>
              <td className="green-cell">11%</td>
              <td>133</td>
              <td className="green-cell">11%</td>
            </tr>
            <tr>
              <td>Repeated Call</td>
              <td className="greenclr">980</td>
              <td className="red-cell">92%</td>
              <td>902</td>
              <td className="green-cell">8%</td>
              <td>78</td>
              <td className="green-cell">8%</td>
            </tr>
            <tr>
              <td>Language Barrier</td>
              <td className="greenclr">870</td>
              <td className="red-cell">88%</td>
              <td>766</td>
              <td className="green-cell">12%</td>
              <td>104</td>
              <td className="green-cell">12%</td>
            </tr>
            <tr>
              <td>Didn't Understand Offer</td>
              <td className="greenclr">1,050</td>
              <td className="red-cell">90%</td>
              <td>945</td>
              <td className="green-cell">10%</td>
              <td>105</td>
              <td className="green-cell">10%</td>
            </tr>
            <tr>
              <td>Pitch Too Long</td>
              <td className="greenclr">1,320</td>
              <td className="red-cell">87%</td>
              <td>1,148</td>
              <td className="green-cell">13%</td>
              <td>172</td>
              <td className="green-cell">13%</td>
            </tr>

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
}
