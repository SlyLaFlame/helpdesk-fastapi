import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client.js";
import { useAuth } from "../context/AuthContext.jsx";
import useTickets from "../hooks/useTickets.js";
import FilterBar from "../components/FilterBar.jsx";
import TicketCard from "../components/TicketCard.jsx";

export default function TicketList() {
  const { isSupport } = useAuth();
  const [filters, setFilters] = useState({});
  const [agents, setAgents] = useState(null);
  const { tickets, loading, error } = useTickets(filters);

  useEffect(() => {
    if (isSupport) api.get("/users/agents").then((r) => setAgents(r.data));
  }, [isSupport]);

  return (
    <>
      <div className="row between">
        <h1>{isSupport ? "All tickets" : "My tickets"}</h1>
        <Link to="/tickets/new" className="button primary">+ New ticket</Link>
      </div>
      <FilterBar filters={filters} setFilters={setFilters} agents={agents} />
      {loading && <p className="muted">Loading…</p>}
      {error && <p className="error">{error}</p>}
      {!loading && tickets.length === 0 && <p className="muted">No tickets match.</p>}
      <div className="list">
        {tickets.map((t) => (
          <TicketCard key={t.id} t={t} />
        ))}
      </div>
    </>
  );
}
