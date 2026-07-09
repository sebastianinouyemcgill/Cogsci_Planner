import { BrowserRouter, Link, Navigate, Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Planner from "./pages/Planner";

function App() {
  return (
    <BrowserRouter>
      <div
        style={{
          padding: 12,
          borderBottom: "1px solid var(--border)",
          marginBottom: 10,
        }}
      >
        <Link to="/dashboard" style={{ marginRight: 12 }}>
          Dashboard
        </Link>
        <Link to="/planner">Planner</Link>
      </div>

      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/planner" element={<Planner />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
