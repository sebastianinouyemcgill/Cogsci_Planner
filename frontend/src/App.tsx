import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import CourseCatalog from "./pages/CourseCatalog";
import Planner from "./pages/Planner";


function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/courses"
          element={<CourseCatalog />}
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