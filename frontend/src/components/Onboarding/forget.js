import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_DOMAIN;

// Step 1 — Enter email
function StepEmail({ onNext }) {
    const [email,   setEmail]   = useState("");
    const [error,   setError]   = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        if (!email) { setError("Email is required"); return; }

        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/auth/forgot-password`, { email });
            onNext(email);
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to send OTP. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <div className="text-center mb-4">
                <div
                    className="rounded-circle bg-warning text-white d-inline-flex align-items-center justify-content-center shadow-sm"
                    style={{ width: "60px", height: "60px" }}
                >
                    <i className="bi bi-key fs-3"></i>
                </div>
                <h3 className="mt-3 fw-bold">Forgot Password</h3>
                <p className="text-muted small">Enter your email and we'll send you a reset code</p>
            </div>

            {error && <div className="alert alert-danger py-2">{error}</div>}

            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label className="form-label fw-semibold">Email Address</label>
                    <div className="input-group">
                        <span className="input-group-text bg-light">
                            <i className="bi bi-envelope"></i>
                        </span>
                        <input
                            type="email"
                            className="form-control"
                            placeholder="Enter your registered email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                </div>

                <button
                    type="submit"
                    className="btn btn-warning w-100 fw-semibold text-white"
                    disabled={loading}
                >
                    {loading
                        ? <span className="spinner-border spinner-border-sm me-2"></span>
                        : <i className="bi bi-send me-2"></i>
                    }
                    {loading ? "Sending OTP..." : "Send Reset Code"}
                </button>
            </form>
        </>
    );
}


// Step 2 — Enter OTP
function StepOtp({ email, onNext, onResend }) {
    const [otp,      setOtp]      = useState(["", "", "", "", "", ""]);
    const [error,    setError]    = useState("");
    const [loading,  setLoading]  = useState(false);
    const [resending, setResending] = useState(false);
    const [timer,    setTimer]    = useState(60);
    const inputsRef = [];

    // Timer countdown
    useState(() => {
        const t = setInterval(() => {
            setTimer(prev => {
                if (prev <= 1) { clearInterval(t); return 0; }
                return prev - 1;
            });
        }, 1000);
        return () => clearInterval(t);
    }, []);

    const handleChange = (value, index) => {
        if (!/^\d?$/.test(value)) return;
        const newOtp = [...otp];
        newOtp[index] = value;
        setOtp(newOtp);
        if (value && index < 5) inputsRef[index + 1].focus();
    };

    const handleKeyDown = (e, index) => {
        if (e.key === "Backspace" && !otp[index] && index > 0) {
            inputsRef[index - 1].focus();
        }
    };

    const handlePaste = (e) => {
        const pasted = e.clipboardData.getData("text").slice(0, 6).split("");
        if (pasted.every(c => /\d/.test(c))) {
            const newOtp = [...otp];
            pasted.forEach((d, i) => { newOtp[i] = d; });
            setOtp(newOtp);
            inputsRef[Math.min(pasted.length, 5)].focus();
        }
    };

    const handleVerify = async () => {
        setError("");
        const code = otp.join("");
        if (code.length !== 6) { setError("Please enter the complete 6-digit OTP"); return; }

        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/auth/verify-forgot-otp`, {
                email,
                otp_code: code
            });
            onNext(code);
        } catch (err) {
            setError(err.response?.data?.detail || "Invalid OTP. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleResend = async () => {
        setResending(true);
        try {
            await axios.post(`${API_BASE_URL}/auth/forgot-password`, { email });
            setTimer(60);
            setOtp(["", "", "", "", "", ""]);
            inputsRef[0].focus();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to resend OTP.");
        } finally {
            setResending(false);
        }
    };

    return (
        <>
            <div className="text-center mb-4">
                <div
                    className="rounded-circle bg-warning text-white d-inline-flex align-items-center justify-content-center shadow-sm"
                    style={{ width: "60px", height: "60px" }}
                >
                    <i className="bi bi-shield-lock fs-3"></i>
                </div>
                <h3 className="mt-3 fw-bold">Enter Reset Code</h3>
                <p className="text-muted small">
                    We sent a 6-digit code to <strong>{email}</strong>
                </p>
            </div>

            {error && <div className="alert alert-danger py-2">{error}</div>}

            <div className="d-flex justify-content-center gap-2 mb-4" onPaste={handlePaste}>
                {otp.map((digit, i) => (
                    <input
                        key={i}
                        ref={el => inputsRef[i] = el}
                        type="text"
                        maxLength={1}
                        className="form-control text-center fw-bold fs-4"
                        style={{ width: "48px", height: "56px" }}
                        value={digit}
                        onChange={(e) => handleChange(e.target.value, i)}
                        onKeyDown={(e) => handleKeyDown(e, i)}
                    />
                ))}
            </div>

            <button
                className="btn btn-warning w-100 fw-semibold text-white"
                onClick={handleVerify}
                disabled={loading}
            >
                {loading
                    ? <span className="spinner-border spinner-border-sm me-2"></span>
                    : <i className="bi bi-check-circle me-2"></i>
                }
                {loading ? "Verifying..." : "Verify Code"}
            </button>

            <div className="text-center mt-3">
                {timer > 0 ? (
                    <p className="text-muted small">Resend code in <strong>{timer}s</strong></p>
                ) : (
                    <button
                        className="btn btn-link text-decoration-none small text-warning p-0"
                        onClick={handleResend}
                        disabled={resending}
                    >
                        {resending ? "Sending..." : "Resend Code"}
                    </button>
                )}
            </div>
        </>
    );
}


// Step 3 — Set new password
function StepReset({ email, otpCode, onSuccess }) {
    const [password,        setPassword]        = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error,           setError]           = useState("");
    const [loading,         setLoading]         = useState(false);
    const [showPass,        setShowPass]        = useState(false);
    const [showConfirm,     setShowConfirm]     = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        if (password.length < 6) {
            setError("Password must be at least 6 characters.");
            return;
        }
        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/auth/reset-password`, {
                email,
                otp_code:     otpCode,
                new_password: password
            });
            onSuccess();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to reset password. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <div className="text-center mb-4">
                <div
                    className="rounded-circle bg-success text-white d-inline-flex align-items-center justify-content-center shadow-sm"
                    style={{ width: "60px", height: "60px" }}
                >
                    <i className="bi bi-lock fs-3"></i>
                </div>
                <h3 className="mt-3 fw-bold">Set New Password</h3>
                <p className="text-muted small">Choose a strong password for your account</p>
            </div>

            {error && <div className="alert alert-danger py-2">{error}</div>}

            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label className="form-label fw-semibold">New Password</label>
                    <div className="input-group">
                        <span className="input-group-text bg-light">
                            <i className="bi bi-lock"></i>
                        </span>
                        <input
                            type={showPass ? "text" : "password"}
                            className="form-control"
                            placeholder="Min. 6 characters"
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

                <div className="mb-4">
                    <label className="form-label fw-semibold">Confirm Password</label>
                    <div className="input-group">
                        <span className="input-group-text bg-light">
                            <i className="bi bi-lock-fill"></i>
                        </span>
                        <input
                            type={showConfirm ? "text" : "password"}
                            className="form-control"
                            placeholder="Re-enter password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                        />
                        <button
                            type="button"
                            className="input-group-text bg-light border-start-0"
                            onClick={() => setShowConfirm(!showConfirm)}
                        >
                            <i className={`bi ${showConfirm ? "bi-eye-slash" : "bi-eye"}`}></i>
                        </button>
                    </div>
                </div>

                <button
                    type="submit"
                    className="btn btn-success w-100 fw-semibold"
                    disabled={loading}
                >
                    {loading
                        ? <span className="spinner-border spinner-border-sm me-2"></span>
                        : <i className="bi bi-check-lg me-2"></i>
                    }
                    {loading ? "Resetting..." : "Reset Password"}
                </button>
            </form>
        </>
    );
}


// Step 4 — Success
function StepSuccess({ navigate }) {
    return (
        <div className="text-center py-3">
            <div
                className="rounded-circle bg-success text-white d-inline-flex align-items-center justify-content-center shadow-sm mb-3"
                style={{ width: "70px", height: "70px" }}
            >
                <i className="bi bi-check-lg" style={{ fontSize: "2rem" }}></i>
            </div>
            <h3 className="fw-bold">Password Reset!</h3>
            <p className="text-muted small mb-4">
                Your password has been reset successfully.<br />
                You can now log in with your new password.
            </p>
            <button
                className="btn btn-primary w-100 fw-semibold"
                onClick={() => navigate("/")}
            >
                <i className="bi bi-box-arrow-in-right me-2"></i>
                Go to Login
            </button>
        </div>
    );
}


// Main Forget component — controls steps
export default function Forget() {
    const navigate = useNavigate();
    const [step,    setStep]    = useState(1); // 1=email, 2=otp, 3=reset, 4=success
    const [email,   setEmail]   = useState("");
    const [otpCode, setOtpCode] = useState("");

    return (
        <div className="d-flex justify-content-center align-items-center min-vh-100 bg-light">
            <div className="card shadow-lg border-0 rounded-4 p-4" style={{ maxWidth: "420px", width: "100%" }}>

                {/* Step indicator */}
                {step < 4 && (
                    <div className="d-flex justify-content-center gap-2 mb-4">
                        {[1, 2, 3].map(s => (
                            <div
                                key={s}
                                style={{
                                    width: "32px", height: "4px", borderRadius: "2px",
                                    backgroundColor: s <= step ? "#f59e0b" : "#e5e7eb"
                                }}
                            />
                        ))}
                    </div>
                )}

                {step === 1 && (
                    <StepEmail onNext={(e) => { setEmail(e); setStep(2); }} />
                )}

                {step === 2 && (
                    <StepOtp
                        email={email}
                        onNext={(code) => { setOtpCode(code); setStep(3); }}
                    />
                )}

                {step === 3 && (
                    <StepReset
                        email={email}
                        otpCode={otpCode}
                        onSuccess={() => setStep(4)}
                    />
                )}

                {step === 4 && (
                    <StepSuccess navigate={navigate} />
                )}

                {/* Back to login */}
                {step < 4 && (
                    <div className="text-center mt-3">
                        <button
                            className="btn btn-link text-decoration-none small text-secondary p-0"
                            onClick={() => step === 1 ? navigate("/") : setStep(step - 1)}
                        >
                            <i className="bi bi-arrow-left me-1"></i>
                            {step === 1 ? "Back to Login" : "Go Back"}
                        </button>
                    </div>
                )}

            </div>
        </div>
    );
}