import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import authService from "../services/authService";

function ResetPassword() {
  const { token } = useParams();
  const navigate = useNavigate();

  const [password, setPassword] = useState("");

  const handleReset = async () => {
    try {
      const response = await authService.resetPassword({
        token,
        new_password: password,
      });

      if (response.data.success) {
        alert("Password reset successful");

        navigate("/login");
      }
    } catch (err) {
      console.log(err);
      alert("Reset failed");
    }
  };

  return (
    <div>
      <h2>Reset Password</h2>

      <input
        type="password"
        placeholder="New Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button onClick={handleReset}>
        Reset Password
      </button>
    </div>
  );
}

export default ResetPassword;