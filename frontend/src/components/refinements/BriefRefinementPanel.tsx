import { FormEvent, useState } from 'react';

import type { RefineBriefResponse } from '../../types/refinement';

type BriefRefinementPanelProps = {
  disabled: boolean;
  loading: boolean;
  result: RefineBriefResponse | null;
  onSubmit: (feedback: string, useRagContext: boolean, apply: boolean) => Promise<void>;
};

export function BriefRefinementPanel({ disabled, loading, result, onSubmit }: BriefRefinementPanelProps) {
  const [feedback, setFeedback] = useState('');
  const [useRagContext, setUseRagContext] = useState(true);
  const [apply, setApply] = useState(true);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit(feedback, useRagContext, apply);
    setFeedback('');
  }

  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Brief Refinement</h2>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 10 }}>
        <textarea
          value={feedback}
          onChange={(event) => setFeedback(event.target.value)}
          rows={3}
          placeholder="Example: Make the tone more premium and less pushy."
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
        <label>
          <input
            type="checkbox"
            checked={apply}
            onChange={(event) => setApply(event.target.checked)}
            disabled={disabled || loading}
          />{' '}
          Apply to campaign brief
        </label>
        <button type="submit" disabled={disabled || loading || !feedback.trim()} style={{ padding: '10px 14px' }}>
          {loading ? 'Refining...' : 'Refine Brief'}
        </button>
      </form>
      {result && (
        <div style={{ marginTop: 12, display: 'grid', gap: 8 }}>
          <strong>{result.applied ? 'Applied refinement' : 'Generated proposal'}</strong>
          <p style={{ margin: 0 }}>Status: {result.campaign_status}</p>
          {result.selected_variant_id === null && result.campaign_status === 'NEEDS_REVIEW' && (
            <p style={{ margin: 0, color: '#b42318' }}>Approval and payloads must be rerun for the updated brief.</p>
          )}
        </div>
      )}
    </section>
  );
}
