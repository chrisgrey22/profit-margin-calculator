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
- `omit_training_webpage.html` – standalone interactive OMIT training/support page covering WHY, WHAT, PIP2 blocks, APP, and PACE reminders.

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

## Peter's Energy (`peters-energy/index.html`)

A simple gas and electricity tracker for a household:

- **My bills** – enter monthly kWh and £ from invoices (includes an m³/ft³ → kWh gas converter).
- **Usage & cost** – month-by-month chart, yearly kWh vs a typical home, price actually paid per kWh.
- **Compare deals** – enter quotes (unit rates and standing charges) and rank them by yearly cost for *your* usage, against the Ofgem price cap (South Wales Oct–Dec 2026 and GB average from 1 Jan 2027).
- **Fix or flex?** – plain-English verdict for each fixed quote, switching checklist, links to comparison sites and a November 2026 market snapshot.

Open the file in any browser; figures are saved on that device. The published claude.ai version saves to a shared store.
