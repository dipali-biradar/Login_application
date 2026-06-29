import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { forgotPassword } from "../apis/authAPI";



function ForgotPassword() {
const navigate = useNavigate();

const [email, setEmail] = useState("");

const [message, setMessage] =
useState("");

const [error, setError] =
useState("");

const [loading, setLoading] =
useState(false);

const handleSubmit = async (e) => {
e.preventDefault();


setMessage("");
setError("");

try {
  setLoading(true);

  const res =
    await forgotPassword({
      email,
    });

  if (res.data.success) {
    setMessage(
      "Reset link sent to your email."
    );

    setTimeout(() => {
      navigate("/login");
    }, 2000);
  } else {
    setError(
      res.data.message
    );
  }
} catch (err) {
  console.error(err);

  setError(
    err?.response?.data?.message ||
    "Something went wrong"
  );
} finally {
  setLoading(false);
}


};

return ( <div className="auth-container"> <div className="auth-card">


    <h2 className="auth-title">
      Forgot Password
    </h2>

    {message && (
      <p className="success-message">
        {message}
      </p>
    )}

    {error && (
      <p className="error-message">
        {error}
      </p>
    )}

    <form
      className="auth-form"
      onSubmit={handleSubmit}
    >
      <input
        className="auth-input"
        type="email"
        placeholder="Enter your email"
        value={email}
        onChange={(e) =>
          setEmail(
            e.target.value
          )
        }
        required
      />

      <button
        className="auth-button"
        type="submit"
        disabled={loading}
      >
        {loading
          ? "Sending..."
          : "Send Reset Link"}
      </button>
    </form>

  </div>
</div>


);
}

export default ForgotPassword;
