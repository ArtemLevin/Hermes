import { useEffect, useState } from "react";

type Assignment = {
  id: number;
  status: string;
  title?: string;
  reward_type?: string;
  due_at?: string;
};

type RadarItem = { student_id: number; name: string; score: number; level: number };

interface Props {
  studentId: number; // передайте id ученика при рендере компонента
}

const API = (p: string) => `${import.meta.env.VITE_API_URL || "http://localhost:8000"}${p}`;

export default function StudentProfile({ studentId }: Props) {
  const [loading, setLoading] = useState(true);
  const [studentName, setStudentName] = useState<string>("");
  const [level, setLevel] = useState<number>(1);
  const [forecast, setForecast] = useState<number | null>(null);
  const [tempo, setTempo] = useState<number | null>(null);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [mems, setMems] = useState<{ id: number; url: string; caption?: string }[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        setError(null);

        // Получаем студента из списка (MVP: отдельной ручки нет)
        const studs = await fetch(API("/students")).then((r) => r.json());
        const me = (studs as { id: number; name: string; level: number }[]).find((s) => s.id === studentId);
        if (me) {
          setStudentName(me.name);
          setLevel(me.level);
        } else {
          setStudentName(`ID ${studentId}`);
        }

        // Прогноз экзамена
        const ef = await fetch(API(`/analytics/exam-forecast?student_id=${studentId}`)).then((r) => r.json());
        setForecast(ef?.predicted_score ?? null);

        // Темпо-ритм (частота ДЗ/день)
        const tt = await fetch(API(`/analytics/tempo?student_id=${studentId}&days=30`)).then((r) => r.json());
        setTempo(tt?.frequency_per_day ?? null);

        // Список ДЗ
        const list = await fetch(API(`/assignments?student_id=${studentId}`)).then((r) => r.json());
        setAssignments(list?.items ?? []);

        // Мемы по студенту
        const mm = await fetch(API(`/mems?student_id=${studentId}`)).then((r) => r.json());
        setMems(mm?.items ?? []);
      } catch (e: any) {
        setError(e?.message || "Ошибка загрузки");
      } finally {
        setLoading(false);
      }
    })();
  }, [studentId]);

  if (loading) return <div className="p-6">Загрузка…</div>;
  if (error) return <div className="p-6 text-red-600">Ошибка: {error}</div>;

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Профиль: {studentName}</h1>
        <div className="text-sm opacity-70">ID: {studentId}</div>
      </header>

      {/* Карточки метрик */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="p-4 rounded-2xl shadow bg-white">
          <div className="text-xs opacity-60">Уровень</div>
          <div className="text-2xl font-semibold">{level}</div>
        </div>
        <div className="p-4 rounded-2xl shadow bg-white">
          <div className="text-xs opacity-60">Прогноз экзамена</div>
          <div className="text-2xl font-semibold">{forecast ?? "—"}</div>
        </div>
        <div className="p-4 rounded-2xl shadow bg-white">
          <div className="text-xs opacity-60">Темпо-ритм (ДЗ/день)</div>
          <div className="text-2xl font-semibold">
            {tempo !== null ? tempo.toFixed(2) : "—"}
          </div>
        </div>
      </section>

      {/* Список ДЗ */}
      <section className="space-y-2">
        <h2 className="text-xl font-semibold">Домашние задания</h2>
        {assignments.length === 0 ? (
          <div className="text-sm opacity-70">Пока нет заданий</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {assignments.map((a) => (
              <div key={a.id} className="p-4 rounded-2xl shadow bg-white">
                <div className="text-sm opacity-60">#{a.id}</div>
                <div className="font-medium">{a.title || "Без названия"}</div>
                <div className="text-sm">
                  Статус: <span className="font-medium">{a.status}</span>
                </div>
                <div className="text-sm">
                  Награда: {a.reward_type || "—"}{" "}
                  {a.due_at ? `· дедлайн: ${new Date(a.due_at).toLocaleString()}` : ""}
                </div>
                <div className="mt-2 flex gap-2">
                  <button
                    className="px-3 py-1 rounded-lg bg-gray-100 hover:bg-gray-200 text-sm"
                    onClick={async () => {
                      await fetch(API(`/assignments/${a.id}/start`), { method: "POST" });
                      // обновим локально
                      setAssignments((prev) =>
                        prev.map((x) => (x.id === a.id ? { ...x, status: "in_progress" } : x)),
                      );
                    }}
                  >
                    Начать
                  </button>
                  <button
                    className="px-3 py-1 rounded-lg bg-green-500 text-white hover:bg-green-600 text-sm"
                    onClick={async () => {
                      const r = await fetch(API(`/assignments/${a.id}/submit`), {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ artifacts: [], grade: 5 }),
                      });
                      if (r.ok) {
                        setAssignments((prev) =>
                          prev.map((x) => (x.id === a.id ? { ...x, status: "done" } : x)),
                        );
                      }
                    }}
                  >
                    Сдать
                  </button>
                  <button
                    className="px-3 py-1 rounded-lg bg-amber-500 text-white hover:bg-amber-600 text-sm"
                    onClick={async () => {
                      await fetch(API(`/assignments/${a.id}/mark_late`), { method: "POST" });
                      setAssignments((prev) =>
                        prev.map((x) => (x.id === a.id ? { ...x, status: "late" } : x)),
                      );
                    }}
                  >
                    Просрочить
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Мемы */}
      <section className="space-y-2">
        <h2 className="text-xl font-semibold">Мем-похвала</h2>
        {mems.length === 0 ? (
          <div className="text-sm opacity-70">Мемов пока нет</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {mems.map((m) => (
              <a
                key={m.id}
                href={m.url}
                target="_blank"
                rel="noreferrer"
                className="block p-3 rounded-2xl shadow bg-white hover:shadow-md transition"
              >
                <div className="text-sm mb-1">{m.caption || "Мем"}</div>
                <div className="text-xs opacity-60 break-all">{m.url}</div>
              </a>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
