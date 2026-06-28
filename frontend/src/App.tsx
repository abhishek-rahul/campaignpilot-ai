import { CampaignChatPage } from './pages/CampaignChatPage';

export default function App() {
  return (
    <main style={{ fontFamily: 'Arial, sans-serif', padding: 24, maxWidth: 1180, margin: '0 auto' }}>
      <h1>CampaignPilot AI</h1>
      <p>Campaign chat, document RAG, campaign planning, and message variants.</p>
      <CampaignChatPage />
    </main>
  );
}
