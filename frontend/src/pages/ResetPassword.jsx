import { useState } from "react";
import {
useParams,
useNavigate,
} from "react-router-dom";

import {
resetPassword
} from "../apis/authAPI";



function ResetPassword() {
const { token } = useParams();

const navigate =
useNavigate();

const [password, setPassword] =
useState("");

const [confirmPassword,
setConfirmPassword] =
useState("");

const [error, setError] =
useState("");

const [loading, setLoading] =
useState(false);

const handleReset =
async (e) => {


  e.preventDefault();

  setError("");

  if (
    password !==
    confirmPassword
  ) {
    setError(
      "Passwords do not match"
    );
    return;
  }

  try {
    setLoading(true);

    const response =
      await resetPassword({
        token,
        new_password:
          password,
      });

    if (
      response.data.success
    ) {
      alert(
        "Password reset successful"
      );

      navigate(
        "/login"
      );
    } else {
      setError(
        response.data
          .message
      );
    }
  } catch (err) {
    console.error(err);

    setError(
      err?.response?.data
        ?.message ||
      "Reset failed"
    );
  } finally {
    setLoading(false);
  }
};


return ( <div className="auth-container"> <div className="auth-card">


    <h2 className="auth-title">
      Reset Password
    </h2>

    {error && (
      <p className="error-message">
        {error}
      </p>
    )}

    <form
      className="auth-form"
      onSubmit={
        handleReset
      }
    >
      <input
        className="auth-input"
        type="password"
        placeholder="New Password"
        value={password}
        onChange={(e) =>
          setPassword(
            e.target.value
          )
        }
        required
      />

      <input
        className="auth-input"
        type="password"
        placeholder="Confirm Password"
        value={
          confirmPassword
        }
        onChange={(e) =>
          setConfirmPassword(
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
          ? "Resetting..."
          : "Reset Password"}
      </button>

    </form>

  </div>
</div>


);
}

export default ResetPassword;
