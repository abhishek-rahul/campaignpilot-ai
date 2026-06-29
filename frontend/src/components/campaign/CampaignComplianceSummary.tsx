import type { CampaignComplianceSummary as Summary } from '../../types/compliance';

type Props = {
  summary: Summary | null;
};

export function CampaignComplianceSummary({ summary }: Props) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Compliance Summary</h2>
      {!summary ? (
        <p style={{ color: '#5d6675' }}>Run compliance checks to see campaign-level counts.</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: 10 }}>
          <Metric label="Variants" value={summary.total_variants} />
          <Metric label="Passed" value={summary.passed_count} />
          <Metric label="Warnings" value={summary.warning_count} />
          <Metric label="Failed" value={summary.failed_count} />
          <Metric label="Approved" value={summary.approved_count} />
          <Metric label="Rejected" value={summary.rejected_count} />
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
