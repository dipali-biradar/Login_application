import {
  useEffect,
  useState,
} from "react";

import { useParams } from "react-router-dom";

import authService from "../services/authService";

function VerifyEmail() {

  SMTP_EMAIL = "biradardipali860@gmail.com"
  SMTP_PASSWORD = "bccc vbhd lpdq bsaz"
  const { token } =
    useParams();

  const [message,
    setMessage] =
    useState(
      "Verifying..."
    );

  useEffect(() => {

    const verify =
      async () => {

        try {

          const res =
            await authService
              .verifyEmail(
                token
              );

          setMessage(
            res.data.message
          );

        } catch {

          setMessage(
            "Verification Failed"
          );
        }
      };

    verify();

  }, [token]);

  return (
    <div className="auth-container">
      <div className="auth-card">

        <h2 className="auth-title">
          Email Verification
        </h2>

        <p className="success-message">
          {message}
        </p>

      </div>
    </div>
  );
}

export default VerifyEmail;