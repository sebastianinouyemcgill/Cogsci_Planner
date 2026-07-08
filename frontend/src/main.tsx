import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./index.css";
import App from "./App.tsx";
import { PlannerProvider } from "./context/PlannerContext";
import { CompletedCoursesProvider } from "./context/CompletedCoursesContext";


createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <PlannerProvider>
      <CompletedCoursesProvider>
        <App />
      </CompletedCoursesProvider>
    </PlannerProvider>
  </StrictMode>,
);