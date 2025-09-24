export const API = (path: string) => `http://localhost:8000${path}`;

export async function getOverview() {
  const r = await fetch(API("/dashboard/overview"));
  return await r.json();
}

export async function getStudents(q?: string) {
  const url = new URL(API("/students"));
  if (q) url.searchParams.set("q", q);
  const r = await fetch(url.toString());
  return await r.json();
}
