import type { EvaluationResult } from '../../types/evaluation';

type Props = {
  evaluations: EvaluationResult[];
};

export function EvaluationHistoryPanel({ evaluations }: Props) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Evaluation History</h2>
      {evaluations.length === 0 ? (
        <p style={{ color: '#5d6675' }}>Saved evaluation results will appear here.</p>
      ) : (
        <div style={{ display: 'grid', gap: 10 }}>
          {evaluations.slice(0, 10).map((evaluation) => (
            <article key={evaluation.evaluation_id} style={{ border: '1px solid #e1e5eb', borderRadius: 8, padding: 12 }}>
              <strong>
                {evaluation.evaluation_type} · {evaluation.grade} · {evaluation.score}/100
              </strong>
              <p style={{ margin: '4px 0', color: '#5d6675' }}>
                {evaluation.variant_id || 'campaign readiness'} · {evaluation.passed ? 'passed' : 'needs work'}
              </p>
              <p style={{ margin: 0 }}>{evaluation.recommendation}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
