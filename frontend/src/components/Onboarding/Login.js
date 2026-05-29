import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = process.env.REACT_APP_API_DOMAIN;

function Login() {
    const [email,    setEmail]    = useState("");
    const [password, setPassword] = useState("");
    const [error,    setError]    = useState("");
    const [loading,  setLoading]  = useState(false);
    const [showPass, setShowPass] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError("");

        if (!email || !password) {
            setError("Email and password are required");
            return;
        }

        // Static Super Admin Bypass
        if (email === "admin@xtsworld.in" && password === "xts@123") {
            localStorage.setItem("user", JSON.stringify({
                email:     "superadmin@xdbs.in",
                full_name: "Sameer Datta",
                role_name: "super_admin",
                user_id:   0,
                role_id:   0
            }));
           navigate("/Intelligence", { replace: true });
            return;
        }

        setLoading(true);
        try {
            const res = await axios.post(`${API_BASE_URL}/auth/login`, {
                email,
                password
            });

            const user = res.data.user;
            localStorage.setItem("user", JSON.stringify(user));

            switch (user.role_name) {
                case "Admin":
                    navigate("/Intelligence", { replace: true });
                    break;
                default:
                   navigate("/Intelligence", { replace: true });
            }

        } catch (err) {
            const msg = err.response?.data?.detail || "Invalid email or password";
            // If email not verified redirect to OTP page
            if (msg.includes("not verified")) {
                navigate("/Otp", { state: { email } });
            } else {
                setError(msg);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="d-flex justify-content-center align-items-center vh-100 bg-light">
            <div
                className="card shadow-lg border-0 rounded-4 p-4"
                style={{ maxWidth: "420px", width: "100%" }}
            >
                <div className="text-center mb-4">
                    <div
                        className="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center shadow-sm"
                        style={{ width: "60px", height: "60px" }}
                    >
                        <i className="bi bi-person-lock fs-3"></i>
                    </div>
                    <h3 className="mt-3 fw-bold">Welcome Back</h3>
                    <p className="text-muted small">Sign in to continue to your dashboard</p>
                </div>

                {error && <div className="alert alert-danger py-2">{error}</div>}

                <form onSubmit={handleLogin}>
                    <div className="mb-3">
                        <label className="form-label fw-semibold">Email</label>
                        <div className="input-group">
                            <span className="input-group-text bg-light">
                                <i className="bi bi-envelope"></i>
                            </span>
                            <input
                                type="email"
                                className="form-control"
                                placeholder="Enter your email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                    </div>

                    <div className="mb-4">
                        <label className="form-label fw-semibold">Password</label>
                        <div className="input-group">
                            <span className="input-group-text bg-light">
                                <i className="bi bi-lock"></i>
                            </span>
                            <input
                                type={showPass ? "text" : "password"}
                                className="form-control"
                                placeholder="Enter your password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                            <button
                                type="button"
                                className="input-group-text bg-light border-start-0"
                                onClick={() => setShowPass(!showPass)}
                            >
                                <i className={`bi ${showPass ? "bi-eye-slash" : "bi-eye"}`}></i>
                            </button>
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary w-100 shadow-sm fw-semibold"
                        disabled={loading}
                    >
                        {loading
                            ? <span className="spinner-border spinner-border-sm me-2"></span>
                            : <i className="bi bi-box-arrow-in-right me-2"></i>
                        }
                        {loading ? "Signing in..." : "Login"}
                    </button>
                </form>

                <div className="text-center mt-3">
                    <button
                        className="btn btn-link text-decoration-none small text-primary p-0"
                        onClick={() => navigate("/Forget")}
                    >
                        Forgot Password?
                    </button>

                    <div className="mt-2">
                        <button
                            className="btn btn-link text-decoration-none small text-primary p-0"
                            onClick={() => navigate("/Onboarding")}
                        >
                            Don't have an account? Register
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Login;