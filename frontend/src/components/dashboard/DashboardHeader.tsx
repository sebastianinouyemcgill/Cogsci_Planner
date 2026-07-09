import { RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";

type DashboardHeaderProps = {
  honours: boolean;
  onHonoursChange: (value: boolean) => void;
  onClearAll: () => void;
  totalSelectedCredits: number;
  degreeCreditTarget: number;
};

export function DashboardHeader({
  honours,
  onHonoursChange,
  onClearAll,
  totalSelectedCredits,
  degreeCreditTarget,
}: DashboardHeaderProps) {
  return (
    <header className="space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
            Degree Dashboard
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            McGill Cognitive Science · {totalSelectedCredits}/{degreeCreditTarget}{" "}
            credits selected
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <Checkbox
              id="honours-toggle"
              checked={honours}
              onCheckedChange={(checked) => onHonoursChange(checked === true)}
            />
            <Label htmlFor="honours-toggle" className="text-sm font-normal">
              Honours (60 cr)
            </Label>
          </div>
          <Separator orientation="vertical" className="hidden h-5 sm:block" />
          <Button type="button" variant="outline" size="sm" onClick={onClearAll}>
            <RotateCcw className="size-3.5" />
            Clear all
          </Button>
        </div>
      </div>
    </header>
  );
}
