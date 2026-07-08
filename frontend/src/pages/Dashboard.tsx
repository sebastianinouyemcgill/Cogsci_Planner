import { useEffect, useMemo, useState } from "react";

import { useCompletedCourses } from "../context/CompletedCoursesContext";
import { getRequirementsProgress } from "../api/requirements";
import type { RequirementsProgressResponse } from "../types/requirement";

const STREAM_REQUIRED_CREDITS = 18;
const COMPLEMENTARY_REQUIRED_CREDITS = 12;
const LEVEL_400_PLUS_REQUIRED_CREDITS = 15;
const ARTS_REQUIRED_CREDITS = 21;
const SCIENCE_REQUIRED_CREDITS = 21;

const STREAM_ORDER = [
  "Computer Science",
  "Neuroscience",
  "Psychology",
  "Linguistics",
  "Philosophy",
];

function ProgressRow({
  label,
  numerator,
  denominator,
}: {
  label: string;
  numerator: number;
  denominator: number;
}) {
  const pct = denominator > 0 ? Math.min(1, numerator / denominator) * 100 : 0;

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ marginBottom: 6 }}>
        {label}: {numerator} / {denominator}
      </div>
      <div style={{ height: 10, background: "#eee", borderRadius: 6 }}>
        <div
          style={{
            height: "100%",
            width: `${pct}%`,
            background: "#444",
            borderRadius: 6,
          }}
        />
      </div>
    </div>
  );
}

function Dashboard() {
  const { completedCourseIds } = useCompletedCourses();

  const [progress, setProgress] = useState<RequirementsProgressResponse | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const completedIdsPayload = useMemo(
    () => ({
      completedCourseIds,
    }),
    [completedCourseIds]
  );

  useEffect(() => {
    async function run() {
      setLoading(true);
      setError(null);
      try {
        const data = await getRequirementsProgress(
          completedIdsPayload.completedCourseIds
        );
        setProgress(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load progress");
      } finally {
        setLoading(false);
      }
    }

    run();
  }, [completedIdsPayload]);

  const requiredAreasCount = progress?.areas.required_areas.length ?? 0;
  const completedAreasCount = progress?.areas.completed_areas.length ?? 0;

  return (
    <div style={{ padding: 20 }}>
      <h1>Dashboard</h1>

      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}

      {loading || progress === null ? <p>Loading...</p> : null}

      {progress ? (
        <>
          <ProgressRow
            label="Required Areas"
            numerator={completedAreasCount}
            denominator={requiredAreasCount}
          />

          {STREAM_ORDER.map((streamName) => (
            <ProgressRow
              key={streamName}
              label={`Stream: ${streamName}`}
              numerator={progress.stream_complementary.stream_credits[streamName] ?? 0}
              denominator={STREAM_REQUIRED_CREDITS}
            />
          ))}

          <ProgressRow
            label="Complementary Credits"
            numerator={progress.stream_complementary.complementary_credits}
            denominator={COMPLEMENTARY_REQUIRED_CREDITS}
          />

          <ProgressRow
            label="400+ Credits"
            numerator={progress.level_400_plus.credits}
            denominator={LEVEL_400_PLUS_REQUIRED_CREDITS}
          />

          <ProgressRow
            label="Arts Credits"
            numerator={progress.arts_science.arts_credits}
            denominator={ARTS_REQUIRED_CREDITS}
          />

          <ProgressRow
            label="Science Credits"
            numerator={progress.arts_science.science_credits}
            denominator={SCIENCE_REQUIRED_CREDITS}
          />
        </>
      ) : null}
    </div>
  );
}

export default Dashboard;

