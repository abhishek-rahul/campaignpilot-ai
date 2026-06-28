from __future__ import annotations

from datetime import date


def build_brief_extraction_prompt(message: str) -> str:
    return f"""
You are CampaignPilot AI. Extract a structured campaign brief from the user message.
Return JSON only with these keys:
campaign_name, goal, target_audience, offer_details, tone, preferred_channels,
cta_link, expiry_date, missing_fields, ai_reply.

Rules:
- preferred_channels must use only "telegram" or "whatsapp_mock".
- expiry_date must be ISO date YYYY-MM-DD when known, otherwise null.
- missing_fields must include any absent required fields among goal, target_audience,
  offer_details, tone, preferred_channels, cta_link, expiry_date.
- ai_reply should ask concise follow-up questions when missing_fields is not empty.

User message:
{message}
""".strip()


def build_variant_generation_prompt(
    *,
    campaign_name: str,
    goal: str | None,
    target_audience: str | None,
    offer_details: str | None,
    tone: str | None,
    preferred_channels: list[str],
    cta_link: str | None,
    expiry_date: date | None,
    variant_count: int,
) -> str:
    return f"""
You are CampaignPilot AI. Generate {variant_count} short campaign message variants.
Return JSON only with key "variants" containing objects with:
variant_name, channel, message_body, tone, reason, risk_level.

Use only these channels: {preferred_channels}.
Do not use RAG, compliance tools, approvals, delivery, or memory.

Campaign:
- Name: {campaign_name}
- Goal: {goal}
- Audience: {target_audience}
- Offer: {offer_details}
- Tone: {tone}
- CTA: {cta_link}
- Expiry: {expiry_date}
""".strip()
