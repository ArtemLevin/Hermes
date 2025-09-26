import { useEffect, useMemo, useState } from "react";

type Assignment = {
  id: number;
  student_id: number;
  lesson_id?: number | null;
  status: "new" | "in_progress" | "done" | "late";
  title?: string | null;
  reward_type?: "badge" | "coin" | "star" | null;
  due_at?: string | null;
  topic_ids?: number[];
};

const API = (p: string) => `${import.meta.env.VITE_API_URL || "http://localhost:8000"}${p}`;

export default function Assignments() {
  const [items, setItems] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [studentId, setStudentId] = useState<number | "">("");
  const [status, setStatus] = useState<Assignment["status"] | "">("");
  const [error, setError] = useState<string | null>(null);

  const qs = useMemo(() => {
    const url = new URL(API("/assignments"));
    if (studentId !== "") url.searchParams.set("student_id", String(studentId));
    if (status !== "") url.searchParams.set("status", status);
    return url.toString();
  }, [studentId, status]);

  const reload = async () => {
    try {
      setLoading(true);
      setError(null);
      const r = await fetch(qs);
      const data = await r.json();
      setItems(data?.items || []);
    } catch (e: any) {
      setError(e?.message || "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    reload();
  }, [qs]);

  const act = async (id: number, action: "start" | "submit" | "late") => {
    const path =
      action === "start"
        ? `/assignments/${id}/start`
        : action === "submit"
        ? `/assignments/${id}/submit`
        : `/assignments/${id}/mark_late`;
    const opts =
        action === "submit"
          ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ artifacts: [], grade: 5 }) }
          : { method: "POST" as const };
    const r = await fetch(API(path), opts);
    if (r.ok) {
      setItems((prev) =>
        prev.map((x) =>
          x.id === id
            ? { ...x, status: action === "start" ? "in_progress" : action === "submit" ? "done" : "late" }
            : x
        )
      );
    }
  };

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Домашние задания</h1>

      {/* Фильтры */}
      <div className="flex flex-wrap gap-3 items-end">
        <div>
          <label className="block text-sm mb-1">ID ученика</label>
          <input
            type="number"
            className="px-3 py-2 rounded-xl border"
            placeholder="любые"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value === "" ? "" : Number(e.target.value))}
          />
        </div>
        <div>
          <label className="block text-sm mb-1">Статус</label>
          <select
            className="px-3 py-2 rounded-xl border"
            value={status}
            onChange={(e) => setStatus(e.target.value as any)}
          >
            <option value="">любой</option>
            <option value="new">new</option>
            <option value="in_progress">in_progress</option>
            <option value="done">done</option>
            <option value="late">late</option>
          </select>
        </div>
        <button
          className="px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200"
          onClick={reload}
          disabled={loading}
        >
          Обновить
        </button>
      </div>

      {/* Состояния */}
      {loading && <div>Загрузка…</div>}
      {error && <div className="text-red-600">Ошибка: {error}</div>}
      {!loading && !error && items.length === 0 && (
        <div className="text-sm opacity-70">Ничего не найдено</div>
      )}

      {/* Список */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {items.map((a) => (
          <div key={a.id} className="p-4 rounded-2xl shadow bg-white">
            <div className="flex items-center justify-between">
              <div className="text-sm opacity-60">#{a.id}</div>
              <span
                className={`px-2 py-0.5 rounded-lg text-xs ${
                  a.status === "done"
                    ? "bg-green-100 text-green-700"
                    : a.status === "late"
                    ? "bg-amber-100 text-amber-700"
                    : a.status === "in_progress"
                    ? "bg-blue-100 text-blue-700"
                    : "bg-gray-100 text-gray-700"
                }`}
              >
                {a.status}
              </span>
            </div>
            <div className="mt-1 font-medium">{a.title || "Без названия"}</div>
            <div className="text-sm opacity-80">
              Ученик: {a.student_id}
              {a.reward_type ? ` · награда: ${a.reward_type}` : ""}
              {a.due_at ? ` · дедлайн: ${new Date(a.due_at).toLocaleString()}` : ""}
            </div>
            <div className="mt-3 flex gap-2">
              <button
                className="px-3 py-1 rounded-lg bg-gray-100 hover:bg-gray-200 text-sm"
                onClick={() => act(a.id, "start")}
              >
                Начать
              </button>
              <button
                className="px-3 py-1 rounded-lg bg-green-500 text-white hover:bg-green-600 text-sm"
                onClick={() => act(a.id, "submit")}
              >
                Сдать
              </button>
              <button
                className="px-3 py-1 rounded-lg bg-amber-500 text-white hover:bg-amber-600 text-sm"
                onClick={() => act(a.id, "late")}
              >
                Просрочить
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
