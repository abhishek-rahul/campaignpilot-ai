import type { ObservabilitySummary } from '../../types/observability';

type Props = {
  summary: ObservabilitySummary | null;
  loading?: boolean;
  onRefresh: () => Promise<void>;
};

export function ObservabilitySummaryPanel({ summary, loading, onRefresh }: Props) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>Observability Summary</h2>
        <button type="button" onClick={onRefresh} disabled={loading} style={{ padding: '8px 12px' }}>
          {loading ? 'Refreshing...' : 'Refresh Debug Data'}
        </button>
      </div>
      {!summary ? (
        <p style={{ color: '#5d6675' }}>Create a campaign to inspect debug counts.</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: 10, marginTop: 12 }}>
          <Metric label="LLM Traces" value={summary.llm_trace_count} />
          <Metric label="RAG Contexts" value={summary.retrieved_context_count} />
          <Metric label="Compliance" value={summary.compliance_result_count} />
          <Metric label="Tool Calls" value={summary.tool_call_count} />
          <Metric label="Payloads" value={summary.payload_count} />
          <Metric label="Deliveries" value={summary.delivery_log_count} />
          <Metric label="Refinements" value={summary.refinement_count} />
          <Metric label="Evaluations" value={summary.evaluation_count} />
        </div>
      )}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <strong style={{ display: 'block', fontSize: 22 }}>{value}</strong>
      <span style={{ color: '#5d6675' }}>{label}</span>
    </div>
  );
}
