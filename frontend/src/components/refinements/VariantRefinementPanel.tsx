import { FormEvent, useState } from 'react';

import type { MessageVariant } from '../../types/variant';

type VariantRefinementPanelProps = {
  variants: MessageVariant[];
  disabled: boolean;
  loading: boolean;
  onRefineVariant: (variantId: string, feedback: string, useRagContext: boolean) => Promise<void>;
  onRegenerateVariants: (feedback: string, useRagContext: boolean) => Promise<void>;
};

export function VariantRefinementPanel({
  variants,
  disabled,
  loading,
  onRefineVariant,
  onRegenerateVariants
}: VariantRefinementPanelProps) {
  const [variantId, setVariantId] = useState('');
  const [feedback, setFeedback] = useState('');
  const [useRagContext, setUseRagContext] = useState(true);

  async function handleRefine(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!variantId) return;
    await onRefineVariant(variantId, feedback, useRagContext);
    setFeedback('');
  }

  async function handleRegenerate() {
    await onRegenerateVariants(feedback, useRagContext);
    setFeedback('');
  }

  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Variant Refinement</h2>
      <form onSubmit={handleRefine} style={{ display: 'grid', gap: 10 }}>
        <select
          value={variantId}
          onChange={(event) => setVariantId(event.target.value)}
          disabled={disabled || loading || variants.length === 0}
          style={{ padding: 10 }}
        >
          <option value="">Select source variant</option>
          {variants.map((variant) => (
            <option key={variant.variant_id} value={variant.variant_id}>
              {variant.variant_name} · {variant.channel}
            </option>
          ))}
        </select>
        <textarea
          value={feedback}
          onChange={(event) => setFeedback(event.target.value)}
          rows={3}
          placeholder="Example: Make it shorter and softer."
          disabled={disabled || loading}
          style={{ boxSizing: 'border-box', width: '100%', padding: 10, resize: 'vertical' }}
        />
        <label>
          <input
            type="checkbox"
            checked={useRagContext}
            onChange={(event) => setUseRagContext(event.target.checked)}
            disabled={disabled || loading}
          />{' '}
          Use RAG context
        </label>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <button type="submit" disabled={disabled || loading || !variantId || !feedback.trim()} style={{ padding: '10px 14px' }}>
            {loading ? 'Working...' : 'Refine Selected Variant'}
          </button>
          <button
            type="button"
            onClick={() => void handleRegenerate()}
            disabled={disabled || loading || !feedback.trim()}
            style={{ padding: '10px 14px' }}
          >
            Regenerate Variants from Feedback
          </button>
        </div>
      </form>
    </section>
  );
}
