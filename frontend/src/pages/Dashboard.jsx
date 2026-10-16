import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api from "../api/client.js";

const COLORS = { open: "#3b82f6", in_progress: "#f59e0b", resolved: "#10b981", closed: "#6b7280" };

export default function Dashboard() {
  const [d, setD] = useState(null);
  useEffect(() => {
    api.get("/tickets/analytics").then((r) => setD(r.data));
  }, []);
  if (!d) return <p className="muted">Loading…</p>;
  const avg = d.avg_resolution_hours;

  return (
    <>
      <h1>Dashboard</h1>
      <div className="stats">
        <Stat label="Total" value={d.total} />
        <Stat label="Active" value={d.open_count} />
        <Stat label="Resolved/closed" value={d.closed_count} />
        <Stat label="Avg resolution" value={avg == null ? "—" : avg < 48 ? `${avg.toFixed(1)} h` : `${(avg / 24).toFixed(1)} d`} />
      </div>
      <div className="charts">
        <div className="panel">
          <h3>Tickets by category</h3>
          <ResponsiveContainer height={260}>
            <BarChart data={d.by_category}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#f97316" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="panel">
          <h3>Status breakdown</h3>
          <ResponsiveContainer height={260}>
            <PieChart>
              <Pie data={d.by_status} dataKey="count" nameKey="label" innerRadius={60} outerRadius={100} label>
                {d.by_status.map((s) => (
                  <Cell key={s.label} fill={COLORS[s.label]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  );
}

const Stat = ({ label, value }) => (
  <div className="panel stat">
    <div className="muted small">{label}</div>
    <div className="big">{value}</div>
  </div>
);
