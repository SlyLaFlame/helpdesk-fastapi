const LABEL = { open: "Open", in_progress: "In progress", resolved: "Resolved", closed: "Closed" };

export default function StatusBadge({ status }) {
  return <span className={`badge status-${status}`}>{LABEL[status]}</span>;
}

export function PriorityBadge({ priority }) {
  return <span className={`badge prio-${priority}`}>{priority}</span>;
}
