import { useEffect, useState } from "react";
import { getOverview, getStudents } from "../lib/api";

export default function Dashboard() {
  const [ov, setOv] = useState<any>();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const [o, s] = await Promise.all([getOverview(), getStudents()]);
      setOv({ ...o, students: s });
      setLoading(false);
    })();
  }, []);

  if (loading) return <div className="p-6">Загрузка…</div>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Дашборд</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="p-4 rounded-2xl shadow bg-white">
          Ученики: {ov.students?.length || 0}
        </div>
        <div className="p-4 rounded-2xl shadow bg-white">
          Уроки/нед: {ov.lessons_count || 0}
        </div>
        <div className="p-4 rounded-2xl shadow bg-white">Вып. ДЗ: —</div>
        <div className="p-4 rounded-2xl shadow bg-white">
          Температура: {ov.engagement_temp}
        </div>
      </div>

      {/* Календарь-мозаика (пока статик для MVP) */}
    </div>
  );
}
