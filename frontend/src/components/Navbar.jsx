import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Navbar() {
  const { user, logout, isSupport } = useAuth();
  return (
    <header className="nav">
      <strong className="brand">ICT/HELPDESK</strong>
      <NavLink to="/" end>Tickets</NavLink>
      <NavLink to="/tickets/new">New ticket</NavLink>
      {isSupport && <NavLink to="/dashboard">Dashboard</NavLink>}
      <span className="spacer" />
      <span>
        {user.name} · <em>{user.role}</em>
      </span>
      <button onClick={logout}>Sign out</button>
    </header>
  );
}
