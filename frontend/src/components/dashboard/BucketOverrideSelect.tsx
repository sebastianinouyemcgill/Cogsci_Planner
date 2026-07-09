import { useCourseStatus } from "@/context/CourseStatusContext";
import type { CourseBucketAllocation } from "@/types/requirement";
import { formatBucketLabel } from "@/lib/dashboard-utils";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type BucketOverrideSelectProps = {
  courseCode: string;
  allocation: CourseBucketAllocation;
  overrideError?: string;
  onOverrideAttempt: (
    courseCode: string,
    override: string | null,
    previousOverride: string | null
  ) => void;
};

export function BucketOverrideSelect({
  courseCode,
  allocation,
  overrideError,
  onOverrideAttempt,
}: BucketOverrideSelectProps) {
  const { getBucketOverride, setBucketOverride } = useCourseStatus();
  const selectedOverride = getBucketOverride(courseCode);
  const autoLabel = formatBucketLabel(allocation.allocated_bucket);

  return (
    <div className="space-y-1">
      <Select
        value={selectedOverride ?? "__auto__"}
        onValueChange={(value) => {
          const nextOverride = value === "__auto__" ? null : value;
          onOverrideAttempt(courseCode, nextOverride, selectedOverride);
          setBucketOverride(courseCode, nextOverride);
        }}
      >
        <SelectTrigger size="sm" className="w-full">
          <SelectValue>
            {selectedOverride
              ? formatBucketLabel(selectedOverride)
              : `Auto (${autoLabel})`}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="__auto__">Auto ({autoLabel})</SelectItem>
          {allocation.eligible_buckets.map((bucket) => (
            <SelectItem key={bucket} value={bucket}>
              {formatBucketLabel(bucket)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {overrideError ? (
        <p className="text-xs text-destructive">{overrideError}</p>
      ) : null}
    </div>
  );
}
