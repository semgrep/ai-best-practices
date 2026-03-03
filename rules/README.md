# Semgrep Rules for AI Trust & Safety Best Practices

Static analysis rules that detect common trust and safety gaps in applications built on LLM APIs. These rules encode best practices published by OpenAI, Anthropic, Google, Cohere, and Mistral into automated checks that run in seconds.

## Quick Start

```bash
# Scan your project
semgrep --config rules/ /path/to/your/project/

# Validate all rules
semgrep --validate --config rules/

# Run all tests
semgrep --test rules/
```

## Rule Catalog

### Phase 1: Hardcoded Credentials (6 rules)

Detects API keys hardcoded in source code instead of using environment variables or secrets managers.

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `openai-hardcoded-api-key` | ERROR | `OpenAI(api_key="sk-...")` and variants | py, js/ts, go, java, rb |
| `anthropic-hardcoded-api-key` | ERROR | `Anthropic(api_key="sk-ant-...")` and variants | py, js/ts, go, java, rb |
| `gemini-hardcoded-api-key` | ERROR | `genai.configure(api_key="AIza...")` and variants | py, js/ts, go, java |
| `cohere-hardcoded-api-key` | ERROR | `cohere.Client(api_key="...")` and variants | py, js/ts |
| `mistral-hardcoded-api-key` | ERROR | `Mistral(api_key="...")` and variants | py, js/ts |
| `llm-api-key-in-source` | ERROR | Any variable assigned a string matching known AI key prefixes (`sk-`, `sk-ant-`, `sk-proj-`, `AIza`) | py, js/ts, go, java, rb |

### Phase 2: Missing Safety Checks (7 rules)

Detects missing safety parameters and guards in LLM API calls.

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `openai-missing-refusal-check` | WARNING | Accessing `.message.content` without checking `.message.refusal` | py, js/ts |
| `anthropic-missing-refusal-check` | WARNING | Accessing `.content` without checking `stop_reason` | py, js/ts |
| `openai-missing-user-parameter` | WARNING | `chat.completions.create()` without `user=` parameter | py, js/ts |
| `openai-missing-max-tokens` | WARNING | `chat.completions.create()` without `max_tokens=` parameter | py, js/ts |
| `anthropic-missing-system-prompt` | WARNING | `messages.create()` without `system=` parameter | py, js/ts |
| `anthropic-missing-max-tokens` | WARNING | `messages.create()` without `max_tokens=` parameter | py, js/ts |
| `gemini-missing-safety-settings` | WARNING | `generate_content()` without `safety_settings=` parameter | py, js/ts |

### Phase 3: Prompt Injection (3 taint rules)

Detects user input flowing into system prompts, enabling prompt injection attacks. Uses Semgrep's taint analysis to trace data flow from web framework request objects to LLM API system prompt parameters.

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `openai-user-input-in-system-prompt` | ERROR | User input &rarr; `{"role": "system", "content": X}` | py, js/ts |
| `anthropic-user-input-in-system-prompt` | ERROR | User input &rarr; `system=` parameter | py, js/ts |
| `gemini-user-input-in-system-prompt` | ERROR | User input &rarr; `system_instruction=` parameter | py, js/ts |

**Taint sources:** Flask (`request.args`, `request.form`, `request.json`), Django (`request.GET`, `request.POST`), Express (`req.body`, `req.query`, `req.params`)

### Phase 4: Missing Safeguards (7 rules)

Detects missing error handling, content moderation, and system messages.

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `openai-missing-system-message` | WARNING | `messages=[...]` with no `{"role": "system", ...}` | py, js/ts |
| `openai-missing-moderation` | WARNING | `chat.completions.create()` without `moderations.create()` in same function | py |
| `openai-no-error-handling` | WARNING | OpenAI API call not in try/except | py |
| `anthropic-no-error-handling` | WARNING | Anthropic API call not in try/except | py |
| `gemini-no-error-handling` | WARNING | Gemini API call not in try/except | py |
| `cohere-no-error-handling` | WARNING | Cohere API call not in try/except | py |
| `mistral-no-error-handling` | WARNING | Mistral API call not in try/except | py |

## CI/CD Integration

### GitHub Actions

```yaml
name: AI Safety Lint
on: [pull_request]

jobs:
  semgrep:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/checkout@v4
        with:
          repository: your-org/ai-best-practices
          path: ai-best-practices
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: ai-best-practices/rules/
```

### GitLab CI

```yaml
semgrep:
  image: semgrep/semgrep
  script:
    - semgrep --config rules/ --error .
  rules:
    - if: $CI_MERGE_REQUEST_IID
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/semgrep/semgrep
    rev: v1.138.0
    hooks:
      - id: semgrep
        args: ['--config', 'rules/', '--error']
```

## Suppressing Findings

Use `# nosemgrep` to suppress false positives on specific lines:

```python
# nosemgrep: openai-missing-moderation
response = client.chat.completions.create(...)  # moderation handled in middleware
```

## Known Limitations

- **Go/Java rules limited to credential detection** — These languages use struct/builder patterns where Semgrep can't reliably detect missing fields
- **Taint rules cover Flask, Django, and Express sources** — Other frameworks (FastAPI query params, Sanic, Koa, Hapi) would need additional source patterns
- **Missing-moderation rule scoped to same function** — If moderation is in middleware, it may false-positive
- **Error handling rules are Python-only** — Try/catch detection in JS/TS has too many patterns (async/await, .catch(), try/catch) to cover reliably
- **Ruby SDK patterns may vary** — The `ruby-openai` and Anthropic Ruby gems use different conventions than official SDKs

## Provider Best Practices References

- [OpenAI Safety Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)
- [OpenAI API Key Safety](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)
- [Anthropic API Documentation](https://docs.anthropic.com/en/api)
- [Google Gemini Safety Settings](https://ai.google.dev/gemini-api/docs/safety-settings)
- [Cohere API Documentation](https://docs.cohere.com/)
- [Mistral API Documentation](https://docs.mistral.ai/)

## Stats

- **23 YAML rule files** containing **51 individual rules** (multi-language rules split per language)
- **51 test files** with positive and negative test cases
- **74 total files** across 23 rule directories
- **5 providers covered:** OpenAI, Anthropic, Google Gemini, Cohere, Mistral
- **5 languages:** Python, JavaScript/TypeScript, Go, Java, Ruby
