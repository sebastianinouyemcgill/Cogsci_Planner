import { GraduationCap, Layers, Sparkles, Target } from "lucide-react";

import type { RequirementProgressBreakdown } from "@/types/requirement";
import {
  COMPLEMENTARY_REQUIRED_CREDITS,
  LEVEL_400_PLUS_REQUIRED_CREDITS,
  STREAM_REQUIRED_CREDITS,
  overallCompletionPct,
  ratio,
} from "@/lib/dashboard-utils";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress, ProgressTrack, ProgressIndicator } from "@/components/ui/progress";

type SummaryCardsProps = {
  projected: RequirementProgressBreakdown | undefined;
  honours: boolean;
  activeStream: string | null;
  declaredStream: string | null;
  isProvisionalStream: boolean;
  requiredAreasCount: number;
};

export function SummaryCards({
  projected,
  honours,
  activeStream,
  declaredStream,
  isProvisionalStream,
  requiredAreasCount,
}: SummaryCardsProps) {
  const overallPct = projected ? overallCompletionPct(projected, honours) : 0;
  const official = projected?.official_stream_complementary;
  const areasDone = projected?.areas.completed_areas.length ?? 0;
  const areasRemaining = Math.max(0, requiredAreasCount - areasDone);
  const level400 = projected?.level_400_plus.credits ?? 0;
  const streamCredits = official?.stream_credits ?? 0;
  const streamRequired =
    official?.stream_credit_required ?? STREAM_REQUIRED_CREDITS;
  const complementaryCredits = official?.complementary_credits ?? 0;
  const complementaryRequired =
    official?.complementary_credit_required ?? COMPLEMENTARY_REQUIRED_CREDITS;
  const streamRemaining = Math.max(0, streamRequired - streamCredits);
  const complementaryRemaining = Math.max(
    0,
    complementaryRequired - complementaryCredits
  );

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <Card size="sm">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <Target className="size-4" />
            Overall progress
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-3xl font-semibold tabular-nums tracking-tight">
            {projected ? `${overallPct}%` : "—"}
          </p>
          <Progress value={overallPct}>
            <ProgressTrack className="h-1.5">
              <ProgressIndicator />
            </ProgressTrack>
          </Progress>
        </CardContent>
      </Card>

      <Card size="sm">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <Layers className="size-4" />
            Stream
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-lg font-semibold leading-tight">
            {activeStream ?? "Not set"}
          </p>
          {activeStream ? (
            <Badge variant={declaredStream ? "default" : "secondary"}>
              {declaredStream ? "Declared" : "Auto-selected"}
            </Badge>
          ) : (
            <Badge variant="outline">Select below</Badge>
          )}
          {isProvisionalStream && !declaredStream ? (
            <p className="text-xs text-muted-foreground">
              Based on your current courses
            </p>
          ) : null}
        </CardContent>
      </Card>

      <Card size="sm">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <GraduationCap className="size-4" />
            400-level credits
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-3xl font-semibold tabular-nums tracking-tight">
            {level400}
            <span className="text-base font-normal text-muted-foreground">
              /{LEVEL_400_PLUS_REQUIRED_CREDITS}
            </span>
          </p>
          <Progress
            value={ratio(level400, LEVEL_400_PLUS_REQUIRED_CREDITS) * 100}
          >
            <ProgressTrack className="h-1.5">
              <ProgressIndicator />
            </ProgressTrack>
          </Progress>
        </CardContent>
      </Card>

      <Card size="sm">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <Sparkles className="size-4" />
            Remaining
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1.5 text-sm">
          <div className="flex justify-between gap-2">
            <span className="text-muted-foreground">Core areas</span>
            <span className="font-medium tabular-nums">{areasRemaining}</span>
          </div>
          <div className="flex justify-between gap-2">
            <span className="text-muted-foreground">Stream credits</span>
            <span className="font-medium tabular-nums">{streamRemaining}</span>
          </div>
          <div className="flex justify-between gap-2">
            <span className="text-muted-foreground">Complementary</span>
            <span className="font-medium tabular-nums">
              {complementaryRemaining}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
