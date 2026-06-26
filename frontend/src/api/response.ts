import type { ApiResponse } from '../types/common';

export async function handleApiResponse<T>(response: Response): Promise<T> {
  const body = (await response.json()) as ApiResponse<T>;
  if (!body.success) {
    throw new Error(body.error?.code || body.message);
  }
  return body.data as T;
}
