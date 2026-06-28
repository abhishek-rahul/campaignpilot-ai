import type { CampaignBrief } from '../../types/campaign';

type CampaignBriefPreviewProps = {
  brief: CampaignBrief | null;
};

export function CampaignBriefPreview({ brief }: CampaignBriefPreviewProps) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Brief Preview</h2>
      {!brief ? (
        <p style={{ color: '#5d6675' }}>The extracted brief will appear after the first chat message.</p>
      ) : (
        <div style={{ display: 'grid', gap: 8 }}>
          <Field label="Status" value={brief.brief_status} />
          <Field label="Goal" value={brief.goal} />
          <Field label="Audience" value={brief.target_audience} />
          <Field label="Offer" value={brief.offer_details} />
          <Field label="Tone" value={brief.tone} />
          <Field label="Channels" value={brief.preferred_channels.join(', ') || null} />
          <Field label="CTA" value={brief.cta_link} />
          <Field label="Expiry" value={brief.expiry_date} />
          {brief.missing_fields.length > 0 && (
            <div>
              <strong>Missing fields</strong>
              <ul style={{ marginTop: 6 }}>
                {brief.missing_fields.map((field) => (
                  <li key={field}>{field}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

function Field({ label, value }: { label: string; value: string | null }) {
  return (
    <div>
      <strong>{label}: </strong>
      <span>{value || 'Not captured yet'}</span>
    </div>
  );
}
