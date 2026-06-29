type Props = {
  ready: boolean;
  selectedChannels: string[];
  regenerate: boolean;
  loading: boolean;
  onToggleChannel: (channel: string) => void;
  onRegenerateChange: (enabled: boolean) => void;
  onGenerate: () => void;
};

export function PayloadGenerationPanel({
  ready,
  selectedChannels,
  regenerate,
  loading,
  onToggleChannel,
  onRegenerateChange,
  onGenerate
}: Props) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Channel payloads</h2>
      <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
        <label>
          <input
            type="checkbox"
            checked={selectedChannels.includes('telegram')}
            onChange={() => onToggleChannel('telegram')}
          />{' '}
          Telegram
        </label>
        <label>
          <input
            type="checkbox"
            checked={selectedChannels.includes('whatsapp_mock')}
            onChange={() => onToggleChannel('whatsapp_mock')}
          />{' '}
          WhatsApp mock
        </label>
        <label>
          <input type="checkbox" checked={regenerate} onChange={(event) => onRegenerateChange(event.target.checked)} />{' '}
          Regenerate
        </label>
      </div>
      <button type="button" disabled={!ready || loading} onClick={onGenerate} style={{ marginTop: 12, padding: '10px 14px' }}>
        {loading ? 'Generating...' : 'Generate Channel Payloads'}
      </button>
    </section>
  );
}
