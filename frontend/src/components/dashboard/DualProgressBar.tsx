import { cn } from "@/lib/utils";
import { ratio } from "@/lib/dashboard-utils";

type DualProgressBarProps = {
  label: string;
  completedNumerator: number;
  projectedNumerator: number;
  denominator: number;
  className?: string;
  compact?: boolean;
};

export function DualProgressBar({
  label,
  completedNumerator,
  projectedNumerator,
  denominator,
  className,
  compact = false,
}: DualProgressBarProps) {
  const completedPct = ratio(completedNumerator, denominator) * 100;
  const projectedPct = ratio(projectedNumerator, denominator) * 100;
  const hasProjection = projectedNumerator > completedNumerator;

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-baseline justify-between gap-2">
        <span
          className={cn(
            "font-medium text-foreground",
            compact ? "text-xs" : "text-sm"
          )}
        >
          {label}
        </span>
        <span className="text-xs tabular-nums text-muted-foreground">
          {completedNumerator}/{denominator}
          {hasProjection ? ` → ${projectedNumerator}` : ""}
        </span>
      </div>
      <div className="relative h-2 overflow-hidden rounded-full bg-muted">
        {hasProjection ? (
          <div
            className="absolute inset-y-0 left-0 rounded-full bg-muted-foreground/25"
            style={{ width: `${projectedPct}%` }}
          />
        ) : null}
        <div
          className="absolute inset-y-0 left-0 rounded-full bg-primary transition-all"
          style={{ width: `${completedPct}%` }}
        />
      </div>
    </div>
  );
}
