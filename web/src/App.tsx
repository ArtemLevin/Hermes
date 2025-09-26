import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Assignments from "./pages/Assignments";
import StudentProfile from "./pages/StudentProfile";
import Heatmap from "./pages/Heatmap";
import StudentBio from "./pages/StudentBio";
import PriorityRadar from "./pages/PriorityRadar";
import Finance from "./pages/Finance";
import Calendar from "./pages/Calendar";

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen">
        <nav className="sticky top-0 z-10 bg-white/80 backdrop-blur border-b">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-4">
            <Link to="/" className="font-semibold">Hermes MVP</Link>
            <div className="flex flex-wrap gap-3 text-sm">
              <Link to="/" className="hover:underline">Дашборд</Link>
              <Link to="/assignments" className="hover:underline">ДЗ</Link>
              <Link to="/students/1" className="hover:underline">Профиль (ID 1)</Link>
              <Link to="/students/1/bio" className="hover:underline">Биография</Link>
              <Link to="/heatmap" className="hover:underline">Теплокарта</Link>
              <Link to="/radar" className="hover:underline">Радар внимания</Link>
              <Link to="/finance" className="hover:underline">Финансы</Link>
              <Link to="/calendar" className="hover:underline">Календарь</Link>
            </div>
          </div>
        </nav>

        <main className="max-w-6xl mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/assignments" element={<Assignments />} />
            <Route path="/students/:id" element={<StudentProfileWrapper />} />
            <Route path="/students/:id/bio" element={<StudentBioWrapper />} />
            <Route path="/heatmap" element={<Heatmap studentId={1} />} />
            <Route path="/radar" element={<PriorityRadar />} />
            <Route path="/finance" element={<Finance />} />
            <Route path="/calendar" element={<Calendar />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

// Вспомогательные обёртки для чтения :id из URL
function StudentProfileWrapper() {
  const id = Number(window.location.pathname.split("/")[2]);
  return <StudentProfile studentId={id || 1} />;
}
function StudentBioWrapper() {
  const id = Number(window.location.pathname.split("/")[2]);
  return <StudentBio studentId={id || 1} />;
}
