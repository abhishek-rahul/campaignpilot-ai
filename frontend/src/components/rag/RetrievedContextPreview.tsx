import type { RetrievedContext } from '../../types/rag';

type Props = {
  contexts: RetrievedContext[];
  onRefresh: () => Promise<void>;
  disabled?: boolean;
  loading?: boolean;
};

export function RetrievedContextPreview({ contexts, onRefresh, disabled, loading }: Props) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'center' }}>
        <h2 style={{ fontSize: 18, margin: 0 }}>Retrieved context</h2>
        <button type="button" onClick={onRefresh} disabled={disabled || loading} style={{ padding: '8px 12px' }}>
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      {contexts.length === 0 ? (
        <p style={{ color: '#5d6675' }}>No context retrieved yet.</p>
      ) : (
        <div style={{ display: 'grid', gap: 10, marginTop: 12 }}>
          {contexts.map((context) => (
            <article key={context.context_id} style={{ borderTop: '1px solid #eceff3', paddingTop: 10 }}>
              <strong>
                #{context.rank_position} {context.document_id || 'document'}
              </strong>
              <p style={{ color: '#5d6675', margin: '4px 0' }}>
                score {context.score ?? 'n/a'} · {context.used_for}
              </p>
              <p style={{ margin: 0 }}>{context.retrieved_text.slice(0, 220)}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
