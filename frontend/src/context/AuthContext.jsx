import { createContext, useContext, useState } from "react";
import api from "../api/client.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem("user") || "null"));

  const save = ({ access_token, user }) => {
    localStorage.setItem("token", access_token);
    localStorage.setItem("user", JSON.stringify(user));
    setUser(user);
  };

  const login = async (email, password) => {
    const form = new URLSearchParams({ username: email, password });
    save((await api.post("/auth/login", form)).data);
  };
  const register = async (payload) => save((await api.post("/auth/register", payload)).data);
  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };
  const isSupport = !!user && ["it_agent", "admin"].includes(user.role);

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isSupport }}>{children}</AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
