import type { DeliveryLog } from '../../types/delivery';

type Props = {
  logs: DeliveryLog[];
};

export function DeliveryLogPanel({ logs }: Props) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Delivery logs</h2>
      {!logs.length ? <p style={{ color: '#5d6675' }}>No explicit send attempts yet.</p> : null}
      <div style={{ display: 'grid', gap: 10 }}>
        {logs.map((log) => (
          <article key={log.delivery_id} style={{ borderBottom: '1px solid #eceff3', paddingBottom: 10 }}>
            <strong>{log.channel}</strong> · {log.status} · {log.provider}
            {log.provider_message_id ? <p>Provider message: {log.provider_message_id}</p> : null}
            {log.error_message ? <p style={{ color: '#b42318' }}>{log.error_message}</p> : null}
            <small>{log.created_at}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
