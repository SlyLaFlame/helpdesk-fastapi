import { Link } from "react-router-dom";
import StatusBadge, { PriorityBadge } from "./StatusBadge.jsx";

export default function TicketCard({ t }) {
  return (
    <Link to={`/tickets/${t.id}`} className="panel card">
      <div className="row">
        <span className="muted">#{t.id}</span>
        <StatusBadge status={t.status} />
        <PriorityBadge priority={t.priority} />
      </div>
      <h3>{t.title}</h3>
      <div className="muted small">
        {t.category.replace("_", " ")} · by {t.creator.name} ·{" "}
        {t.assignee ? `assigned to ${t.assignee.name}` : "unassigned"} · {new Date(t.created_at).toLocaleString()}
      </div>
    </Link>
  );
}
