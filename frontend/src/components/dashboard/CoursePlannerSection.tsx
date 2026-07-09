import { Link } from "react-router-dom";
import { CalendarDays } from "lucide-react";

import { buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function CoursePlannerSection() {
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold tracking-tight">Course planner</h2>
        <p className="text-sm text-muted-foreground">
          Semester planning and schedule view.
        </p>
      </div>

      <Card size="sm" className="max-w-xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <CalendarDays className="size-4" />
            Semester planner
          </CardTitle>
          <CardDescription>
            Organize selected courses across terms. Full planner integration
            will expand here.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Use the dedicated planner page to arrange courses by semester.
          </p>
        </CardContent>
        <CardFooter>
          <Link
            to="/planner"
            className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
          >
            Open planner
          </Link>
        </CardFooter>
      </Card>
    </section>
  );
}
