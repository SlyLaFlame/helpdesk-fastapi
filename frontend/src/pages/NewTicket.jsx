import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { errMsg } from "../api/client.js";

export default function NewTicket() {
  const nav = useNavigate();
  const [f, setF] = useState({ title: "", description: "", category: "other", priority: "medium" });
  const [error, setError] = useState("");
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    try {
      const { data } = await api.post("/tickets", f);
      nav(`/tickets/${data.id}`);
    } catch (err) {
      setError(errMsg(err));
    }
  };

  return (
    <form className="panel narrow" onSubmit={submit}>
      <h1>New ticket</h1>
      <input placeholder="Short summary" required maxLength={200} value={f.title} onChange={set("title")} />
      <select value={f.category} onChange={set("category")}>
        {["password_reset", "printer", "desktop", "wifi", "other"].map((c) => (
          <option key={c} value={c}>{c.replace("_", " ")}</option>
        ))}
      </select>
      <select value={f.priority} onChange={set("priority")}>
        {["low", "medium", "high"].map((p) => (
          <option key={p}>{p}</option>
        ))}
      </select>
      <textarea rows={6} placeholder="Details" value={f.description} onChange={set("description")} />
      {error && <p className="error">{error}</p>}
      <button className="primary">Submit</button>
    </form>
  );
}
