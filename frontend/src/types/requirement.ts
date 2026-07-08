export type RequirementsProgressResponse = {
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
  };
  areas: {
    required_areas: string[];
    completed_areas: string[];
  };
};

