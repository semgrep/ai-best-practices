# Semgrep Rules for AI Trust & Safety Best Practices

Static analysis rules that detect common trust and safety gaps in applications built on LLM APIs. These rules encode best practices published by OpenAI, Anthropic, Google, Cohere, Mistral, and Hugging Face into automated checks that run in seconds.

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

### Phase 1: Hardcoded Credentials (7 rules)

Detects API keys hardcoded in source code instead of using environment variables or secrets managers.

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `openai-hardcoded-api-key` | ERROR | `OpenAI(api_key="sk-...")` and variants | py, js/ts, go, java, rb |
| `anthropic-hardcoded-api-key` | ERROR | `Anthropic(api_key="sk-ant-...")` and variants | py, js/ts, go, java, rb |
| `gemini-hardcoded-api-key` | ERROR | `genai.configure(api_key="AIza...")` and variants | py, js/ts, go, java |
| `cohere-hardcoded-api-key` | ERROR | `cohere.Client(api_key="...")` and variants | py, js/ts |
| `mistral-hardcoded-api-key` | ERROR | `Mistral(api_key="...")` and variants | py, js/ts |
| `huggingface-hardcoded-api-key` | ERROR | `InferenceClient(token="hf_...")` and variants | py, js/ts |
| `llm-api-key-in-source` | ERROR | Any variable assigned a string matching known AI key prefixes (`sk-`, `sk-ant-`, `sk-proj-`, `AIza`, `hf_`) | py, js/ts, go, java, rb |

### Phase 2: Missing Safety Checks (12 rules)

Detects missing safety parameters and guards in LLM API calls.

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `openai-missing-refusal-check` | WARNING | Accessing `.message.content` without checking `.message.refusal` | py, js/ts |
| `anthropic-missing-refusal-check` | WARNING | Accessing `.content` without checking `stop_reason` | py, js/ts |
| `openai-missing-user-parameter` | WARNING | `chat.completions.create()` without `user=` parameter | py, js/ts |
| `openai-missing-safety-identifier` | WARNING | `responses.create()` without `safety_identifier=` parameter | py, js/ts |
| `openai-missing-max-tokens` | WARNING | `chat.completions.create()` without `max_tokens=` parameter | py, js/ts |
| `anthropic-missing-system-prompt` | WARNING | `messages.create()` without `system=` parameter | py, js/ts |
| `anthropic-missing-max-tokens` | WARNING | `messages.create()` without `max_tokens=` parameter | py, js/ts |
| `anthropic-missing-metadata-user-id` | WARNING | `messages.create()` without `metadata=` for user tracking | py, js/ts |
| `gemini-missing-safety-settings` | WARNING | `generate_content()` without `safety_settings=` parameter | py, js/ts |
| `gemini-missing-system-instruction` | WARNING | `GenerativeModel()` without `system_instruction=` parameter | py, js/ts |
| `mistral-missing-safe-prompt` | WARNING | `chat.complete()` without `safe_prompt=` parameter | py, js/ts |
| `cohere-missing-safety-mode` | WARNING | `chat()` without explicit `safety_mode=` parameter | py, js/ts |

### Phase 3: Prompt Injection (3 taint rules)

Detects user input flowing into system prompts, enabling prompt injection attacks. Uses Semgrep's taint analysis to trace data flow from web framework request objects to LLM API system prompt parameters.

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `openai-user-input-in-system-prompt` | ERROR | User input &rarr; `{"role": "system", "content": X}` | py, js/ts |
| `anthropic-user-input-in-system-prompt` | ERROR | User input &rarr; `system=` parameter | py, js/ts |
| `gemini-user-input-in-system-prompt` | ERROR | User input &rarr; `system_instruction=` parameter | py, js/ts |

**Taint sources:** Flask (`request.args`, `request.form`, `request.json`), Django (`request.GET`, `request.POST`), Express (`req.body`, `req.query`, `req.params`)

### Phase 4: Missing Safeguards (11 rules)

Detects missing error handling, content moderation, and system messages.

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `openai-missing-system-message` | WARNING | `messages=[...]` with no `{"role": "system", ...}` | py, js/ts |
| `openai-missing-moderation` | WARNING | `chat.completions.create()` without `moderations.create()` in same function | py |
| `openai-missing-moderation-check` | WARNING | Moderation response accessed without checking `.flagged` | py |
| `mistral-missing-moderation` | WARNING | `chat.complete()` without `classifiers.moderate()` in same function | py |
| `cohere-safety-mode-off` | ERROR | `safety_mode="OFF"` explicitly disabling all safety guardrails | py, js/ts |
| `openai-no-error-handling` | WARNING | OpenAI API call not in try/except | py |
| `anthropic-no-error-handling` | WARNING | Anthropic API call not in try/except | py |
| `gemini-no-error-handling` | WARNING | Gemini API call not in try/except | py |
| `cohere-no-error-handling` | WARNING | Cohere API call not in try/except | py |
| `mistral-no-error-handling` | WARNING | Mistral API call not in try/except | py |
| `huggingface-no-error-handling` | WARNING | Hugging Face Inference API call not in try/except | py |

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

- [OpenAI Safety Best Practices](https://developers.openai.com/api/docs/guides/safety-best-practices/)
- [OpenAI Safety Checks](https://developers.openai.com/api/docs/guides/safety-checks/)
- [OpenAI Moderation Guide](https://developers.openai.com/api/docs/guides/moderation)
- [OpenAI API Key Safety](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)
- [Anthropic API Safeguards](https://support.claude.com/en/articles/9199617-api-safeguards-tools)
- [Anthropic API Key Best Practices](https://support.claude.com/en/articles/9767949-api-key-best-practices-keeping-your-keys-safe-and-secure)
- [Google Gemini Safety Guidance](https://ai.google.dev/gemini-api/docs/safety-guidance)
- [Google Gemini Safety Settings](https://ai.google.dev/gemini-api/docs/safety-settings)
- [Cohere Safety Modes](https://docs.cohere.com/docs/safety-modes)
- [Mistral Guardrailing](https://docs.mistral.ai/capabilities/guardrailing/)
- [Hugging Face Security Tokens](https://huggingface.co/docs/hub/en/security-tokens)
- [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/)

## Stats

- **33 YAML rule files** containing **68 individual rules** (multi-language rules split per language)
- **6 providers covered:** OpenAI, Anthropic, Google Gemini, Cohere, Mistral, Hugging Face
- **5 languages:** Python, JavaScript/TypeScript, Go, Java, Ruby
