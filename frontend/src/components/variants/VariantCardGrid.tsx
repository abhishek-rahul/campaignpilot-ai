import type { MessageVariant } from '../../types/variant';

type VariantCardGridProps = {
  variants: MessageVariant[];
};

export function VariantCardGrid({ variants }: VariantCardGridProps) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Generated Variants</h2>
      {variants.length === 0 ? (
        <p style={{ color: '#5d6675' }}>Generated variants will appear here.</p>
      ) : (
        <div style={{ display: 'grid', gap: 12, gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))' }}>
          {variants.map((variant) => (
            <article key={variant.variant_id} style={{ border: '1px solid #e1e5eb', borderRadius: 8, padding: 14 }}>
              <h3 style={{ marginTop: 0 }}>{variant.variant_name}</h3>
              <p>{variant.message_body}</p>
              <dl style={{ display: 'grid', gap: 4, marginBottom: 0 }}>
                <Meta label="Channel" value={variant.channel} />
                <Meta label="Tone" value={variant.tone || 'Not set'} />
                <Meta label="Reason" value={variant.reason || 'Not set'} />
                <Meta label="Risk" value={variant.risk_level || 'Not set'} />
                <Meta label="Status" value={variant.status} />
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
