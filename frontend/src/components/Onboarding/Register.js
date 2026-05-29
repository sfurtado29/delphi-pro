import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_DOMAIN;

export default function Register() {
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        first_name:   "",
        last_name:    "",
        company_name: "",
        email:        "",
        password:     "",
        confirm_password: ""
    });

    const [errors,  setErrors]  = useState({});
    const [loading, setLoading] = useState(false);
    const [apiError, setApiError] = useState("");

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        setErrors({ ...errors, [e.target.name]: "" });
    };

    const validate = () => {
        const e = {};
        if (!formData.first_name)   e.first_name   = "First name is required";
        if (!formData.last_name)    e.last_name    = "Last name is required";
        if (!formData.company_name) e.company_name = "Company name is required";
        if (!formData.email)        e.email        = "Email is required";
        if (!formData.password)     e.password     = "Password is required";
        if (formData.password.length < 6) e.password = "Minimum 6 characters";
        if (formData.password !== formData.confirm_password)
            e.confirm_password = "Passwords do not match";
        setErrors(e);
        return Object.keys(e).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setApiError("");
        if (!validate()) return;

        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/auth/register`, {
                first_name:   formData.first_name,
                last_name:    formData.last_name,
                company_name: formData.company_name,
                email:        formData.email,
                password:     formData.password
            });

            // Redirect to OTP page with email
            navigate("/Otp", { state: { email: formData.email } });

        } catch (err) {
            setApiError(err.response?.data?.detail || "Registration failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="d-flex justify-content-center align-items-center min-vh-100 bg-light py-4">
            <div className="card shadow-lg border-0 rounded-4 p-4" style={{ maxWidth: "480px", width: "100%" }}>
                <div className="text-center mb-4">
                    <div
                        className="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center shadow-sm"
                        style={{ width: "60px", height: "60px" }}
                    >
                        <i className="bi bi-person-plus fs-3"></i>
                    </div>
                    <h3 className="mt-3 fw-bold">Create Account</h3>
                    <p className="text-muted small">Set up your Delphi AI account</p>
                </div>

                {apiError && <div className="alert alert-danger py-2">{apiError}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="row g-3">
                        <div className="col-md-6">
                            <label className="form-label fw-semibold">First Name</label>
                            <input
                                type="text"
                                name="first_name"
                                className={`form-control ${errors.first_name ? "is-invalid" : ""}`}
                                placeholder="John"
                                value={formData.first_name}
                                onChange={handleChange}
                            />
                            {errors.first_name && <div className="invalid-feedback">{errors.first_name}</div>}
                        </div>

                        <div className="col-md-6">
                            <label className="form-label fw-semibold">Last Name</label>
                            <input
                                type="text"
                                name="last_name"
                                className={`form-control ${errors.last_name ? "is-invalid" : ""}`}
                                placeholder="Doe"
                                value={formData.last_name}
                                onChange={handleChange}
                            />
                            {errors.last_name && <div className="invalid-feedback">{errors.last_name}</div>}
                        </div>

                        <div className="col-12">
                            <label className="form-label fw-semibold">Company Name</label>
                            <input
                                type="text"
                                name="company_name"
                                className={`form-control ${errors.company_name ? "is-invalid" : ""}`}
                                placeholder="XTS World"
                                value={formData.company_name}
                                onChange={handleChange}
                            />
                            {errors.company_name && <div className="invalid-feedback">{errors.company_name}</div>}
                        </div>

                        <div className="col-12">
                            <label className="form-label fw-semibold">Work Email</label>
                            <input
                                type="email"
                                name="email"
                                className={`form-control ${errors.email ? "is-invalid" : ""}`}
                                placeholder="john@company.com"
                                value={formData.email}
                                onChange={handleChange}
                            />
                            {errors.email && <div className="invalid-feedback">{errors.email}</div>}
                        </div>

                        <div className="col-12">
                            <label className="form-label fw-semibold">Password</label>
                            <input
                                type="password"
                                name="password"
                                className={`form-control ${errors.password ? "is-invalid" : ""}`}
                                placeholder="Min. 6 characters"
                                value={formData.password}
                                onChange={handleChange}
                            />
                            {errors.password && <div className="invalid-feedback">{errors.password}</div>}
                        </div>

                        <div className="col-12">
                            <label className="form-label fw-semibold">Confirm Password</label>
                            <input
                                type="password"
                                name="confirm_password"
                                className={`form-control ${errors.confirm_password ? "is-invalid" : ""}`}
                                placeholder="Re-enter password"
                                value={formData.confirm_password}
                                onChange={handleChange}
                            />
                            {errors.confirm_password && <div className="invalid-feedback">{errors.confirm_password}</div>}
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary w-100 mt-4 fw-semibold"
                        disabled={loading}
                    >
                        {loading
                            ? <span className="spinner-border spinner-border-sm me-2"></span>
                            : <i className="bi bi-check-circle me-2"></i>
                        }
                        {loading ? "Creating account..." : "Create Account & Send OTP"}
                    </button>
                </form>

                <div className="text-center mt-3">
                    <button
                        onClick={() => navigate("/")}
                        className="btn btn-link text-decoration-none small text-primary p-0"
                    >
                        Already have an account? Login
                    </button>
                </div>
            </div>
        </div>
    );
}