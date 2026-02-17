# profit-margin-calculator

## South Wales Police Internal Comms Agent

This repository now includes a lightweight drafting agent that converts operational updates into:

- a **Viva Engage post draft**
- an **internal web page article draft**
- explicit **delivery plan alignment** (top matching key messages)

### Files

- `agent/internal_comms_agent.py` – CLI generator.
- `agent/delivery_plan_messages.json` – editable delivery-plan message map and keywords.
- `agent/examples/update_example.txt` – sample operational update.
- `agent/tests/test_internal_comms_agent.py` – automated checks.

### Usage

```bash
python agent/internal_comms_agent.py \
  --update-file agent/examples/update_example.txt \
  --author "Inspector Jane Doe" \
  --team "Neighbourhood Policing" \
  --output agent/examples/generated_draft.md
```

If you omit `--output`, the draft prints to stdout.

### How alignment works

1. The agent scans the update text.
2. It scores delivery-plan themes based on configured keywords.
3. It selects the top matched themes and includes them in both draft formats.

To tune this for your force plan, edit `agent/delivery_plan_messages.json` and update each theme description and keyword list.
