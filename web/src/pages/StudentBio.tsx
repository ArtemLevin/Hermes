import { useEffect, useState } from "react";

type Bio = {
  student_id: number;
  started_at?: string | null;
  goals?: string | null;
  strengths?: string | null;
  weaknesses?: string | null;
  notes?: string | null;
  updated_at?: string;
};

const API = (p: string) => `${import.meta.env.VITE_API_URL || "http://localhost:8000"}${p}`;

export default function StudentBio({ studentId = 1 }: { studentId?: number }) {
  const [bio, setBio] = useState<Bio | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [avatar, setAvatar] = useState<string>("warrior"); // warrior|mage|explorer

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        setErr(null);
        const b = await fetch(API(`/students/${studentId}/bio`)).then((r) => r.json());
        setBio(b);
      } catch (e: any) {
        setErr(e?.message || "Ошибка загрузки");
      } finally {
        setLoading(false);
      }
    })();
  }, [studentId]);

  const save = async () => {
    if (!bio) return;
    try {
      setSaving(true);
      setErr(null);
      const r = await fetch(API(`/students/${studentId}/bio`), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          started_at: bio.started_at || null,
          goals: bio.goals || null,
          strengths: bio.strengths || null,
          weaknesses: bio.weaknesses || null,
          notes: bio.notes || null,
        }),
      });
      if (!r.ok) throw new Error("Не удалось сохранить");
      const b = await r.json();
      setBio(b);
    } catch (e: any) {
      setErr(e?.message || "Ошибка сохранения");
    } finally {
      setSaving(false);
    }
  };

  const saveAvatar = async () => {
    try {
      setSaving(true);
      setErr(null);
      const r = await fetch(API(`/students/${studentId}/avatar`), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ avatar_theme_code: avatar }),
      });
      if (!r.ok) throw new Error("Не удалось установить аватар");
    } catch (e: any) {
      setErr(e?.message || "Ошибка установки аватара");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-6">Загрузка…</div>;
  if (err) return <div className="p-6 text-red-600">Ошибка: {err}</div>;
  if (!bio) return <div className="p-6">Данные не найдены</div>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Биография ученика #{studentId}</h1>

      {/* Основные поля */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 rounded-2xl shadow bg-white space-y-2">
          <label className="block text-sm">
            Дата старта
            <input
              type="date"
              value={bio.started_at || ""}
              onChange={(e) => setBio({ ...bio, started_at: e.target.value })}
              className="mt-1 w-full px-3 py-2 rounded-xl border"
            />
          </label>

          <label className="block text-sm">
            Цели
            <textarea
              rows={3}
              value={bio.goals || ""}
              onChange={(e) => setBio({ ...bio, goals: e.target.value })}
              className="mt-1 w-full px-3 py-2 rounded-xl border"
              placeholder="Поступить в вуз, поднять матан до 80+ баллов…"
            />
          </label>

          <label className="block text-sm">
            Сильные стороны
            <textarea
              rows={3}
              value={bio.strengths || ""}
              onChange={(e) => setBio({ ...bio, strengths: e.target.value })}
              className="mt-1 w-full px-3 py-2 rounded-xl border"
              placeholder="Логика, скорость счета…"
            />
          </label>

          <label className="block text-sm">
            Слабые стороны
            <textarea
              rows={3}
              value={bio.weaknesses || ""}
              onChange={(e) => setBio({ ...bio, weaknesses: e.target.value })}
              className="mt-1 w-full px-3 py-2 rounded-xl border"
              placeholder="Геометрия, невнимательность…"
            />
          </label>

          <label className="block text-sm">
            Заметки
            <textarea
              rows={3}
              value={bio.notes || ""}
              onChange={(e) => setBio({ ...bio, notes: e.target.value })}
              className="mt-1 w-full px-3 py-2 rounded-xl border"
              placeholder="Связаться с родителями по расписанию…"
            />
          </label>

          <div className="pt-2">
            <button
              onClick={save}
              disabled={saving}
              className="px-4 py-2 rounded-xl bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
            >
              Сохранить
            </button>
            <span className="ml-3 text-sm opacity-60">
              Обновлено: {bio.updated_at ? new Date(bio.updated_at).toLocaleString() : "—"}
            </span>
          </div>
        </div>

        {/* Аватар */}
        <div className="p-4 rounded-2xl shadow bg-white space-y-3">
          <div className="font-medium">Аватар героя</div>
          <div className="flex gap-3">
            {[
              { code: "warrior", label: "Воин 🛡️" },
              { code: "mage", label: "Маг 🪄" },
              { code: "explorer", label: "Исследователь 🧭" },
            ].map((opt) => (
              <label key={opt.code} className="flex items-center gap-2">
                <input
                  type="radio"
                  name="avatar"
                  value={opt.code}
                  checked={avatar === opt.code}
                  onChange={() => setAvatar(opt.code)}
                />
                <span>{opt.label}</span>
              </label>
            ))}
          </div>
          <button
            onClick={saveAvatar}
            disabled={saving}
            className="px-4 py-2 rounded-xl bg-amber-500 text-white hover:bg-amber-600 disabled:opacity-60"
          >
            Установить аватар
          </button>
          <p className="text-xs opacity-70">
            Темы и иконки предзаданы в сид-скрипте (warrior/mage/explorer).
          </p>
        </div>
      </div>
    </div>
  );
}
