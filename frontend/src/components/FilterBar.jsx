const opts = {
  status: ["open", "in_progress", "resolved", "closed"],
  category: ["password_reset", "printer", "desktop", "wifi", "other"],
  priority: ["low", "medium", "high"],
};

export default function FilterBar({ filters, setFilters, agents }) {
  const set = (k) => (e) => setFilters({ ...filters, [k]: e.target.value });
  return (
    <div className="panel filters">
      <input placeholder="Search…" value={filters.q || ""} onChange={set("q")} />
      {Object.entries(opts).map(([k, values]) => (
        <select key={k} value={filters[k] || ""} onChange={set(k)}>
          <option value="">All {k}</option>
          {values.map((v) => (
            <option key={v} value={v}>{v.replace("_", " ")}</option>
          ))}
        </select>
      ))}
      {agents && (
        <select value={filters.assigned_to || ""} onChange={set("assigned_to")}>
          <option value="">Any assignee</option>
          {agents.map((a) => (
            <option key={a.id} value={a.id}>{a.name}</option>
          ))}
        </select>
      )}
      <input type="date" value={filters.date_from || ""} onChange={set("date_from")} />
      <input type="date" value={filters.date_to || ""} onChange={set("date_to")} />
      <button onClick={() => setFilters({})}>Clear</button>
    </div>
  );
}
