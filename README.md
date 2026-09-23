# Product Clarity Coach prototype

This is a small, model-agnostic reference implementation for translating an
expert methodology into an adaptive coaching experience. It demonstrates:

- state-based next-question selection rather than a fixed questionnaire;
- diagnostic challenges for vague customers, weak problem statements, and
  feature creep;
- strict Product Clarity scope boundaries;
- explicit completion criteria and readiness status;
- a stable Product Clarity Snapshot schema; and
- automated tests across multiple behavior paths.

It deliberately does **not** reproduce the client's proprietary Mind to
Market methodology. The rules and field names are placeholders that would be
replaced after a paid discovery review of the provided materials.

Run the tests:

```powershell
python -m unittest -v
```

Run the interactive reference flow:

```powershell
python demo.py
```

For a native Custom GPT delivery, these deterministic rules become the
instruction architecture, knowledge-map contract, diagnostic rubric,
completion gate, output schema, and regression test suite. The model handles
natural language; the rules keep the coach consistent and in scope.
