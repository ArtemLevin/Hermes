import { useEffect, useState } from "react";

type Invoice = {
  id: number;
  student_id: number;
  amount: number | string;
  status: string;
  due_date?: string | null;
  created_at: string;
  notes?: string | null;
};

type Payment = {
  id: number;
  student_id: number;
  invoice_id?: number | null;
  amount: number | string;
  status: string;
  method?: string | null;
  paid_at?: string | null;
  created_at: string;
};

const API = (p: string) =>
  `${import.meta.env.VITE_API_URL || "http://localhost:8000"}${p}`;

export default function Finance() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  // формы
  const [invStudent, setInvStudent] = useState<number>(1);
  const [invAmount, setInvAmount] = useState<string>("3000");
  const [invDue, setInvDue] = useState<string>("");

  const [payStudent, setPayStudent] = useState<number>(1);
  const [payInvoice, setPayInvoice] = useState<string>("");
  const [payAmount, setPayAmount] = useState<string>("3000");
  const [payMethod, setPayMethod] = useState<string>("cash");

  const loadAll = async () => {
    try {
      setLoading(true);
      setErr(null);
      const [inv, pay] = await Promise.all([
        fetch(API("/finance/invoices")).then((r) => r.json()),
        fetch(API("/finance/payments")).then((r) => r.json()),
      ]);
      setInvoices(inv?.items || []);
      setPayments(pay?.items || []);
    } catch (e: any) {
      setErr(e?.message || "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const createInvoice = async () => {
    const body: any = {
      student_id: invStudent,
      amount: Number(invAmount),
    };
    if (invDue) body.due_date = invDue;
    const r = await fetch(API("/finance/invoices"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (r.ok) {
      await loadAll();
      setInvAmount("3000");
      setInvDue("");
    }
  };

  const markPaid = async (id: number) => {
    const r = await fetch(API(`/finance/invoices/${id}/mark_paid`), {
      method: "POST",
    });
    if (r.ok) loadAll();
  };

  const createPayment = async () => {
    const body = {
      student_id: payStudent,
      invoice_id: payInvoice ? Number(payInvoice) : null,
      amount: Number(payAmount),
      method: payMethod,
    };
    const r = await fetch(API("/finance/payments"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (r.ok) {
      await loadAll();
      setPayInvoice("");
    }
  };

  if (loading) return <div className="p-6">Загрузка…</div>;
  if (err) return <div className="p-6 text-red-600">Ошибка: {err}</div>;

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-2xl font-semibold">Финансы</h1>

      {/* Создать инвойс */}
      <section className="p-4 rounded-2xl shadow bg-white space-y-3">
        <h2 className="text-lg font-medium">Создать инвойс</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <label className="text-sm">
            ID ученика
            <input
              type="number"
              className="mt-1 w-full px-3 py-2 rounded-xl border"
              value={invStudent}
              onChange={(e) => setInvStudent(Number(e.target.value))}
            />
          </label>
          <label className="text-sm">
            Сумма
            <input
              type="number"
              className="mt-1 w-full px-3 py-2 rounded-xl border"
              value={invAmount}
              onChange={(e) => setInvAmount(e.target.value)}
            />
          </label>
          <label className="text-sm">
            Дедлайн (опц.)
            <input
              type="date"
              className="mt-1 w-full px-3 py-2 rounded-xl border"
              value={invDue}
              onChange={(e) => setInvDue(e.target.value)}
            />
          </label>
          <div className="flex items-end">
            <button
              className="px-4 py-2 rounded-xl bg-blue-600 text-white hover:bg-blue-700"
              onClick={createInvoice}
            >
              Создать
            </button>
          </div>
        </div>
        <p className="text-xs opacity-70">
          Напоминание об оплате шедулится за 3 дня до дедлайна (через RQ).
        </p>
      </section>

      {/* Инвойсы */}
      <section className="space-y-2">
        <h2 className="text-lg font-medium">Инвойсы</h2>
        {invoices.length === 0 ? (
          <div className="text-sm opacity-70">Инвойсов пока нет</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {invoices.map((x) => (
              <div key={x.id} className="p-4 rounded-2xl shadow bg-white">
                <div className="flex items-center justify-between">
                  <div className="font-medium">#{x.id} · ученик {x.student_id}</div>
                  <span
                    className={`px-2 py-0.5 rounded-lg text-xs ${
                      x.status === "paid"
                        ? "bg-green-100 text-green-700"
                        : x.status === "overdue"
                        ? "bg-amber-100 text-amber-700"
                        : "bg-gray-100 text-gray-700"
                    }`}
                  >
                    {x.status}
                  </span>
                </div>
                <div className="text-sm opacity-80">
                  Сумма: {x.amount} · Создан: {new Date(x.created_at).toLocaleString()}
                  {x.due_date ? ` · Дедлайн: ${x.due_date}` : ""}
                </div>
                {x.status !== "paid" && (
                  <div className="mt-2">
                    <button
                      className="px-3 py-1 rounded-lg bg-green-500 text-white hover:bg-green-600 text-sm"
                      onClick={() => markPaid(x.id)}
                    >
                      Отметить оплаченным
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Создать оплату */}
      <section className="p-4 rounded-2xl shadow bg-white space-y-3">
        <h2 className="text-lg font-medium">Зачислить оплату (ручной учёт)</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <label className="text-sm">
            ID ученика
            <input
              type="number"
              className="mt-1 w-full px-3 py-2 rounded-xl border"
              value={payStudent}
              onChange={(e) => setPayStudent(Number(e.target.value))}
            />
          </label>
          <label className="text-sm">
            Инвойс (опц.)
            <input
              type="number"
              className="mt-1 w-full px-3 py-2 rounded-xl border"
              placeholder="id инвойса"
              value={payInvoice}
              onChange={(e) => setPayInvoice(e.target.value)}
            />
          </label>
          <label className="text-sm">
            Сумма
            <input
              type="number"
              className="mt-1 w-full px-3 py-2 rounded-xl border"
              value={payAmount}
              onChange={(e) => setPayAmount(e.target.value)}
            />
          </label>
          <label className="text-sm">
            Метод
            <select
              className="mt-1 w-full px-3 py-2 rounded-xl border"
              value={payMethod}
              onChange={(e) => setPayMethod(e.target.value)}
            >
              <option value="cash">cash</option>
              <option value="transfer">transfer</option>
              <option value="card">card</option>
            </select>
          </label>
          <div className="flex items-end">
            <button
              className="px-4 py-2 rounded-xl bg-emerald-600 text-white hover:bg-emerald-700"
              onClick={createPayment}
            >
              Зачислить
            </button>
          </div>
        </div>
      </section>

      {/* Оплаты */}
      <section className="space-y-2">
        <h2 className="text-lg font-medium">Оплаты</h2>
        {payments.length === 0 ? (
          <div className="text-sm opacity-70">Оплат пока нет</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {payments.map((p) => (
              <div key={p.id} className="p-4 rounded-2xl shadow bg-white">
                <div className="flex items-center justify-between">
                  <div className="font-medium">#{p.id} · ученик {p.student_id}</div>
                  <span
                    className={`px-2 py-0.5 rounded-lg text-xs ${
                      p.status === "paid"
                        ? "bg-green-100 text-green-700"
                        : p.status === "refunded"
                        ? "bg-amber-100 text-amber-700"
                        : "bg-gray-100 text-gray-700"
                    }`}
                  >
                    {p.status}
                  </span>
                </div>
                <div className="text-sm opacity-80">
                  Сумма: {p.amount} · Метод: {p.method || "—"} ·{" "}
                  {p.paid_at ? `Оплачено: ${new Date(p.paid_at).toLocaleString()}` : "—"}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
