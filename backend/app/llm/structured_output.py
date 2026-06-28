from __future__ import annotations

import json
import re
from datetime import date, datetime
from typing import Any

REQUIRED_BRIEF_FIELDS = [
    "goal",
    "target_audience",
    "offer_details",
    "tone",
    "preferred_channels",
    "cta_link",
    "expiry_date",
]


class StructuredOutputError(ValueError):
    pass


def parse_json_object(raw: str) -> dict[str, Any]:
    text = raw.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise StructuredOutputError(f"LLM response was not valid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise StructuredOutputError("LLM response must be a JSON object")
    return value


def normalize_channel(channel: str) -> str | None:
    value = channel.strip().lower().replace("-", "_").replace(" ", "_")
    if value in {"telegram", "tg"}:
        return "telegram"
    if value in {"whatsapp", "whatsapp_mock", "wa", "whatsappmock"}:
        return "whatsapp_mock"
    return None


def normalize_channels(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        raw_channels = re.split(r"[,/]| and ", value, flags=re.IGNORECASE)
    elif isinstance(value, list):
        raw_channels = value
    else:
        return []
    channels: list[str] = []
    for raw in raw_channels:
        channel = normalize_channel(str(raw))
        if channel and channel not in channels:
            channels.append(channel)
    return channels


def parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d %B %Y", "%d %b %Y"):
        try:
            parsed = datetime.strptime(text, fmt).date()
            if parsed.year == 1900:
                return parsed.replace(year=datetime.now().year)
            return parsed
        except ValueError:
            continue
    return None


def normalize_brief(data: dict[str, Any]) -> dict[str, Any]:
    channels = normalize_channels(data.get("preferred_channels"))
    brief = {
        "campaign_name": data.get("campaign_name") or "Untitled Campaign",
        "goal": data.get("goal"),
        "target_audience": data.get("target_audience"),
        "offer_details": data.get("offer_details"),
        "tone": data.get("tone"),
        "preferred_channels": channels,
        "cta_link": data.get("cta_link"),
        "expiry_date": parse_date(data.get("expiry_date")),
    }
    missing = [field for field in REQUIRED_BRIEF_FIELDS if not brief.get(field)]
    explicit_missing = data.get("missing_fields") if isinstance(data.get("missing_fields"), list) else []
    for field in explicit_missing:
        if field in REQUIRED_BRIEF_FIELDS and field not in missing:
            missing.append(field)
    brief["missing_fields"] = missing
    brief["brief_status"] = "COMPLETE" if not missing else "INCOMPLETE"
    brief["ai_reply"] = data.get("ai_reply") or build_default_ai_reply(missing)
    return brief


def build_default_ai_reply(missing_fields: list[str]) -> str:
    if not missing_fields:
        return "Great, I have enough details to generate campaign variants."
    friendly = ", ".join(missing_fields)
    return f"I can help with this campaign. Please share these missing details: {friendly}."


def normalize_variants(data: dict[str, Any], *, fallback_channels: list[str], fallback_tone: str | None) -> list[dict[str, Any]]:
    raw_variants = data.get("variants")
    if not isinstance(raw_variants, list):
        raise StructuredOutputError("Variant response must include a variants list")
    variants: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_variants, start=1):
        if not isinstance(raw, dict):
            continue
        channel = normalize_channel(str(raw.get("channel") or ""))
        if channel is None and fallback_channels:
            channel = fallback_channels[(index - 1) % len(fallback_channels)]
        body = str(raw.get("message_body") or "").strip()
        if not channel or not body:
            continue
        variants.append(
            {
                "variant_name": str(raw.get("variant_name") or f"Variant {index}"),
                "channel": channel,
                "message_body": body,
                "tone": raw.get("tone") or fallback_tone,
                "reason": raw.get("reason") or "Generated from the Slice 1 campaign brief.",
                "risk_level": str(raw.get("risk_level") or "low").lower(),
            }
        )
    if not variants:
        raise StructuredOutputError("No usable variants were generated")
    return variants
