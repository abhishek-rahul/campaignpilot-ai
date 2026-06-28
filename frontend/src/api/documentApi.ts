import { apiGet, apiPost, apiPostForm } from './apiClient';
import type {
  DocumentListResponse,
  DocumentRecord,
  IngestDocumentRequest,
  IngestDocumentResponse
} from '../types/document';

export function uploadDocument(payload: {
  file: File;
  documentType: string;
  campaignId?: string | null;
}): Promise<DocumentRecord> {
  const form = new FormData();
  form.append('file', payload.file);
  form.append('document_type', payload.documentType);
  if (payload.campaignId) {
    form.append('campaign_id', payload.campaignId);
  }
  return apiPostForm<DocumentRecord>('/documents/upload', form);
}

export function listDocuments(campaignId?: string | null): Promise<DocumentListResponse> {
  const query = campaignId ? `?campaign_id=${encodeURIComponent(campaignId)}` : '';
  return apiGet<DocumentListResponse>(`/documents${query}`);
}

export function getDocument(documentId: string): Promise<DocumentRecord> {
  return apiGet<DocumentRecord>(`/documents/${documentId}`);
}

export function ingestDocument(
  documentId: string,
  payload: IngestDocumentRequest = {}
): Promise<IngestDocumentResponse> {
  return apiPost<IngestDocumentResponse>(`/documents/${documentId}/ingest`, payload);
}
