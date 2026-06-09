import React, { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./MyProfile.css";

export default function MyProfile() {
  const navigate = useNavigate();

  const user = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem("user") || "{}");
    } catch {
      return {};
    }
  }, []);

  const [editing, setEditing] = useState(false);
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem("delphi-theme") === "dark"
  );
  const [emailNotif, setEmailNotif] = useState(true);
  const [twoFA, setTwoFA] = useState(false);

  const fullName = user.full_name || "User";
  const nameParts = fullName.split(" ");

  const [form, setForm] = useState({
    firstName: nameParts[0] || "",
    lastName: nameParts.slice(1).join(" "),
    email: user.email || "",
    phone: user.phone || "",
    company: user.company_name || "",
  });

  const initials = `${form.firstName?.[0] || ""}${form.lastName?.[0] || ""}`
    .toUpperCase();

  const joinedDate = user.created_at
    ? new Date(user.created_at).toLocaleDateString("en-US", {
        month: "long",
        year: "numeric",
      })
    : "2024";

  const plan = {
    name: "Pro",
    renewal: "Aug 1, 2026",
    campaigns: {
      used: 3,
      total: 20,
    },
    storage: {
      used: 1.2,
      total: 5,
    },
  };
  const [brands, setBrands] = useState([]);
  const [brandInput, setBrandInput] = useState("");

  const stats = {
    campaigns: 0,
    chats: 0,
    memberSince: joinedDate,
  };

  const updateField = (field, value) => {
    setForm((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const saveProfile = () => {
    const updatedUser = {
      ...user,
      full_name: `${form.firstName} ${form.lastName}`.trim(),
      phone: form.phone,
    };

    localStorage.setItem("user", JSON.stringify(updatedUser));
    setEditing(false);
  };

  const toggleDarkMode = (enabled) => {
    setDarkMode(enabled);

    if (enabled) {
      document.documentElement.setAttribute("data-theme", "dark");
      localStorage.setItem("delphi-theme", "dark");
    } else {
      document.documentElement.removeAttribute("data-theme");
      localStorage.setItem("delphi-theme", "light");
    }
  };

  const renderField = (
    label,
    value,
    editable = false,
    fieldName = ""
  ) => (
    <div className="mp-field">
      <label>{label}</label>

      {editing && editable ? (
        <input
          value={value}
          onChange={(e) =>
            updateField(fieldName, e.target.value)
          }
        />
      ) : (
        <div className="mp-field-value">{value || "—"}</div>
      )}
    </div>
  );

  return (
    <div className="mp-page">
      <div className="container-fluid" style={{ maxWidth: "1100px" }}>

        {/* Back Button */}
        <button
          className="btn btn-light border mb-4 d-flex align-items-center gap-2"
          onClick={() => navigate(-1)}
        >
          <i className="bi bi-arrow-left"></i>
          Back
        </button>

        {/* Header */}
        <div className="mp-header-card">
          <div className="mp-avatar-wrap">
            <div className="mp-avatar">{initials}</div>
          </div>

          <div className="mp-header-info">
            <h2 className="mp-header-name">{fullName}</h2>
            <p className="mp-header-email">{user.email}</p>

            <span className="mp-plan-badge">
              <i className="bi bi-patch-check-fill"></i>
              {plan.name} Plan
            </span>
          </div>

          <button
            className="mp-edit-btn"
            onClick={() =>
              editing ? saveProfile() : setEditing(true)
            }
          >
            <i
              className={`bi ${
                editing ? "bi-check-lg" : "bi-pencil"
              }`}
            />
            {editing ? "Save Changes" : "Edit Profile"}
          </button>
        </div>

        <div className="mp-grid">

          {/* Personal Information */}
          <div className="mp-card">
            <div className="mp-card-title">
              <span
                className="mp-card-title-icon"
                style={{
                  background: "#eff6ff",
                  color: "#1a56db",
                }}
              >
                <i className="bi bi-person-fill"></i>
              </span>
              Personal Information
            </div>

            <div className="mp-fields">

              <div className="mp-field-row">
                {renderField(
                  "First Name",
                  form.firstName,
                  true,
                  "firstName"
                )}

                {renderField(
                  "Last Name",
                  form.lastName,
                  true,
                  "lastName"
                )}
              </div>

              <div className="mp-field-row">
                {renderField("Email Address", form.email)}

                {renderField(
                  "Phone Number",
                  form.phone,
                  true,
                  "phone"
                )}
              </div>

              {renderField("Company", form.company)}
            </div>
          </div>

          {/* Activity Overview */}
          <div className="mp-card">
            <div className="mp-card-title">
              <span
                className="mp-card-title-icon"
                style={{
                  background: "#f0fdf4",
                  color: "#059669",
                }}
              >
                <i className="bi bi-activity"></i>
              </span>
              Activity Overview
            </div>

            <div className="mp-stats">

              <div className="mp-stat-card">
                <div className="mp-stat-value">
                  {stats.campaigns}
                </div>
                <div className="mp-stat-label">
                  Campaigns
                </div>
              </div>

              <div className="mp-stat-card">
                <div className="mp-stat-value">
                  {stats.chats}
                </div>
                <div className="mp-stat-label">
                  Chats
                </div>
              </div>

              <div className="mp-stat-card">
                <div className="mp-stat-value">
                  {stats.memberSince}
                </div>
                <div className="mp-stat-label">
                  Member Since
                </div>
              </div>

            </div>
          </div>

          {/* Plan & Usage */}
          <div className="mp-card">
            <div className="mp-card-title">
              <span
                className="mp-card-title-icon"
                style={{ background: "#fef9c3", color: "#d97706" }}
              >
                <i className="bi bi-lightning-charge-fill" />
              </span>
              Plan & Usage
            </div>

            <div className="mp-plan-row">
              <div>
                <div className="mp-plan-name">
                  {plan.name} Plan
                </div>

                <div className="mp-plan-renewal">
                  Renews on {plan.renewal}
                </div>
              </div>

              <button className="mp-manage-btn">
                Manage Subscription
              </button>
            </div>

            <div className="mp-usage">

              <div className="mp-usage-item">
                <div className="mp-usage-header">
                  <span>Campaigns</span>
                  <span>
                    {plan.campaigns.used}/
                    {plan.campaigns.total}
                  </span>
                </div>

                <div className="mp-bar-track">
                  <div
                    className="mp-bar-fill"
                    style={{
                      width: `${
                        (plan.campaigns.used /
                          plan.campaigns.total) *
                        100
                      }%`,
                    }}
                  />
                </div>
              </div>

              <div className="mp-usage-item">
                <div className="mp-usage-header">
                  <span>Storage</span>
                  <span>
                    {plan.storage.used} GB /
                    {plan.storage.total} GB
                  </span>
                </div>

                <div className="mp-bar-track">
                  <div
                    className="mp-bar-fill"
                    style={{
                      width: `${
                        (plan.storage.used /
                          plan.storage.total) *
                        100
                      }%`,
                    }}
                  />
                </div>
              </div>

            </div>
          </div>

            {/* Brands / Products / Services */}
            <div className="mp-card">
                <div className="mp-card-title">
                    <span className="mp-card-title-icon" style={{ background: "#eef2ff", color: "#4338ca" }}>
                        <i className="bi bi-box-seam"></i>
                    </span>
                    BRANDS / PRODUCTS / SERVICES
                    <button
                      className="mp-manage-btn mp-card-action-btn"
                      onClick={() => {
                        // placeholder for auto-detect feature
                        alert('Auto-detect from website not implemented yet');
                      }}
                    >
                      Auto-detect from website
                    </button>
                </div>

                <div className="mp-brands">
                    {brands.length === 0 && (
                        <div style={{ padding: '12px 18px', color: '#6b7280' }}>No brands yet. Add one below.</div>
                    )}

                    <div style={{ display: 'flex', gap: 8, padding: '12px 18px' }}>
                        <input
                            value={brandInput}
                            onChange={e => setBrandInput(e.target.value)}
                            placeholder="Add brand / product / model"
                            style={{ flex: 1, padding: '10px 12px', borderRadius: 8, border: '1px solid rgba(0,0,0,0.08)' }}
                        />
                        <button
                            className="mp-manage-btn"
                            onClick={() => {
                                const v = (brandInput || '').trim();
                                if (!v) return;
                                setBrands(b => [...b, v]);
                                setBrandInput('');
                            }}
                            style={{ height: 36 }}
                        >+ Add</button>
                    </div>

                    {brands.length > 0 && (
                        <div style={{ padding: '0 18px 12px', display: 'flex', flexDirection: 'column', gap: 8 }}>
                            {brands.map((b, i) => (
                                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 10px', borderRadius: 8, background: '#fff' }}>
                                    <div style={{ color: '#111827' }}>{b}</div>
                                    <button className="mp-manage-btn" onClick={() => setBrands(prev => prev.filter((_, idx) => idx !== i))}>Remove</button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

        </div>
      </div>
    </div>
  );
}