import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

const authService = {
  register: (data) => 
    axios.post(`${API_URL}/register`, data),

  login: (data) => 
    axios.post(`${API_URL}/login`, data),

  forgotPassword: (data) => 
    axios.post(`${API_URL}/forgot-password`, data),

  resetPassword: (data) => 
    axios.post(`${API_URL}/reset-password`, data),

  verifyEmail: (token) => 
    axios.get(`${API_URL}/verify-email/${token}`),

  saveToken: (token) => 
    localStorage.setItem("token", token),

  getToken: () => 
    localStorage.getItem("token"),

  logout: () => 
    localStorage.removeItem("token"),

  isAuthenticated: () => 
    !!localStorage.getItem("token")
};

export default authService;