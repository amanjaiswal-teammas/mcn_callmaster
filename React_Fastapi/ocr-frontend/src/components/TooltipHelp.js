

import React from "react";
import "./TooltipHelp.css";

const TooltipHelp = ({ message }) => {
  return (
    <div className="tooltip-container">
      {/* <span className="tooltip-icon">ℹ️</span> */}
      <span className="tooltip-icon">🛈</span>
      <span className="tooltip-text">{message}</span>
    </div>
  );
};

export default TooltipHelp;
