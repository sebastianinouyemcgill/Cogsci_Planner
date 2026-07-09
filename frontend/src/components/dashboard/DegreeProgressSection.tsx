import type { RequirementProgressBreakdown } from "@/types/requirement";
import {
  ARTS_REQUIRED_CREDITS,
  COMPLEMENTARY_REQUIRED_CREDITS,
  LEVEL_400_PLUS_REQUIRED_CREDITS,
  SCIENCE_REQUIRED_CREDITS,
  STREAM_ORDER,
  STREAM_REQUIRED_CREDITS,
} from "@/lib/dashboard-utils";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { DualProgressBar } from "@/components/dashboard/DualProgressBar";

type DegreeProgressSectionProps = {
  completed: RequirementProgressBreakdown;
  projected: RequirementProgressBreakdown;
  requiredAreasCount: number;
  activeStream: string | null;
  honours: boolean;
};

export function DegreeProgressSection({
  completed,
  projected,
  requiredAreasCount,
  activeStream,
  honours,
}: DegreeProgressSectionProps) {
  const officialCompleted = completed.official_stream_complementary;
  const officialProjected = projected.official_stream_complementary;

  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold tracking-tight">Degree progress</h2>
        <p className="text-sm text-muted-foreground">
          Solid bars are completed; lighter fill shows projected (planned) credit.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card size="sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Core & official</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <DualProgressBar
              label="Required areas"
              completedNumerator={completed.areas.completed_areas.length}
              projectedNumerator={projected.areas.completed_areas.length}
              denominator={requiredAreasCount}
              compact
            />
            <DualProgressBar
              label={
                activeStream
                  ? `Official stream (${activeStream})`
                  : "Official stream"
              }
              completedNumerator={officialCompleted?.stream_credits ?? 0}
              projectedNumerator={officialProjected?.stream_credits ?? 0}
              denominator={
                officialProjected?.stream_credit_required ?? STREAM_REQUIRED_CREDITS
              }
              compact
            />
            <DualProgressBar
              label="Complementary (official)"
              completedNumerator={officialCompleted?.complementary_credits ?? 0}
              projectedNumerator={officialProjected?.complementary_credits ?? 0}
              denominator={
                officialProjected?.complementary_credit_required ??
                COMPLEMENTARY_REQUIRED_CREDITS
              }
              compact
            />
            {honours && projected.honours_research ? (
              <DualProgressBar
                label="Honours research"
                completedNumerator={completed.honours_research?.credits ?? 0}
                projectedNumerator={projected.honours_research.credits}
                denominator={projected.honours_research.required_credits}
                compact
              />
            ) : null}
          </CardContent>
        </Card>

        <Card size="sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">
              Faculty & level requirements
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <DualProgressBar
              label="400+ credits"
              completedNumerator={completed.level_400_plus.credits}
              projectedNumerator={projected.level_400_plus.credits}
              denominator={LEVEL_400_PLUS_REQUIRED_CREDITS}
              compact
            />
            <DualProgressBar
              label="Arts credits"
              completedNumerator={completed.arts_science.arts_credits}
              projectedNumerator={projected.arts_science.arts_credits}
              denominator={ARTS_REQUIRED_CREDITS}
              compact
            />
            <DualProgressBar
              label="Science credits"
              completedNumerator={completed.arts_science.science_credits}
              projectedNumerator={projected.arts_science.science_credits}
              denominator={SCIENCE_REQUIRED_CREDITS}
              compact
            />
          </CardContent>
        </Card>
      </div>

      <Card size="sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">
            Stream exploration (all streams)
          </CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {STREAM_ORDER.map((streamName) => (
            <DualProgressBar
              key={streamName}
              label={streamName}
              completedNumerator={
                completed.stream_complementary.stream_credits[streamName] ?? 0
              }
              projectedNumerator={
                projected.stream_complementary.stream_credits[streamName] ?? 0
              }
              denominator={STREAM_REQUIRED_CREDITS}
              compact
            />
          ))}
        </CardContent>
      </Card>
    </section>
  );
}
