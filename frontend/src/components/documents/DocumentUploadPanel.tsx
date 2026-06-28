import { FormEvent, useState } from 'react';

type Props = {
  disabled?: boolean;
  onUpload: (file: File, documentType: string) => Promise<void>;
};

export function DocumentUploadPanel({ disabled, onUpload }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState('brand_guideline');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) return;
    setLoading(true);
    try {
      await onUpload(file, documentType);
      setFile(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ fontSize: 18, marginTop: 0 }}>Documents</h2>
      <div style={{ display: 'grid', gap: 10 }}>
        <input
          type="file"
          accept=".txt,.md,.pdf"
          disabled={disabled || loading}
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />
        <select
          value={documentType}
          disabled={disabled || loading}
          onChange={(event) => setDocumentType(event.target.value)}
          style={{ padding: 9 }}
        >
          <option value="brand_guideline">Brand guideline</option>
          <option value="product_doc">Product document</option>
          <option value="campaign_reference">Campaign reference</option>
        </select>
        <button type="submit" disabled={!file || disabled || loading} style={{ padding: '10px 14px' }}>
          {loading ? 'Uploading...' : 'Upload'}
        </button>
      </div>
    </form>
  );
}
