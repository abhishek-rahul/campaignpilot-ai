export type ApiError = {
  code: string;
  details: Array<Record<string, unknown>>;
};

export type ResponseMeta = {
  request_id: string;
  timestamp: string;
};

export type ApiResponse<T> = {
  success: boolean;
  message: string;
  data: T | null;
  error: ApiError | null;
  meta: ResponseMeta;
};

export type Pagination = {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
};
