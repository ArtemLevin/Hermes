import { useEffect, useState } from "react";

type Lesson = {
  id: number;
  student_id: number;
  date: string;
  topic: string;
};

const API = (p: string) =>
  `${import.meta.env.VITE_API_URL || "http://localhost:8000"}${p}`;

export default function Calendar() {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        setErr(null);
        const r = await fetch(API("/lessons"));
        const data = await r.json();
        setLessons(data.items || []);
      } catch (e: any) {
        setErr(e?.message || "Ошибка загрузки");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="p-6">Загрузка…</div>;
  if (err) return <div className="p-6 text-red-600">Ошибка: {err}</div>;

  // группировка по дате
  const byDate: Record<string, Lesson[]> = {};
  lessons.forEach((l) => {
    const d = l.date.split("T")[0];
    if (!byDate[d]) byDate[d] = [];
    byDate[d].push(l);
  });
  const dates = Object.keys(byDate).sort();

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Календарь занятий</h1>
      {dates.length === 0 && <div className="opacity-70">Уроков нет</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {dates.map((d) => (
          <div key={d} className="p-4 rounded-2xl shadow bg-white space-y-3">
            <div className="font-medium">{new Date(d).toLocaleDateString()}</div>
            <div className="flex flex-wrap gap-2">
              {byDate[d].map((l) => (
                <div
                  key={l.id}
                  className="px-3 py-2 rounded-xl text-sm bg-indigo-100 hover:bg-indigo-200 cursor-pointer"
                  title={`Ученик ${l.student_id}`}
                >
                  <div className="font-medium">{l.topic || "Без темы"}</div>
                  <div className="opacity-70">Ученик {l.student_id}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
