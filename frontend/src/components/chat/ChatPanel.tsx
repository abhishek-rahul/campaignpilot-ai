import type { ConversationMessage } from '../../types/chat';

type ChatPanelProps = {
  messages: ConversationMessage[];
};

export function ChatPanel({ messages }: ChatPanelProps) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Campaign Chat</h2>
      <div style={{ display: 'grid', gap: 10 }}>
        {messages.length === 0 ? (
          <p style={{ color: '#5d6675' }}>Start with a campaign idea.</p>
        ) : (
          messages.map((message) => (
            <article
              key={message.message_id}
              style={{
                background: message.sender === 'AI_AGENT' ? '#f4f7fb' : '#eef8f1',
                border: '1px solid #e1e5eb',
                borderRadius: 8,
                padding: 12
              }}
            >
              <strong>{message.sender === 'AI_AGENT' ? 'AI Assistant' : 'Campaign Manager'}</strong>
              <p style={{ marginBottom: 0 }}>{message.message_text}</p>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
