import type { LlmTracePreview } from '../../types/observability';

type Props = {
  traces: LlmTracePreview[];
};

export function LlmTraceListPanel({ traces }: Props) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>LLM Trace Preview</h2>
      {traces.length === 0 ? (
        <p style={{ color: '#5d6675' }}>LLM traces will appear after chat, plan, variants, or refinements.</p>
      ) : (
        <div style={{ display: 'grid', gap: 10 }}>
          {traces.slice(0, 8).map((trace) => (
            <article key={trace.trace_id} style={{ border: '1px solid #e1e5eb', borderRadius: 8, padding: 12 }}>
              <strong>{trace.operation_name}</strong>
              <p style={{ margin: '4px 0', color: '#5d6675' }}>
                {trace.model_name} · {trace.used_mock ? 'mock' : 'real'} · {trace.status} · {trace.latency_ms ?? 'n/a'}ms
              </p>
              {trace.prompt_preview && <p style={{ margin: '4px 0' }}>Prompt: {trace.prompt_preview}</p>}
              {trace.response_preview && <p style={{ margin: '4px 0' }}>Response: {trace.response_preview}</p>}
              {trace.error_message && <p style={{ margin: '4px 0', color: '#b42318' }}>{trace.error_message}</p>}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
