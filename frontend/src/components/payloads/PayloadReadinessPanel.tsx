import type { PayloadReadiness } from '../../types/payload';

type Props = {
  readiness: PayloadReadiness | null;
};

export function PayloadReadinessPanel({ readiness }: Props) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Payload readiness</h2>
      {!readiness ? (
        <p style={{ color: '#5d6675' }}>Approve a variant to unlock payload generation.</p>
      ) : (
        <>
          <p style={{ marginTop: 0 }}>
            <strong>Status:</strong> {readiness.ready ? 'Ready' : 'Blocked'}
          </p>
          <dl style={{ display: 'grid', gap: 4, margin: 0 }}>
            <Meta label="Campaign" value={readiness.campaign_status || 'Unknown'} />
            <Meta label="Selected variant" value={readiness.selected_variant_id || 'Missing'} />
            <Meta label="Variant status" value={readiness.selected_variant_status || 'Unknown'} />
          </dl>
          {readiness.missing_requirements.length ? (
            <ul style={{ marginBottom: 0 }}>
              {readiness.missing_requirements.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : null}
        </>
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
