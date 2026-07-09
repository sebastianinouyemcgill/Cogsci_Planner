import type { Course } from "@/types/course";
import type { RequirementProgressBreakdown } from "@/types/requirement";
import { streamHighlightFor } from "@/lib/dashboard-utils";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { StreamCourseRow } from "@/components/dashboard/StreamCourseRow";
import { ScrollArea } from "@/components/ui/scroll-area";

type StreamProgressSectionProps = {
  coursesByStream: Map<string, Course[]>;
  researchCourses: Course[];
  honoursResearchCourses: Course[];
  projected: RequirementProgressBreakdown | undefined;
  declaredStream: string | null;
  overrideErrors: Record<string, string>;
  onOverrideAttempt: (
    courseCode: string,
    override: string | null,
    previousOverride: string | null
  ) => void;
  honours: boolean;
};

export function StreamProgressSection({
  coursesByStream,
  researchCourses,
  honoursResearchCourses,
  projected,
  declaredStream,
  overrideErrors,
  onOverrideAttempt,
  honours,
}: StreamProgressSectionProps) {
  const officialProjected = projected?.official_stream_complementary;

  const streamEntries = Array.from(coursesByStream.entries()).map(
    ([streamName, courses]) => {
      const highlight = streamHighlightFor(
        streamName,
        declaredStream,
        officialProjected
      );
      return { streamName, courses, highlight };
    }
  );

  const accordionItems = [
    ...streamEntries.map(({ streamName, courses, highlight }) => ({
      id: streamName,
      title: streamName,
      badge:
        highlight === "declared"
          ? "Your stream"
          : highlight === "provisional"
            ? "Best fit"
            : null,
      courses,
    })),
    {
      id: "research",
      title: "Research",
      badge: null as string | null,
      courses: researchCourses,
    },
    ...(honours
      ? [
          {
            id: "honours-research",
            title: "Honours research",
            badge: "Honours" as string | null,
            courses: honoursResearchCourses,
          },
        ]
      : []),
  ];

  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold tracking-tight">Stream progress</h2>
        <p className="text-sm text-muted-foreground">
          Mark stream and research courses as planned or completed.
        </p>
      </div>

      <Accordion className="rounded-xl border border-border/60 bg-card px-4">
        {accordionItems.map((item) => (
          <AccordionItem key={item.id} value={item.id}>
            <AccordionTrigger className="hover:no-underline">
              <div className="flex items-center gap-2">
                <span>{item.title}</span>
                <span className="text-xs font-normal text-muted-foreground">
                  ({item.courses.length})
                </span>
                {item.badge ? (
                  <Badge variant="secondary" className="ml-1">
                    {item.badge}
                  </Badge>
                ) : null}
              </div>
            </AccordionTrigger>
            <AccordionContent>
              {item.courses.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No courses in this group.
                </p>
              ) : (
                <ScrollArea className="h-[420px] pr-3">
                  <div className="space-y-2 pb-2">
                    {item.courses.map((course) => (
                      <StreamCourseRow
                        key={course.code}
                        course={course}
                        projected={projected}
                        overrideErrors={overrideErrors}
                        onOverrideAttempt={onOverrideAttempt}
                      />
                    ))}
                  </div>
                </ScrollArea>
              )}
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </section>
  );
}
