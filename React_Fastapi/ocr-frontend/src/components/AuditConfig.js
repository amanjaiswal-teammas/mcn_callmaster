import React, { useEffect, useState } from "react";
import Layout from "../layout";
import { BASE_URL } from "./config";
import "./AuditConfig.css";

export default function AuditConfig() {
  const [configs, setConfigs] = useState([]);
  const [agents, setAgents] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [filteredAgents, setFilteredAgents] = useState([]);

  const [form, setForm] = useState({
    client_id: "",
    agent_users: [],
    min_call_duration: "",
    max_call_duration: "",
    audit_call_count_per_agent: "",
    time_from: "",
    time_to: "",
    call_type: "inbound",
    total_audit_call_count: "",
    dialer_server_ip: ""
  });

  const [editId, setEditId] = useState(null);

  // ✅ Fetch companies + agents
  useEffect(() => {
    fetch(`${BASE_URL}/call-master/active-data`)
      .then(res => res.json())
      .then(data => {
          setCompanies(data);

          // flatten all agents from companies
          const allAgents = data.flatMap(c => c.agents || []);
          setAgents(allAgents);
      });

    fetchConfigs();
  }, []);

  const fetchConfigs = () => {
    fetch(`${BASE_URL}/call-master/audit-config`)
      .then(res => res.json())
      .then(data => setConfigs(data));
  };

  // ✅ Handle form change
  const handleChange = (e) => {
      const { name, value } = e.target;

      setForm({ ...form, [name]: value });

      if (name === "client_id") {
        const selectedCompany = companies.find(
          c => String(c.company_id) === value
        );

        setFilteredAgents(selectedCompany?.agents || []);
        setForm(prev => ({ ...prev, agent_users: [] }));
      }
  };

  // ✅ Multi-select agents
  const handleAgentSelect = (e) => {
    const selected = Array.from(e.target.selectedOptions, o => o.value);
    setForm({ ...form, agent_users: selected });
  };

  // ✅ Submit (Create/Update)
  const handleSubmit = async () => {
      try {
        const payload = {
          ...form,
          client_id: Number(form.client_id),
          agent_users: form.agent_users.join(",")
        };

        const url = editId
          ? `${BASE_URL}/call-master/audit-config/${editId}`
          : `${BASE_URL}/call-master/audit-config`;

        const method = editId ? "PUT" : "POST";

        const res = await fetch(url, {
          method,
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("API failed");

        resetForm();
        fetchConfigs();

      } catch (err) {
        console.error(err);
        alert("Something went wrong");
      }
  };

  const resetForm = () => {
    setForm({
      client_id: "",
      agent_users: [],
      min_call_duration: "",
      max_call_duration: "",
      audit_call_count_per_agent: "",
      time_from: "",
      time_to: "",
      call_type: "inbound",
      total_audit_call_count: "",
      dialer_server_ip: ""
    });

    setFilteredAgents([]);
    setEditId(null);
  };

  // ✅ Edit
  const handleEdit = (item) => {
      setEditId(item.id);

      const agentList = item.agent_users
        ? item.agent_users.split(",")
        : [];

      const selectedCompany = companies.find(
        c => c.company_id === item.client_id
      );

      setFilteredAgents(selectedCompany?.agents || []);

      setForm({
        ...item,
        agent_users: agentList
      });
  };

  const remainingCount =
      (Number(form.total_audit_call_count) || 0) -
      (Number(form.audit_call_count_per_agent) || 0) *
        form.agent_users.length;

  return (
    <Layout heading="Audit Config Management">
      <div className="audit-container">

        {/* 🔹 FORM */}
        <div className="form-card">
          <h3>{editId ? "Update Config" : "Create Config"}</h3>

          <div className="grid-2">

            {/* Company */}
            <div>
              <label>Company</label>
              <select name="client_id" value={form.client_id} onChange={handleChange}>
                <option value="">Select Company</option>
                {companies.map(c => (
                  <option key={c.company_id} value={c.company_id}>
                    {c.company_name}
                  </option>
                ))}
              </select>
            </div>

            {/* Call Type */}
            <div>
              <label>Call Type</label>
              <select name="call_type" value={form.call_type} onChange={handleChange}>
                <option value="inbound">Inbound</option>
                <option value="outbound">Outbound</option>
              </select>
            </div>

            {/* Agents */}
            <div className="full-width">
              <label>Select Agents</label>
              <select key={form.client_id} multiple value={form.agent_users} onChange={handleAgentSelect}>
                {filteredAgents.length === 0 ? (
                    <option disabled>No agents available</option>
                  ) : (
                    filteredAgents.map(a => (
                      <option key={a.username} value={a.username}>
                        {a.displayname}
                      </option>
                    ))
                )}
              </select>

              {/* Selected Agents Preview */}
              <div className="tag-container">
                {form.agent_users.map(a => (
                  <span key={a} className="tag">{a}</span>
                ))}
              </div>
            </div>

            {/* Duration */}
            <div>
              <label>Min Duration (in seconds)</label>
              <input type="number" name="min_call_duration"
                value={form.min_call_duration} onChange={handleChange} />
            </div>

            <div>
              <label>Max Duration (in seconds)</label>
              <input type="number" name="max_call_duration"
                value={form.max_call_duration} onChange={handleChange} />
            </div>

            {/* Audit Config */}
            <div>
              <label>Audit Calls / Agent</label>
              <input type="number" name="audit_call_count_per_agent"
                value={form.audit_call_count_per_agent}
                onChange={handleChange} />
            </div>

            <div>
              <label>Total Audit Calls</label>
              <input type="number" name="total_audit_call_count"
                value={form.total_audit_call_count}
                onChange={handleChange} />
            </div>

            {/* ⏱ Remaining Count */}
            <div className="remaining-box full-width">
              Remaining Audit Calls:
              <b style={{ color: remainingCount < 0 ? "red" : "green" }}>
                {remainingCount}
              </b>
            </div>

            {/* Time */}
            <div>
              <label>Time From</label>
              <input type="time" name="time_from" value={form.time_from} onChange={handleChange} />
            </div>

            <div>
              <label>Time To</label>
              <input type="time" name="time_to" value={form.time_to} onChange={handleChange} />
            </div>

            {/* IP */}
            <div className="full-width">
              <label>Dialer Server IP</label>
              <input type="text" name="dialer_server_ip"
                value={form.dialer_server_ip}
                onChange={handleChange} />
            </div>

          </div>

          <div className="btn-group">
            <button className="primary-btn" onClick={handleSubmit}>
              {editId ? "Update" : "Create"}
            </button>
            <button onClick={resetForm} className="cancel-btn">Reset</button>
          </div>
        </div>

        {/* 🔹 TABLE */}
        <div className="table-card">
          <h3>Audit Config List</h3>

          <table>
            <thead>
              <tr>
                <th>Company</th>
                <th>Agents</th>
                <th>Duration</th>
                <th>Time</th>
                <th>Type</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {configs.map(c => {
                const company = companies.find(x => x.company_id === c.client_id);

                return (
                  <tr key={c.id}>
                    <td>{company?.company_name}</td>

                    <td>
                      {c.agent_users?.split(",").map(a => (
                        <span key={a} className="tag small">{a}</span>
                      ))}
                    </td>

                    <td>{c.min_call_duration} - {c.max_call_duration}</td>

                    <td>{c.time_from} - {c.time_to}</td>

                    <td>
                      <span className={`badge ${c.call_type}`}>
                        {c.call_type}
                      </span>
                    </td>

                    <td>
                      <button className="edit-btn" onClick={() => handleEdit(c)}>
                        Edit
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

        </div>
      </div>
    </Layout>
  );
}