export type EvaluationCheck = {
  check_id: string;
  passed: boolean;
  score: number;
  max_score: number;
  message: string;
  high_risk: boolean;
};

export type EvaluationResult = {
  evaluation_id: string;
  campaign_id: string;
  variant_id: string | null;
  evaluation_type: string;
  score: number;
  grade: string;
  passed: boolean;
  checks: EvaluationCheck[];
  recommendation: string;
  created_at: string;
};

export type EvaluationList = {
  campaign_id: string;
  evaluations: EvaluationResult[];
};
