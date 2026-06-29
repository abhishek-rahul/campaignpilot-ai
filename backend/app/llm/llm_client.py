from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.core.config import settings
from app.llm.prompt_builder import (
    build_brief_extraction_prompt,
    build_brief_refinement_prompt,
    build_campaign_plan_prompt,
    build_variant_generation_prompt,
    build_variant_refinement_prompt,
)
from app.llm.structured_output import normalize_brief, normalize_variants, parse_json_object


@dataclass
class LLMResult:
    data: dict[str, Any]
    prompt: str
    response_text: str
    model_name: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    used_mock: bool = False


class LLMProviderError(RuntimeError):
    pass


def should_use_mock() -> bool:
    key = (settings.openai_api_key or "").strip()
    return key == "" or key == "replace_me"


def extract_campaign_brief(message: str) -> LLMResult:
    prompt = build_brief_extraction_prompt(message)
    if should_use_mock():
        started = time.perf_counter()
        data = _mock_brief(message)
        return LLMResult(
            data=data,
            prompt=prompt,
            response_text=json.dumps(data, default=str),
            model_name="mock-llm",
            latency_ms=int((time.perf_counter() - started) * 1000),
            used_mock=True,
        )
    return _call_openai_json(prompt, normalizer="brief", message=message)


def generate_message_variants(
    *,
    campaign_name: str,
    goal: str | None,
    target_audience: str | None,
    offer_details: str | None,
    tone: str | None,
    preferred_channels: list[str],
    cta_link: str | None,
    expiry_date: object,
    variant_count: int,
    rag_context: list[dict] | None = None,
) -> LLMResult:
    prompt = build_variant_generation_prompt(
        campaign_name=campaign_name,
        goal=goal,
        target_audience=target_audience,
        offer_details=offer_details,
        tone=tone,
        preferred_channels=preferred_channels,
        cta_link=cta_link,
        expiry_date=expiry_date,
        variant_count=variant_count,
        rag_context=rag_context,
    )
    if should_use_mock():
        started = time.perf_counter()
        variants = _mock_variants(
            goal=goal,
            target_audience=target_audience,
            offer_details=offer_details,
            tone=tone,
            preferred_channels=preferred_channels,
            cta_link=cta_link,
            expiry_date=expiry_date,
            variant_count=variant_count,
            rag_context=rag_context,
        )
        data = {"variants": variants}
        return LLMResult(
            data=data,
            prompt=prompt,
            response_text=json.dumps(data, default=str),
            model_name="mock-llm",
            latency_ms=int((time.perf_counter() - started) * 1000),
            used_mock=True,
        )
    return _call_openai_json(
        prompt,
        normalizer="variants",
        fallback_channels=preferred_channels,
        fallback_tone=tone,
    )


def generate_campaign_plan(*, campaign_name: str, brief: dict[str, Any], rag_context: list[dict]) -> LLMResult:
    prompt = build_campaign_plan_prompt(campaign_name=campaign_name, brief=brief, rag_context=rag_context)
    if should_use_mock():
        started = time.perf_counter()
        data = {"plan": _mock_campaign_plan(campaign_name=campaign_name, brief=brief, rag_context=rag_context)}
        return LLMResult(
            data=data,
            prompt=prompt,
            response_text=json.dumps(data, default=str),
            model_name="mock-llm",
            latency_ms=int((time.perf_counter() - started) * 1000),
            used_mock=True,
        )
    return _call_openai_json(prompt, normalizer="plan")


def refine_campaign_brief(*, current_brief: dict[str, Any], feedback: str, rag_context: list[dict] | None = None) -> LLMResult:
    prompt = build_brief_refinement_prompt(current_brief=current_brief, feedback=feedback, rag_context=rag_context)
    if should_use_mock():
        started = time.perf_counter()
        data = _mock_refined_brief(current_brief=current_brief, feedback=feedback)
        return LLMResult(
            data=data,
            prompt=prompt,
            response_text=json.dumps(data, default=str),
            model_name="mock-llm",
            latency_ms=int((time.perf_counter() - started) * 1000),
            used_mock=True,
        )
    return _call_openai_json(prompt, normalizer="brief")


def refine_message_variant(
    *,
    current_brief: dict[str, Any],
    source_variant: dict[str, Any],
    feedback: str,
    rag_context: list[dict] | None = None,
) -> LLMResult:
    prompt = build_variant_refinement_prompt(
        current_brief=current_brief,
        source_variant=source_variant,
        feedback=feedback,
        rag_context=rag_context,
    )
    if should_use_mock():
        started = time.perf_counter()
        data = {"variant": _mock_refined_variant(source_variant=source_variant, feedback=feedback)}
        return LLMResult(
            data=data,
            prompt=prompt,
            response_text=json.dumps(data, default=str),
            model_name="mock-llm",
            latency_ms=int((time.perf_counter() - started) * 1000),
            used_mock=True,
        )
    result = _call_openai_json(prompt, normalizer="variant", fallback_channels=[source_variant.get("channel")], fallback_tone=source_variant.get("tone"))
    return result


def _call_openai_json(prompt: str, normalizer: str, **kwargs: Any) -> LLMResult:
    started = time.perf_counter()
    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        completion = client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        text = completion.choices[0].message.content or "{}"
        parsed = parse_json_object(text)
        if normalizer == "brief":
            data = normalize_brief(parsed)
        elif normalizer == "variants":
            data = {
                "variants": normalize_variants(
                    parsed,
                    fallback_channels=kwargs.get("fallback_channels") or [],
                    fallback_tone=kwargs.get("fallback_tone"),
                )
            }
        elif normalizer == "variant":
            variant_payload = parsed.get("variant") if isinstance(parsed.get("variant"), dict) else parsed
            variants = normalize_variants(
                {"variants": [variant_payload]},
                fallback_channels=kwargs.get("fallback_channels") or [],
                fallback_tone=kwargs.get("fallback_tone"),
            )
            data = {"variant": variants[0]}
        else:
            data = {"plan": parsed.get("plan") or parsed}
        usage = completion.usage
        return LLMResult(
            data=data,
            prompt=prompt,
            response_text=text,
            model_name=settings.openai_chat_model,
            input_tokens=getattr(usage, "prompt_tokens", 0) if usage else 0,
            output_tokens=getattr(usage, "completion_tokens", 0) if usage else 0,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )
    except Exception as exc:  # noqa: BLE001
        raise LLMProviderError("LLM provider failed") from exc


def _mock_brief(message: str) -> dict[str, Any]:
    lower = message.lower()
    channels: list[str] = []
    if "telegram" in lower:
        channels.append("telegram")
    if "whatsapp" in lower:
        channels.append("whatsapp_mock")
    if not channels:
        channels = ["telegram"]

    cta_match = re.search(r"https?://\S+", message)
    expiry = None
    date_match = re.search(r"(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)", lower)
    if date_match:
        year_match = re.search(r"\b(20\d{2})\b", lower)
        year = int(year_match.group(1)) if year_match else datetime.now().year
        expiry = datetime.strptime(f"{date_match.group(1)} {date_match.group(2)} {year}", "%d %B %Y").date()

    offer_match = re.search(r"(\d+%\s+discount)", lower)
    offer = offer_match.group(1) if offer_match else None
    tone = "friendly" if "friendly" in lower else ("professional" if "professional" in lower else None)
    target = "inactive customers" if "inactive" in lower and "customer" in lower else None
    goal = "Reactivate inactive customers" if target else "Promote campaign offer"
    if "festive" in lower:
        campaign_name = "Festive Reactivation Campaign"
    else:
        campaign_name = "CampaignPilot Draft Campaign"

    data = normalize_brief(
        {
            "campaign_name": campaign_name,
            "goal": goal,
            "target_audience": target,
            "offer_details": offer,
            "tone": tone,
            "preferred_channels": channels,
            "cta_link": cta_match.group(0).rstrip(".") if cta_match else None,
            "expiry_date": expiry,
            "missing_fields": [],
        }
    )
    return data


def _mock_variants(
    *,
    goal: str | None,
    target_audience: str | None,
    offer_details: str | None,
    tone: str | None,
    preferred_channels: list[str],
    cta_link: str | None,
    expiry_date: object,
    variant_count: int,
    rag_context: list[dict] | None = None,
) -> list[dict[str, Any]]:
    channels = preferred_channels or ["telegram"]
    offer = offer_details or "your special offer"
    audience = target_audience or "customers"
    expiry_text = f" before {expiry_date}" if expiry_date else ""
    cta = cta_link or "your CTA link"
    context_hint = ""
    if rag_context:
        first = rag_context[0].get("text") or rag_context[0].get("retrieved_text") or ""
        context_hint = f" Brand note: {first[:90].strip()}."
    templates = [
        ("Friendly Reminder", "Hi there! Your festive offer is live: {offer}{expiry}. Shop now: {cta}"),
        ("Warm Nudge", "We saved something special for {audience}. Get {offer}{expiry}. Tap here: {cta}"),
        ("Clear CTA", "Ready to come back? Enjoy {offer}{expiry}. Start here: {cta}"),
        ("Short Promo", "A friendly deal is waiting: {offer}{expiry}. {cta}"),
        ("Festive Push", "Celebrate with us again. Claim {offer}{expiry}: {cta}"),
    ]
    variants: list[dict[str, Any]] = []
    for index in range(variant_count):
        name, template = templates[index % len(templates)]
        channel = channels[index % len(channels)]
        variants.append(
            {
                "variant_name": name,
                "channel": channel,
                "message_body": template.format(offer=offer, expiry=expiry_text, cta=cta, audience=audience) + context_hint,
                "tone": tone or "friendly",
                "reason": f"Supports {goal or 'the campaign goal'} with a concise {channel} message."
                + (" Uses retrieved document context." if rag_context else ""),
                "risk_level": "low",
            }
        )
    return variants


def _mock_campaign_plan(*, campaign_name: str, brief: dict[str, Any], rag_context: list[dict]) -> dict[str, Any]:
    context_line = "Use uploaded brand/product guidance where relevant."
    if rag_context:
        context_line = (rag_context[0].get("text") or rag_context[0].get("retrieved_text") or context_line)[:180]
    return {
        "campaign_summary": f"{campaign_name} campaign for {brief.get('target_audience') or 'the target audience'}.",
        "target_audience": brief.get("target_audience"),
        "key_message": f"{brief.get('offer_details') or 'The offer'} is available through the campaign CTA.",
        "recommended_channels": brief.get("preferred_channels") or [],
        "offer_positioning": brief.get("offer_details") or "Lead with the clearest customer benefit.",
        "content_guidelines": [context_line, f"Keep tone {brief.get('tone') or 'clear'}."],
        "risks_or_constraints": ["Verify claims against uploaded source material before launch."],
        "next_step": "Generate channel-aware variants with RAG context enabled.",
    }


def _mock_refined_brief(*, current_brief: dict[str, Any], feedback: str) -> dict[str, Any]:
    refined = dict(current_brief)
    lower = feedback.lower()
    if "premium" in lower:
        refined["tone"] = "premium"
    if "inactive" in lower:
        refined["target_audience"] = "inactive customers"
    if "less pushy" in lower or "reduce urgency" in lower or "softer" in lower:
        refined["tone"] = refined.get("tone") or "friendly"
        refined["ai_reply"] = "I refined the brief to use softer urgency."
    else:
        refined["ai_reply"] = "I refined the campaign brief."
    return normalize_brief(refined)


def _mock_refined_variant(*, source_variant: dict[str, Any], feedback: str) -> dict[str, Any]:
    lower = feedback.lower()
    body = source_variant.get("message_body") or ""
    if "shorter" in lower:
        body = body.split(".")[0][:160].strip() or body[:160]
    if "less pushy" in lower or "reduce urgency" in lower or "softer" in lower:
        body = body.replace("Hurry", "When you're ready").replace("Last chance", "A friendly reminder")
    if "premium" in lower:
        body = f"An exclusive update for you: {body}"
    return {
        "variant_name": f"Refined {source_variant.get('variant_name') or 'Variant'}",
        "channel": source_variant.get("channel") or "telegram",
        "message_body": body,
        "tone": "premium" if "premium" in lower else (source_variant.get("tone") or "friendly"),
        "reason": f"Refined based on feedback: {feedback}",
        "risk_level": "low",
    }
