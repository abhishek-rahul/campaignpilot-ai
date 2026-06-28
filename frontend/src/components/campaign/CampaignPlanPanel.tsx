type Props = {
  plan: Record<string, unknown> | null;
  onGenerate: () => Promise<void>;
  disabled?: boolean;
  loading?: boolean;
};

export function CampaignPlanPanel({ plan, onGenerate, disabled, loading }: Props) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'center' }}>
        <h2 style={{ fontSize: 18, margin: 0 }}>Campaign plan</h2>
        <button type="button" onClick={onGenerate} disabled={disabled || loading} style={{ padding: '8px 12px' }}>
          {loading ? 'Generating...' : 'Generate Plan'}
        </button>
      </div>
      {!plan ? (
        <p style={{ color: '#5d6675' }}>No plan generated yet.</p>
      ) : (
        <div style={{ display: 'grid', gap: 8, marginTop: 12 }}>
          {Object.entries(plan).map(([key, value]) => (
            <div key={key}>
              <strong>{key.replace(/_/g, ' ')}</strong>
              <p style={{ margin: '4px 0 0' }}>{Array.isArray(value) ? value.join(', ') : String(value ?? '')}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
