# AI Best Practices — Semgrep Rules

## Project Overview

This repo contains Semgrep static analysis rules that detect trust and safety gaps in LLM-powered applications. Rules cover 6 providers (OpenAI, Anthropic, Google Gemini, Cohere, Mistral, Hugging Face) across Python, JS/TS, Go, Java, and Ruby.

## Repo Structure

```
rules/<rule-id>/
  <rule-id>.yaml       # Semgrep rule definition (one or more sub-rules)
  <rule-id>.py         # Python test file with # ruleid: and # ok: annotations
  <rule-id>.js         # JS/TS test file (if applicable)
  <rule-id>.go         # Go test file (if applicable)
  <rule-id>.java       # Java test file (if applicable)
  <rule-id>.rb         # Ruby test file (if applicable)
.github/workflows/test.yml  # CI: validates and tests all rules
```

## Working with Rules

### Validate rules
```bash
semgrep --validate --config rules/
```

### Run all tests
```bash
semgrep --test rules/
```

### Validate/test a single rule
```bash
semgrep --validate --config rules/<rule-id>/
semgrep --test rules/<rule-id>/
```

## Writing Rules

### Rule YAML format
Each `.yaml` file contains a `rules:` list. Each sub-rule has a unique `id` with a language suffix (e.g., `openai-hardcoded-api-key-python`, `openai-hardcoded-api-key-javascript`).

### Test annotations
- `# ruleid: <rule-id>` on the line immediately BEFORE the line that should be flagged
- `# ok: <rule-id>` on the line immediately BEFORE the line that should NOT be flagged

### Common pitfalls
- Rule IDs must be unique within a YAML file; use language suffixes
- JS patterns containing colons (e.g., `user: $USER`) must be quoted in YAML
- `pattern-not-inside` with `...` at both start AND end matches too broadly (entire file scope)
- JS `await` changes AST; use `pattern-either` with both `await` and non-await variants
- For `pattern-inside` guards matching multiple constructors, use a metavariable: `$CLIENT = cohere.$CLASS(...)`

### Metadata fields
Every sub-rule should include:
```yaml
metadata:
  cwe: "CWE-XXX: Description"
  category: security
  confidence: HIGH|MEDIUM
  technology: [provider-name]
  references:
    - https://...
```

CWE mapping:
- Hardcoded credentials: `CWE-798: Use of Hard-coded Credentials`
- Error handling: `CWE-755: Improper Handling of Exceptional Conditions`
- Missing safety params: `CWE-693: Protection Mechanism Failure`
- Prompt injection (taint): `CWE-77: Command Injection`

## Important Reminders

- **Always update README.md** when adding, removing, or modifying rules. Update the stats line, providers table, "What It Catches" table, and Rule Catalog section as needed.

## Current Stats

- 40 YAML rule files, 83 individual sub-rules
- All rules validated, all tests passing
