import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api, { errMsg } from "../api/client.js";
import { useAuth } from "../context/AuthContext.jsx";
import StatusBadge, { PriorityBadge } from "../components/StatusBadge.jsx";

// Mirrors backend crud.TRANSITIONS
const NEXT = { open: ["in_progress"], in_progress: ["resolved", "open"], resolved: ["closed", "in_progress"], closed: [] };

export default function TicketDetail() {
  const { id } = useParams();
  const { isSupport } = useAuth();
  const [t, setT] = useState(null);
  const [agents, setAgents] = useState([]);
  const [comment, setComment] = useState("");
  const [error, setError] = useState("");

  const load = () => api.get(`/tickets/${id}`).then((r) => setT(r.data)).catch((e) => setError(errMsg(e)));
  useEffect(() => {
    load();
    if (isSupport) api.get("/users/agents").then((r) => setAgents(r.data));
  }, [id]);

  const patch = async (body) => {
    try {
      setT((await api.patch(`/tickets/${id}`, body)).data);
      setError("");
    } catch (e) {
      setError(errMsg(e));
    }
  };
  const post = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/tickets/${id}/comments`, { comment });
      setComment("");
      load();
    } catch (err) {
      setError(errMsg(err));
    }
  };

  if (error && !t) return <p className="error">{error}</p>;
  if (!t) return <p className="muted">Loading…</p>;

  return (
    <div className="detail">
      <Link to="/">← All tickets</Link>
      <div className="panel">
        <div className="row">
          <span className="muted">#{t.id}</span>
          <StatusBadge status={t.status} />
          <PriorityBadge priority={t.priority} />
          <span className="muted">{t.category}</span>
        </div>
        <h1>{t.title}</h1>
        <p className="pre">{t.description}</p>
        <p className="muted small">
          By {t.creator.name} · {new Date(t.created_at).toLocaleString()}
          {t.resolved_at && ` · resolved ${new Date(t.resolved_at).toLocaleString()}`}
        </p>
      </div>

      {isSupport && t.status !== "closed" && (
        <div className="panel row wrap">
          {NEXT[t.status].map((s) => (
            <button key={s} className="primary" onClick={() => patch({ status: s })}>
              → {s.replace("_", " ")}
            </button>
          ))}
          <select
            value={t.assignee?.id || ""}
            onChange={(e) => patch(e.target.value ? { assigned_to: Number(e.target.value) } : { unassign: true })}
          >
            <option value="">Unassigned</option>
            {agents.map((a) => (
              <option key={a.id} value={a.id}>{a.name}</option>
            ))}
          </select>
          <select value={t.priority} onChange={(e) => patch({ priority: e.target.value })}>
            {["low", "medium", "high"].map((p) => (
              <option key={p}>{p}</option>
            ))}
          </select>
        </div>
      )}
      {error && <p className="error">{error}</p>}

      <h2>Activity</h2>
      {t.comments.map((c) =>
        c.is_system ? (
          <p key={c.id} className="muted small">
            ⚙ {c.comment} · {c.author.name} · {new Date(c.created_at).toLocaleString()}
          </p>
        ) : (
          <div key={c.id} className="panel">
            <strong>{c.author.name}</strong>{" "}
            <span className="muted small">{new Date(c.created_at).toLocaleString()}</span>
            <p className="pre">{c.comment}</p>
          </div>
        )
      )}
      {t.status !== "closed" && (
        <form onSubmit={post} className="panel">
          <textarea rows={3} required placeholder="Add a comment" value={comment} onChange={(e) => setComment(e.target.value)} />
          <button>Post</button>
        </form>
      )}
    </div>
  );
}
