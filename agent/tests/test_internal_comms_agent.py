from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))

from agent.internal_comms_agent import load_delivery_messages, select_key_messages


def test_select_key_messages_matches_relevant_themes():
    update = "Victim support and safeguarding were strengthened with neighbourhood patrol activity."
    messages = load_delivery_messages(Path("agent/delivery_plan_messages.json"))

    aligned = select_key_messages(update, messages)
    titles = {message.title for message in aligned}

    assert "Victim-Focused Service" in titles
    assert "Safe Neighbourhoods" in titles


def test_select_key_messages_falls_back_when_no_keywords():
    update = "A general internal note with no mapped terminology."
    messages = load_delivery_messages(Path("agent/delivery_plan_messages.json"))

    aligned = select_key_messages(update, messages)

    assert len(aligned) == 1
    assert aligned[0].id == "safe-neighbourhoods"
