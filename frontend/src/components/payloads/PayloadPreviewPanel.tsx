import type { ChannelPayload } from '../../types/payload';

type Props = {
  payloads: ChannelPayload[];
  sendingPayloadId: string | null;
  onSendTelegram: (payloadId: string) => void;
};

export function PayloadPreviewPanel({ payloads, sendingPayloadId, onSendTelegram }: Props) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Payload preview</h2>
      {!payloads.length ? <p style={{ color: '#5d6675' }}>No payloads generated yet.</p> : null}
      <div style={{ display: 'grid', gap: 12 }}>
        {payloads.map((payload) => (
          <article key={payload.payload_id} style={{ border: '1px solid #eceff3', borderRadius: 8, padding: 12 }}>
            <h3 style={{ marginTop: 0 }}>{payload.channel}</h3>
            <p>
              <strong>{payload.payload_type}</strong> · {payload.status}
            </p>
            <p style={{ whiteSpace: 'pre-wrap' }}>{payload.preview_text}</p>
            <pre style={{ overflowX: 'auto', background: '#f6f7f9', padding: 10 }}>
              {JSON.stringify(payload.payload_json, null, 2)}
            </pre>
            {payload.channel === 'telegram' ? (
              <button
                type="button"
                disabled={sendingPayloadId === payload.payload_id}
                onClick={() => onSendTelegram(payload.payload_id)}
              >
                {sendingPayloadId === payload.payload_id ? 'Sending...' : 'Send Telegram'}
              </button>
            ) : (
              <p style={{ color: '#5d6675' }}>Mock payload only. No WhatsApp send in Slice 4.</p>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
