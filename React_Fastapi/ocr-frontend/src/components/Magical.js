
import React, { useState } from "react";
import Layout from "../layout"; // Import layout component
import "../layout.css"; // Import styles
import "./Magical.css";


export default function Magical() {
  // const [loading, setLoading] = useState(true);
  const [startDate, setStartDate] = useState(new Date().toISOString().split("T")[0]);
  const [endDate, setEndDate] = useState(new Date().toISOString().split("T")[0]);










  // if (loading) {
  //   return (
  //     <div className="zigzag-container">
  //       <div className="bar"></div>
  //       <div className="bar"></div>
  //       <div className="bar"></div>
  //       <div className="bar"></div>
  //       <div className="bar"></div>
  //     </div>
  //   );
  // }

  return (
    <Layout heading="Title to be decided">
      <div className="dashboard-container">
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
              <input type="submit" class="setsubmitbtn" value="Submit" />
            </label>
          </div>
        </div>

        {/* <h4>Today's Magical Scripts</h4> */}
        {/* Main Flowchart */}
        <div className="flowchart">
          <div className="op-con">
            <div className="flow-box">Magical OP </div>
            <div className="connector"></div>
            <div className="flow-box-middile">Hello, good morning/afternoon/evening</div>
            <div className="connector"></div>
            {/* <div className="connectorver"></div> */}
            {/* <div className="connector-top"></div>
            <div className="connector-down"></div> */}
            {/* <div className="connectorver"></div> */}

            <div className="right-call-end">

              <div className="flow-box">Call End</div><br></br>
              <div className="flow-box">Sucess Rate</div>

            </div>
          </div>

          <div className="connectorver"></div>
          <div className="op-con">
            <div className="flow-box">Magical CSP</div>
            <div className="connector"></div>
            <div className="flow-box-middile">Sir/Ma'am, ye feedback call hai...</div>
            <div className="connector"></div>
            {/* <div className="connectorver"></div> */}

            <div className="right-call-end">
              <div className="flow-box">Call End</div><br></br>
              <div className="flow-box">Sucess Rate</div>

            </div>
          </div>

          <div className="connectorver"></div>
          <div className="op-con">
            <div className="flow-box">Magical Offer</div>
            <div className="connector"></div>
            <div className="flow-box-middile">100ml x 3 Perfume Bottles for Rs. 999</div>
            <div className="connector"></div>
            {/* <div className="connectorver"></div> */}

            <div className="right-call-end">
              <div className="flow-box">Call End</div><br></br>
              <div className="flow-box">Sucess Rate</div>

            </div>
          </div>

          <div className="connectorver"></div>
          <div className="connector-res"></div>
          <div className="connectorver1"></div>
          <div className="connectorver2"></div>
          <div className="connectorver3"></div>
          <div className="connectorver4"></div>


          {/* Four response paths */}
          <div className="responses">
            <div className="response">
              <div className="box-response">Not Interested in Perfumes (41%)</div>
              <div className="connectorver"></div>
              <div className="sub-box">Gifting Angle - Perfect for Someone Else</div>
              <div className="bottom-end">
                <div className="call-end ">Call End</div>
                <div className="call-end ">Sale Done (7%)</div>
              </div>
            </div>

            <div className="response">
              <div className="box-response">Overstock/No Need for More (33%)</div>
              <div className="connectorver"></div>
              <div className="sub-box">Exclusive offer for valued customers</div>
              <div className="bottom-end">
                <div className="call-end ">Call End</div>
                <div className="call-end ">Sale Done (7%)</div>
              </div>
            </div>

            <div className="response">
              <div className="box-response">Negative Product Feedback (10%)</div>
              <div className="connectorver"></div>
              <div className="sub-box">Offering long-lasting fragrances</div>
              <div className="bottom-end">
                <div className="call-end ">Call End</div>
                <div className="call-end ">Sale Done (7%)</div>
              </div>
            </div>

            <div className="response">
              <div className="box-response">Product Quality Concerns (3%)</div>
              <div className="connectorver"></div>
              <div className="sub-box">Assuring better quality</div>
              <div className="bottom-end">
                <div className="call-end ">Call End</div>
                <div className="call-end ">Sale Done (7%)</div>
              </div>
            </div>
          </div>
        </div>
      </div>


    </Layout>
  );
}














