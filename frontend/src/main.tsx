import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./index.css";
import App from "./App.tsx";
import { PlannerProvider } from "./context/PlannerContext";
import { CourseStatusProvider } from "./context/CourseStatusContext";
import { TooltipProvider } from "@/components/ui/tooltip";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <TooltipProvider>
      <PlannerProvider>
        <CourseStatusProvider>
          <App />
        </CourseStatusProvider>
      </PlannerProvider>
    </TooltipProvider>
  </StrictMode>,
);
