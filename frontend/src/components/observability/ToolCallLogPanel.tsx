import type { ToolCallPreview } from '../../types/observability';

type Props = {
  toolCalls: ToolCallPreview[];
};

export function ToolCallLogPanel({ toolCalls }: Props) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Tool Calls</h2>
      {toolCalls.length === 0 ? (
        <p style={{ color: '#5d6675' }}>Compliance rule executions will appear here.</p>
      ) : (
        <div style={{ display: 'grid', gap: 10 }}>
          {toolCalls.slice(0, 8).map((toolCall) => (
            <article key={toolCall.tool_call_id} style={{ border: '1px solid #e1e5eb', borderRadius: 8, padding: 12 }}>
              <strong>{toolCall.tool_name}</strong>
              <p style={{ margin: '4px 0', color: '#5d6675' }}>
                {toolCall.status} · {toolCall.latency_ms ?? 'n/a'}ms
              </p>
              {toolCall.error_message && <p style={{ margin: 0, color: '#b42318' }}>{toolCall.error_message}</p>}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
