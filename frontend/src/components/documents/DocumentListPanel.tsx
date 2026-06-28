import type { DocumentRecord } from '../../types/document';

type Props = {
  documents: DocumentRecord[];
  onIngest: (documentId: string) => Promise<void>;
  loadingDocumentId?: string | null;
};

export function DocumentListPanel({ documents, onIngest, loadingDocumentId }: Props) {
  return (
    <section style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
      <h2 style={{ fontSize: 18, marginTop: 0 }}>Uploaded docs</h2>
      {documents.length === 0 ? (
        <p style={{ color: '#5d6675' }}>No documents uploaded yet.</p>
      ) : (
        <div style={{ display: 'grid', gap: 10 }}>
          {documents.map((document) => (
            <article key={document.document_id} style={{ borderTop: '1px solid #eceff3', paddingTop: 10 }}>
              <strong>{document.original_filename}</strong>
              <p style={{ color: '#5d6675', margin: '4px 0' }}>
                {document.document_type} · {document.status} · chunks {document.chunks_count} · embeddings{' '}
                {document.embeddings_count}
              </p>
              {document.error_message && <p style={{ color: '#b42318', margin: '4px 0' }}>{document.error_message}</p>}
              <button
                type="button"
                onClick={() => onIngest(document.document_id)}
                disabled={loadingDocumentId === document.document_id}
                style={{ padding: '8px 12px' }}
              >
                {loadingDocumentId === document.document_id ? 'Ingesting...' : 'Ingest'}
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
