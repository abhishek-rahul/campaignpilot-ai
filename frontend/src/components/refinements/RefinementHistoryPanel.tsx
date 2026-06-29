import type { RefinementRecord } from '../../types/refinement';

type RefinementHistoryPanelProps = {
  refinements: RefinementRecord[];
};

export function RefinementHistoryPanel({ refinements }: RefinementHistoryPanelProps) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Refinement History</h2>
      {refinements.length === 0 ? (
        <p style={{ color: '#5d6675' }}>Brief and variant refinements will appear here.</p>
      ) : (
        <div style={{ display: 'grid', gap: 10 }}>
          {refinements.map((item) => (
            <article key={item.refinement_id} style={{ border: '1px solid #e1e5eb', borderRadius: 8, padding: 12 }}>
              <strong>{item.refinement_type}</strong>
              <p style={{ margin: '6px 0' }}>{item.user_feedback}</p>
              <dl style={{ display: 'grid', gap: 4, margin: 0 }}>
                <Meta label="Source" value={`${item.source_type}${item.source_id ? ` · ${item.source_id}` : ''}`} />
                <Meta label="Status" value={item.status} />
                <Meta label="Created" value={new Date(item.created_at).toLocaleString()} />
              </dl>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <>
      <dt style={{ fontWeight: 700 }}>{label}</dt>
      <dd style={{ marginLeft: 0 }}>{value}</dd>
    </>
  );
}
