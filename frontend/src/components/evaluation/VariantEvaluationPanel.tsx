import type { EvaluationResult } from '../../types/evaluation';
import type { MessageVariant } from '../../types/variant';

type Props = {
  variants: MessageVariant[];
  latestByVariantId: Record<string, EvaluationResult>;
  busyVariantId: string | null;
  onEvaluate: (variantId: string) => Promise<void>;
  onEvaluateReadiness: () => Promise<void>;
  readinessLoading?: boolean;
};

export function VariantEvaluationPanel({
  variants,
  latestByVariantId,
  busyVariantId,
  onEvaluate,
  onEvaluateReadiness,
  readinessLoading
}: Props) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>Variant Evaluation</h2>
        <button type="button" onClick={onEvaluateReadiness} disabled={readinessLoading} style={{ padding: '8px 12px' }}>
          {readinessLoading ? 'Evaluating...' : 'Evaluate Readiness'}
        </button>
      </div>
      {variants.length === 0 ? (
        <p style={{ color: '#5d6675' }}>Generate variants before running quality evaluation.</p>
      ) : (
        <div style={{ display: 'grid', gap: 10, marginTop: 12 }}>
          {variants.map((variant) => {
            const evaluation = latestByVariantId[variant.variant_id];
            return (
              <article key={variant.variant_id} style={{ border: '1px solid #e1e5eb', borderRadius: 8, padding: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'center' }}>
                  <strong>{variant.variant_name}</strong>
                  <button
                    type="button"
                    onClick={() => void onEvaluate(variant.variant_id)}
                    disabled={busyVariantId === variant.variant_id}
                    style={{ padding: '8px 12px' }}
                  >
                    {busyVariantId === variant.variant_id ? 'Evaluating...' : 'Run Evaluation'}
                  </button>
                </div>
                {evaluation && (
                  <div style={{ marginTop: 8 }}>
                    <strong>
                      {evaluation.grade} · {evaluation.score}/100 · {evaluation.passed ? 'Passed' : 'Needs work'}
                    </strong>
                    <p style={{ margin: '4px 0' }}>{evaluation.recommendation}</p>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
