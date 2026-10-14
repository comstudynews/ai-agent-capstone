# Recipe 12. Stateless Session

## 1. What you will learn

Memory vs PostgreSQL Checkpointer. Read the detailed theoretical chapter in Notion before running this checkpoint.

## 2. Prerequisite

Run commands from the repository root. Complete Recipe 11 and `python scripts/check_env.py`. Demo mode works without external credentials; actual integration requires the optional extras noted in the root README.

## 3. First successful observation

```bash
python -m app.lesson 12
```

Explain what the output represents and why this layer is needed. **This is a small checkpoint, not a claim that the full external integration is complete.**

The self-contained checkpoint entrypoint is [complete.py](complete.py); execute `python -m steps.step12.complete` after installing the editable package. The shared `app/` implementation is the accumulated source of truth.

## 4. Read the implementation

Open [`app/checkpoint.py`](../../app/checkpoint.py). Locate its inputs, return schema, side effects and error boundary. Modify one safe mock value in a disposable local copy, rerun the checkpoint, and compare the result.

## 5. Verify and troubleshoot

```bash
python -m pytest -q
```

If imports fail, check virtualenv and optional dependencies. If a network or API error occurs, use demo mode first, then use `docs/VALIDATION.md` to isolate the affected external component.

## 6. Reflection

- Which system component owns this behavior?
- What happens if its input is invalid or missing?
- How will you observe success without relying only on the model's wording?

[Previous](../step11/README.md) · [Next](../step13/README.md)
