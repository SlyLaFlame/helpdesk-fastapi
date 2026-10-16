import { useEffect, useState } from "react";
import api, { errMsg } from "../api/client.js";

/** Turns filter state into ?status=open&category=printer... and fetches. */
export default function useTickets(filters) {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const key = JSON.stringify(filters);

  useEffect(() => {
    const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v !== "" && v != null));
    setLoading(true);
    const t = setTimeout(() => {
      api
        .get("/tickets", { params })
        .then((r) => {
          setTickets(r.data);
          setError(null);
        })
        .catch((e) => setError(errMsg(e)))
        .finally(() => setLoading(false));
    }, 250); // debounce search typing
    return () => clearTimeout(t);
  }, [key]);

  return { tickets, loading, error };
}
