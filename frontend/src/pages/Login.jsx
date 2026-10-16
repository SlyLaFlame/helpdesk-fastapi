import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { errMsg } from "../api/client.js";

export default function Login() {
  const { user, login, register } = useAuth();
  const [mode, setMode] = useState("login");
  const [f, setF] = useState({ name: "", email: "", password: "", department: "", role: "student" });
  const [error, setError] = useState("");
  if (user) return <Navigate to="/" />;
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      if (mode === "login") await login(f.email, f.password);
      else await register(f);
    } catch (err) {
      setError(errMsg(err));
    }
  };

  return (
    <form className="panel narrow" onSubmit={submit}>
      <h1>{mode === "login" ? "Sign in" : "Create account"}</h1>
      {mode === "register" && (
        <>
          <input placeholder="Full name" required value={f.name} onChange={set("name")} />
          <input placeholder="Department" value={f.department} onChange={set("department")} />
          <select value={f.role} onChange={set("role")}>
            <option value="student">Student</option>
            <option value="staff">Staff</option>
          </select>
        </>
      )}
      <input type="email" placeholder="Email" required value={f.email} onChange={set("email")} />
      <input type="password" placeholder="Password" required minLength={6} value={f.password} onChange={set("password")} />
      {error && <p className="error">{error}</p>}
      <button className="primary">{mode === "login" ? "Sign in" : "Register"}</button>
      <button type="button" className="link" onClick={() => setMode(mode === "login" ? "register" : "login")}>
        {mode === "login" ? "No account? Register" : "Have an account? Sign in"}
      </button>
    </form>
  );
}
