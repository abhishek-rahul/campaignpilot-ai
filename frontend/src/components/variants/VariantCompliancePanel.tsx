import type { ApprovalActionResponse, ComplianceResult } from '../../types/compliance';
import type { MessageVariant } from '../../types/variant';

type Props = {
  variant: MessageVariant;
  compliance?: ComplianceResult;
  isBusy?: boolean;
  onRunCompliance: (variantId: string) => Promise<void>;
  onApprove: (variantId: string, reason: string | null, allowHighRiskOverride: boolean) => Promise<ApprovalActionResponse | void>;
  onReject: (variantId: string, reason: string | null) => Promise<ApprovalActionResponse | void>;
};

export function VariantCompliancePanel({
  variant,
  compliance,
  isBusy,
  onRunCompliance,
  onApprove,
  onReject
}: Props) {
  async function handleApprove() {
    const reason = window.prompt('Approval reason', 'Looks good');
    const allowOverride =
      compliance?.status === 'FAILED' ? window.confirm('This variant failed compliance. Approve with override?') : false;
    await onApprove(variant.variant_id, reason, allowOverride);
  }

  async function handleReject() {
    const reason = window.prompt('Reject reason', 'Needs copy edit');
    await onReject(variant.variant_id, reason);
  }

  return (
    <section style={{ borderTop: '1px solid #eceff3', marginTop: 12, paddingTop: 12 }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 10 }}>
        <button type="button" onClick={() => onRunCompliance(variant.variant_id)} disabled={isBusy}>
          {isBusy ? 'Checking...' : 'Run Compliance Check'}
        </button>
        <button type="button" onClick={handleApprove} disabled={isBusy || variant.status === 'APPROVED'}>
          Approve
        </button>
        <button type="button" onClick={handleReject} disabled={isBusy || variant.status === 'REJECTED'}>
          Reject
        </button>
      </div>

      <dl style={{ display: 'grid', gap: 4, margin: 0 }}>
        <Meta label="Compliance" value={compliance?.status || variant.latest_compliance_status || 'Not checked'} />
        <Meta label="Recommendation" value={compliance?.recommendation || 'Not checked yet'} />
      </dl>

      {compliance?.issues.length ? (
        <ul style={{ margin: '10px 0 0', paddingLeft: 18 }}>
          {compliance.issues.map((issue, index) => (
            <li key={`${issue.rule_id}-${index}`}>
              <strong>{issue.severity}:</strong> {issue.message}
              {issue.evidence ? ` (${issue.evidence})` : ''}
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <>
      <dt style={{ fontWeight: 700 }}>{label}</dt>
      <dd style={{ marginLeft: 0 }}>{value}</dd>
    </>
  );
}
