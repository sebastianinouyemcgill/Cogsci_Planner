export type CourseProgressStatus = "planned" | "completed";

export type CourseBucketAllocation = {
  eligible_buckets: string[];
  allocated_bucket: string | null;
};

export type RequirementProgressBreakdown = {
  arts_science: {
    arts_credits: number;
    science_credits: number;
  };
  level_400_plus: {
    threshold: number;
    credits: number;
    course_ids: number[];
  };
  stream_complementary: {
    stream_credits: Record<string, number>;
    complementary_credits: number;
    course_bucket: Record<number, string>;
    course_allocations: Record<number, CourseBucketAllocation>;
  };
  official_stream_complementary?: {
    declared_stream: string | null;
    stream_is_provisional: boolean;
    provisional_stream: string | null;
    stream_credits: number;
    stream_credit_required: number;
    complementary_credits: number;
    complementary_credit_required: number;
    course_bucket: Record<number, string>;
    course_allocations: Record<number, CourseBucketAllocation>;
  };
  electives?: {
    credits: number;
    course_ids: number[];
  };
  areas: {
    required_areas: string[];
    completed_areas: string[];
    area_course_ids?: Record<string, number>;
  };
  honours_research?: {
    required_credits: number;
    credits: number;
    remaining_credits: number;
    course_ids: number[];
    satisfied: boolean;
  };
};

export type RequirementsProgressResponse = {
  completed: RequirementProgressBreakdown;
  projected: RequirementProgressBreakdown;
};
