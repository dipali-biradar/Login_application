import {
  createContext,
  useState,
  useEffect,
  useContext
} from "react";

import {
  loginUser,
} from "../apis/authAPI";

export const useAuth = () => {
  return useContext(AuthContext);
};
 
export const AuthContext =
  createContext();

export const AuthProvider = ({
  children,
}) => {


  const [user, setUser] =
    useState(null);

  const [token, setToken] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  // Load user from localStorage
  useEffect(() => {

    const savedUser =
      localStorage.getItem("user");

    const savedToken =
      localStorage.getItem("token");

    if (savedUser && savedToken) {

      setUser(
        JSON.parse(savedUser)
      );

      setToken(savedToken);
    }

    setLoading(false);

  }, []);

  // Login
  const login = async (
    email,
    password
  ) => {

   const res =
      await loginUser({
        email,
        password,
      });

    if (!res.data.success) {
      throw new Error(
        res.data.message
      );
    }

    const userData =
      res.data.user;

    const jwtToken =
      res.data.token;

    setUser(userData);

    setToken(jwtToken);

    localStorage.setItem(
      "user",
      JSON.stringify(userData)
    );

    localStorage.setItem(
      "token",
      jwtToken
    );

    return userData;
  };

  // Logout
  const logout = () => {

    setUser(null);

    setToken(null);

    localStorage.removeItem(
      "user"
    );

    localStorage.removeItem(
      "token"
    );
  };

  // Helpers
  const isAuthenticated =
    !!token;

  const isAdmin =
    user?.role === "admin";

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,

        login,
        logout,

        isAuthenticated,
        isAdmin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};