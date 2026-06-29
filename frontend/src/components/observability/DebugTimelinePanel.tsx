import type { DebugTimelineEvent } from '../../types/observability';

type Props = {
  events: DebugTimelineEvent[];
};

export function DebugTimelinePanel({ events }: Props) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Debug Timeline</h2>
      {events.length === 0 ? (
        <p style={{ color: '#5d6675' }}>Campaign events will appear here chronologically.</p>
      ) : (
        <div style={{ display: 'grid', gap: 10 }}>
          {events.slice(-20).map((event) => (
            <article key={event.event_id} style={{ borderTop: '1px solid #eceff3', paddingTop: 10 }}>
              <strong>{event.title}</strong>
              <p style={{ margin: '4px 0', color: '#5d6675' }}>
                {event.event_type} · {new Date(event.created_at).toLocaleString()}
              </p>
              <p style={{ margin: 0 }}>{event.summary}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
