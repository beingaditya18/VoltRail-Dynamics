const BASE_URL = "http://127.0.0.1:8000";

export async function fetchFleet() {
  const res = await fetch(`${BASE_URL}/api/fleet`);
  if (!res.ok) throw new Error("Failed to fetch fleet");
  return res.json();
}

export async function fetchOptimizedAssignments() {
  const res = await fetch(`${BASE_URL}/api/optimize`);
  if (!res.ok) throw new Error("Failed to fetch assignments");
  return res.json();
}

export async function fetchShap(train_id) {
  const res = await fetch(`${BASE_URL}/api/shap/${train_id}`);
  if (!res.ok) throw new Error("Failed to fetch SHAP");
  return res.json();
}
