import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import authService from "../services/authService";
import "./Login.css";

function Login() {
const navigate = useNavigate();

const [email, setEmail] = useState("");
const [password, setPassword] = useState("");
const [error, setError] = useState("");

const handleSubmit = async (e) => {
e.preventDefault();


setError("");

try {
  const res = await authService.login({
    email,
    password,
  });

  if (res.data.success) {
    // Save JWT Token
    authService.saveToken(res.data.token);

    // Save User Details
    localStorage.setItem(
      "user",
      JSON.stringify(res.data.user)
    );

    localStorage.setItem(
      "role",
      res.data.user.role
    );

    // Redirect Based On Role
    if (res.data.user.role === "admin") {
      navigate("/admin");
    } else {
      navigate("/dashboard");
    }
  } else {
    setError(res.data.message);
  }
} catch (err) {
  console.error(err);

  setError(
    err?.response?.data?.message ||
    "Login failed. Please try again."
  );
}


};

return ( <div className="login-container"> <div className="login-card">


    <h2>Login</h2>

    {error && (
      <p className="error-message">
        {error}
      </p>
    )}

    <form
      onSubmit={handleSubmit}
      className="login-form"
    >
      <input
        type="email"
        placeholder="Enter Email"
        value={email}
        onChange={(e) =>
          setEmail(e.target.value)
        }
        required
      />

      <input
        type="password"
        placeholder="Enter Password"
        value={password}
        onChange={(e) =>
          setPassword(e.target.value)
        }
        required
      />

      <button type="submit">
        Login
      </button>
    </form>

    <div className="login-links">
      <p>
        <Link to="/forgot-password">
          Forgot Password?
        </Link>
      </p>

      <p>
        Don't have an account?{" "}
        <Link to="/signup">
          Create Account
        </Link>
      </p>
    </div>

  </div>
</div>


);
}

export default Login;
