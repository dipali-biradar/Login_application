import { useState } from "react";
import { Link } from "react-router-dom";
import authService from "../services/authService";
import PhoneInput from "react-phone-number-input";
import "react-phone-number-input/style.css";
import { MuiTelInput } from "mui-tel-input";
import { matchIsValidTel } from "mui-tel-input";
import "./Signup.css";

function Signup() {
const [formData, setFormData] = useState({
first_name: "",
middle_name: "",
last_name: "",
email: "",
mobile: "",
password: "",
});

const [message, setMessage] = useState("");
const [error, setError] = useState("");

const handleChange = (e) => {
setFormData({
...formData,
[e.target.name]:
e.target.value,
});
};


const handleSubmit = async (e) => {
e.preventDefault();


setMessage("");
setError("");
if (!matchIsValidTel(formData.mobile)) {
    setError("Please enter a valid mobile number");
    return;
  }
try {
  const res =
    await authService.register(
      formData
    );

  if (res.data.success) {
    setMessage(
      "Registration successful. Please check your email and verify your account before logging in."
    );
    

    setFormData({
      first_name: "",
      middle_name: "",
      last_name: "",
      email: "",
      mobile: "",
      password: "",
    });
    

  } else {
    setError(
      res.data.message
    );
  }

} catch (err) {
  console.error(err);

  setError(
    "Registration Failed"
  );
}
};

return ( <div className="auth-container"> <div className="auth-card signup-card">


    <h2 className="auth-title">
      Create Account
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
        name="first_name"
        placeholder="First Name"
        value={formData.first_name}
        onChange={handleChange}
        required
      />

      <input
        className="auth-input"
        name="middle_name"
        placeholder="Middle Name"
        value={formData.middle_name}
        onChange={handleChange}
      />
      <input
        className="auth-input"
        name="last_name"
        placeholder="Last Name"
        value={formData.last_name}
        onChange={handleChange}
        required
      />
      <input
        className="auth-input"
        type="email"
        name="email"
        placeholder="Email Address"
        value={formData.email}
        onChange={handleChange}
        required
      />
    
      <MuiTelInput
        className="auth-input"
        name="mobile"
        placeholder="Monile Number"
        defaultCountry="IN"
        value={formData.mobile}
        onChange={(value) =>
        setFormData({
        ...formData,
        mobile: value,
         })
       }
      />  
      <input
        className="auth-input"
        type="password"
        name="password"
        placeholder="Password"
        value={formData.password}
        onChange={handleChange}
        required
      />

      <button
        className="auth-button"
        type="submit"
      >
        Register
      </button>

    </form>

    <div className="signup-login-link">
      Already have an account?
      <Link to="/login"> Login</Link>
    </div>

  </div>
</div>


);
}

export default Signup;