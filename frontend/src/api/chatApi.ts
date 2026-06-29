import { API_BASE_URL, apiGet, apiPost } from './apiClient';
import type {
  CampaignChatRequest,
  CampaignChatResponse,
  CampaignChatStreamEvent,
  ConversationResponse
} from '../types/chat';

export function sendCampaignChatMessage(payload: CampaignChatRequest): Promise<CampaignChatResponse> {
  return apiPost<CampaignChatResponse>('/chat/campaign', payload);
}

export function getCampaignConversation(campaignId: string): Promise<ConversationResponse> {
  return apiGet<ConversationResponse>(`/campaigns/${campaignId}/conversation`);
}

export async function sendCampaignChatMessageStream(
  payload: CampaignChatRequest,
  onEvent: (event: CampaignChatStreamEvent) => void
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/chat/campaign/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...payload, stream: true })
  });
  if (!response.ok || !response.body) {
    throw new Error('Streaming chat request failed.');
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const frames = buffer.split('\n\n');
    buffer = frames.pop() || '';
    for (const frame of frames) {
      const parsed = parseSseFrame(frame);
      if (parsed) onEvent(parsed);
    }
  }
  const finalFrame = parseSseFrame(buffer);
  if (finalFrame) onEvent(finalFrame);
}

function parseSseFrame(frame: string): CampaignChatStreamEvent | null {
  const eventLine = frame.split('\n').find((line) => line.startsWith('event: '));
  const dataLine = frame.split('\n').find((line) => line.startsWith('data: '));
  if (!eventLine || !dataLine) return null;
  return {
    event: eventLine.replace('event: ', '').trim() as CampaignChatStreamEvent['event'],
    data: JSON.parse(dataLine.replace('data: ', ''))
  } as CampaignChatStreamEvent;
}
