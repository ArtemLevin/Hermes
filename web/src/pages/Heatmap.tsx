import { useEffect, useMemo, useState } from "react";

type Topic = { id: number; name: string };
type Heat = { topic_id: number; heat: number; updated_at: string };

const API = (p: string) =>
  `${import.meta.env.VITE_API_URL || "http://localhost:8000"}${p}`;

export default function Heatmap({ studentId = 1 }: { studentId?: number }) {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [heat, setHeat] = useState<Record<number, number>>({});
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const maxHeat = useMemo(
    () => Math.max(1, ...Object.values(heat), 1),
    [heat]
  );

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        setErr(null);
        const [t, h] = await Promise.all([
          fetch(API("/topics")).then((r) => r.json()),
          fetch(API(`/topics/heatmap?student_id=${studentId}`)).then((r) =>
            r.json()
          ),
        ]);
        setTopics(t || []);
        const map: Record<number, number> = {};
        (h as Heat[]).forEach((x) => (map[x.topic_id] = x.heat));
        setHeat(map);
      } catch (e: any) {
        setErr(e?.message || "Ошибка загрузки");
      } finally {
        setLoading(false);
      }
    })();
  }, [studentId]);

  const adjust = async (topicId: number, delta: number) => {
    const r = await fetch(API(`/topics/heatmap?student_id=${studentId}`), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic_id: topicId, delta }),
    });
    if (r.ok) {
      const data = await r.json();
      setHeat((prev) => ({ ...prev, [topicId]: data.heat }));
    }
  };

  if (loading) return <div className="p-6">Загрузка…</div>;
  if (err) return <div className="p-6 text-red-600">Ошибка: {err}</div>;

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Теплокарта ошибок (ученик #{studentId})</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {topics.map((t) => {
          const v = heat[t.id] || 0;
          // нормализуем интенсивность 0..1
          const k = Math.min(1, v / maxHeat);
          // цветовая шкала: от зелёного к красному
          const bg = `rgba(${Math.round(255 * k)}, ${Math.round(
            200 * (1 - k)
          )}, 120, 0.25)`;
          const border = `rgba(${Math.round(255 * k)}, ${Math.round(
            200 * (1 - k)
          )}, 120, 0.7)`;
          return (
            <div
              key={t.id}
              className="p-4 rounded-2xl shadow bg-white border"
              style={{ backgroundColor: bg, borderColor: border }}
            >
              <div className="flex items-center justify-between">
                <div className="font-medium">{t.name}</div>
                <span className="text-sm px-2 py-0.5 rounded-lg bg-white/60">
                  heat: {v}
                </span>
              </div>
              <div className="mt-3 flex gap-2">
                <button
                  className="px-3 py-1 rounded-lg bg-gray-100 hover:bg-gray-200 text-sm"
                  onClick={() => adjust(t.id, -1)}
                >
                  −1
                </button>
                <button
                  className="px-3 py-1 rounded-lg bg-amber-100 hover:bg-amber-200 text-sm"
                  onClick={() => adjust(t.id, +1)}
                >
                  +1
                </button>
                <button
                  className="px-3 py-1 rounded-lg bg-amber-200 hover:bg-amber-300 text-sm"
                  onClick={() => adjust(t.id, +5)}
                >
                  +5
                </button>
              </div>
              <div className="mt-2 text-xs opacity-70">
                Поднимайте «heat» там, где часто ошибки. Со временем снижайте при прогрессе.
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
