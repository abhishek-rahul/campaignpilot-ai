export type DocumentRecord = {
  document_id: string;
  original_filename: string;
  document_type: string;
  status: string;
  file_size_bytes: number;
  content_type: string | null;
  error_message: string | null;
  chunks_count: number;
  embeddings_count: number;
  created_at: string;
  ingested_at: string | null;
};

export type DocumentListResponse = {
  items: DocumentRecord[];
  pagination: {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
  };
};

export type IngestDocumentRequest = {
  chunk_size?: number;
  chunk_overlap?: number;
  embedding_model?: string | null;
};

export type IngestDocumentResponse = {
  document_id: string;
  status: string;
  chunks_count: number;
  embeddings_count: number;
  elasticsearch_index: string;
  used_mock_embeddings: boolean;
};
