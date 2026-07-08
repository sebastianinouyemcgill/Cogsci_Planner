import {
  BrowserRouter,
  Link,
  Routes,
  Route,
} from "react-router-dom";

import CourseCatalog from "./pages/CourseCatalog";
import Dashboard from "./pages/Dashboard";
import Planner from "./pages/Planner";


function App() {
  return (
    <BrowserRouter>

      <div style={{ padding: 12, borderBottom: "1px solid #ddd", marginBottom: 10 }}>
        <Link to="/courses" style={{ marginRight: 12 }}>
          Courses
        </Link>
        <Link to="/dashboard" style={{ marginRight: 12 }}>
          Dashboard
        </Link>
        <Link to="/planner">Planner</Link>
      </div>

      <Routes>

        <Route
          path="/courses"
          element={<CourseCatalog />}
        />

        <Route
          path="/dashboard"
          element={<Dashboard />}
        />

        <Route
          path="/planner"
          element={<Planner />}
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;