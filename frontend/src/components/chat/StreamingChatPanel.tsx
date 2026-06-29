type StreamingChatPanelProps = {
  text: string;
  active: boolean;
};

export function StreamingChatPanel({ text, active }: StreamingChatPanelProps) {
  if (!text && !active) return null;
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Streaming Response</h2>
      <div
        style={{
          minHeight: 72,
          border: '1px solid #e1e5eb',
          borderRadius: 8,
          padding: 12,
          background: '#fbfcfe',
          whiteSpace: 'pre-wrap'
        }}
      >
        {text || 'Waiting for tokens...'}
      </div>
      {active && <p style={{ color: '#5d6675', marginBottom: 0 }}>Streaming...</p>}
    </section>
  );
}
