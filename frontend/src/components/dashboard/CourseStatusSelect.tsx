import {
  useCourseStatus,
  type CourseSelectionStatus,
} from "@/context/CourseStatusContext";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const STATUS_OPTIONS: { value: CourseSelectionStatus; label: string }[] = [
  { value: "not_taken", label: "Not taken" },
  { value: "planned", label: "Planned" },
  { value: "completed", label: "Completed" },
];

type CourseStatusSelectProps = {
  courseCode: string;
  size?: "sm" | "default";
  className?: string;
};

export function CourseStatusSelect({
  courseCode,
  size = "sm",
  className,
}: CourseStatusSelectProps) {
  const { getStatus, setStatus } = useCourseStatus();
  const status = getStatus(courseCode);

  return (
    <Select
      value={status}
      onValueChange={(value) =>
        setStatus(courseCode, value as CourseSelectionStatus)
      }
    >
      <SelectTrigger size={size} className={className ?? "w-full"}>
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {STATUS_OPTIONS.map((option) => (
          <SelectItem key={option.value} value={option.value}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
