#!/usr/bin/env python3
"""South Wales Police internal communications drafting agent.

This script converts operational updates into internal-facing article drafts and
maps each article to delivery-plan key messages.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


@dataclass
class DeliveryMessage:
    id: str
    title: str
    description: str
    keywords: list[str]


def load_delivery_messages(path: Path) -> list[DeliveryMessage]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [DeliveryMessage(**item) for item in payload]


def normalise_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def keyword_score(update_text: str, keywords: Iterable[str]) -> int:
    clean = normalise_text(update_text)
    return sum(clean.count(normalise_text(keyword)) for keyword in keywords)


def select_key_messages(update_text: str, messages: list[DeliveryMessage], top_n: int = 3) -> list[DeliveryMessage]:
    ranked = sorted(
        ((keyword_score(update_text, msg.keywords), msg) for msg in messages),
        key=lambda item: item[0],
        reverse=True,
    )
    selected = [msg for score, msg in ranked if score > 0][:top_n]
    if selected:
        return selected
    return messages[:1]


def first_sentence(text: str) -> str:
    chunks = re.split(r"(?<=[.!?])\s+", text.strip())
    return chunks[0] if chunks and chunks[0] else text.strip()


def build_headline(update_text: str) -> str:
    sentence = first_sentence(update_text)
    sentence = sentence[:110].strip()
    return sentence.rstrip(".")


def build_viva_engage_variant(headline: str, update_text: str, aligned_messages: list[DeliveryMessage]) -> str:
    alignment = ", ".join(msg.title for msg in aligned_messages)
    short_update = update_text.strip().replace("\n", " ")
    short_update = re.sub(r"\s+", " ", short_update)
    short_update = (short_update[:300] + "...") if len(short_update) > 300 else short_update

    return (
        f"**{headline}**\n\n"
        f"{short_update}\n\n"
        f"Delivery plan alignment: {alignment}.\n"
        "Please add feedback in the comments so we can adapt delivery quickly."
    )


def build_web_variant(headline: str, update_text: str, aligned_messages: list[DeliveryMessage], author: str, team: str) -> str:
    bullet_points = "\n".join(
        f"- **{msg.title}:** {msg.description}" for msg in aligned_messages
    )

    return f"""# {headline}

**Author:** {author}
**Team:** {team}
**Date:** {date.today().isoformat()}

## Operational Update
{update_text.strip()}

## Delivery Plan Alignment
{bullet_points}

## What This Means for Colleagues
- Continue using this update in local briefings and team discussions.
- Escalate implementation barriers through your usual governance route.
- Share examples of impact so we can include them in future force-wide communications.

## Suggested Call to Action
Managers: cascade this in your next team briefing and capture one example of local impact this week.
"""


def build_article(update_text: str, messages: list[DeliveryMessage], author: str, team: str) -> str:
    aligned = select_key_messages(update_text, messages)
    headline = build_headline(update_text)

    alignment_list = "\n".join(
        f"- {msg.title} ({msg.id})" for msg in aligned
    )

    viva = build_viva_engage_variant(headline, update_text, aligned)
    web = build_web_variant(headline, update_text, aligned, author, team)

    return f"""# Internal Comms Draft Pack

## Headline
{headline}

## Key Message Alignment
{alignment_list}

## Viva Engage Draft
{viva}

## Internal Web Page Draft
{web}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Turn South Wales Police updates into aligned internal comms drafts."
    )
    parser.add_argument("--update-file", type=Path, required=True, help="Path to plain text update content.")
    parser.add_argument(
        "--messages-file",
        type=Path,
        default=Path("agent/delivery_plan_messages.json"),
        help="Path to delivery plan key-message config.",
    )
    parser.add_argument("--author", default="Corporate Communications")
    parser.add_argument("--team", default="South Wales Police")
    parser.add_argument("--output", type=Path, help="Optional file to write generated markdown.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    update_text = args.update_file.read_text(encoding="utf-8")
    messages = load_delivery_messages(args.messages_file)
    article = build_article(update_text, messages, args.author, args.team)

    if args.output:
        args.output.write_text(article, encoding="utf-8")
        print(f"Draft written to {args.output}")
    else:
        print(article)


if __name__ == "__main__":
    main()
