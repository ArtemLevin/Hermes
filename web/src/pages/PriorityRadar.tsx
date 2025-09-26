import { useEffect, useState } from "react";

type RadarItem = { student_id: number; name: string; score: number; level: number };

const API = (p: string) =>
  `${import.meta.env.VITE_API_URL || "http://localhost:8000"}${p}`;

export default function PriorityRadar() {
  const [items, setItems] = useState<RadarItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        setErr(null);
        const r = await fetch(API("/analytics/priority-radar"));
        const data = await r.json();
        setItems(data.items || []);
      } catch (e: any) {
        setErr(e?.message || "Ошибка загрузки");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="p-6">Загрузка…</div>;
  if (err) return <div className="p-6 text-red-600">Ошибка: {err}</div>;

  // нормализуем score для визуализации
  const max = Math.max(1, ...items.map((i) => Math.abs(i.score)));
  const norm = (v: number) => (Math.max(0, v) / max) * 100; // 0..100

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Радар внимания</h1>
      <p className="text-sm opacity-70">
        Выше — больше нуждаемость: просрочки, пробелы, низкий темп.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {items.map((it) => (
          <div key={it.student_id} className="p-4 rounded-2xl shadow bg-white">
            <div className="flex items-center justify-between">
              <div className="font-medium">{it.name}</div>
              <div className="text-xs opacity-60">Lvl {it.level}</div>
            </div>
            <div className="mt-2">
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-2 bg-rose-500"
                  style={{ width: `${norm(it.score)}%` }}
                  title={`score=${it.score.toFixed(2)}`}
                />
              </div>
              <div className="mt-1 text-xs opacity-70">score: {it.score.toFixed(2)}</div>
            </div>
            <div className="mt-3 flex gap-2">
              <a
                className="px-3 py-1 rounded-lg bg-gray-100 hover:bg-gray-200 text-sm"
                href={`/students/${it.student_id}`}
              >
                Профиль
              </a>
              <a
                className="px-3 py-1 rounded-lg bg-amber-100 hover:bg-amber-200 text-sm"
                href={`/assignments?student_id=${it.student_id}`}
                onClick={(e) => {
                  e.preventDefault();
                  // простая навигация без полноценного роутера-поиска:
                  window.history.pushState({}, "", "/assignments");
                  window.location.reload();
                }}
              >
                Задания
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
