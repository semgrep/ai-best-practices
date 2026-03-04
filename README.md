# AI Best Practices — Semgrep Rules

Semgrep rules that catch common trust & safety mistakes in LLM-powered applications. Scan any codebase in seconds to find hardcoded API keys, missing safety checks, prompt injection risks, and unhandled errors across all major AI providers.

## What It Catches

| Category | Example | Severity |
|----------|---------|----------|
| **Hardcoded API keys** | `OpenAI(api_key="sk-abc123...")` | ERROR |
| **Prompt injection** | User input flowing into system prompts | ERROR |
| **Missing refusal handling** | Accessing response content without checking for refusals | WARNING |
| **Missing safety settings** | Gemini calls without `safety_settings` | WARNING |
| **No error handling** | API calls outside try/except blocks | WARNING |
| **Missing moderation** | Chat completions without moderation checks | WARNING |

## Providers & Languages

|  | Python | JS/TS | Go | Java | Ruby |
|--|:------:|:-----:|:--:|:----:|:----:|
| **OpenAI** | X | X | X | X | X |
| **Anthropic** | X | X | X | X | X |
| **Google Gemini** | X | X | X | X | |
| **Cohere** | X | X | | | |
| **Mistral** | X | X | | | |
| **Hugging Face** | X | X | | | |

## Quick Start

```bash
# Install Semgrep
pip install semgrep

# Clone the rules
git clone https://github.com/semgrep/ai-best-practices.git

# Scan your project
semgrep --config ai-best-practices/rules/ /path/to/your/project/
```

## Example Findings

**Hardcoded API key:**
```
rules/openai-hardcoded-api-key/openai-hardcoded-api-key.py
   severity:error rule:openai-hardcoded-api-key-python:
   OpenAI API key is hardcoded in source code. Use environment variables
   or a secrets manager instead.
```

**Prompt injection risk:**
```
app.py
   severity:error rule:openai-user-input-in-system-prompt-python:
   User input flows into the OpenAI system prompt. This enables prompt
   injection attacks where users can override system instructions.
```

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
          repository: semgrep/ai-best-practices
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
    - git clone https://github.com/semgrep/ai-best-practices.git
    - semgrep --config ai-best-practices/rules/ --error .
  rules:
    - if: $CI_MERGE_REQUEST_IID
```

### Pre-commit

```yaml
repos:
  - repo: https://github.com/semgrep/semgrep
    rev: v1.138.0
    hooks:
      - id: semgrep
        args: ['--config', 'path/to/ai-best-practices/rules/', '--error']
```

## Rule Catalog (33 rules, 68 sub-rules)

### Hardcoded Credentials

| Rule | What it catches | Languages |
|------|----------------|-----------|
| `openai-hardcoded-api-key` | `sk-*` keys in OpenAI constructors | py, js/ts, go, java, rb |
| `anthropic-hardcoded-api-key` | `sk-ant-*` keys in Anthropic constructors | py, js/ts, go, java, rb |
| `gemini-hardcoded-api-key` | `AIza*` keys in Gemini constructors | py, js/ts, go, java |
| `cohere-hardcoded-api-key` | String literals in Cohere constructors | py, js/ts |
| `mistral-hardcoded-api-key` | String literals in Mistral constructors | py, js/ts |
| `huggingface-hardcoded-api-key` | `hf_*` tokens in HF InferenceClient / AutoModel | py, js/ts |
| `llm-api-key-in-source` | Any variable matching AI key prefixes (`sk-`, `sk-ant-`, `AIza`, `hf_`) | py, js/ts, go, java, rb |

### Missing Safety Checks

| Rule | What it catches | Languages |
|------|----------------|-----------|
| `openai-missing-refusal-check` | `.message.content` without `.message.refusal` guard | py, js/ts |
| `anthropic-missing-refusal-check` | `.content` without `stop_reason` check | py, js/ts |
| `openai-missing-user-parameter` | `chat.completions.create()` without `user=` | py, js/ts |
| `openai-missing-safety-identifier` | `responses.create()` without `safety_identifier=` | py, js/ts |
| `openai-missing-max-tokens` | `chat.completions.create()` without `max_tokens=` | py, js/ts |
| `anthropic-missing-system-prompt` | `messages.create()` without `system=` | py, js/ts |
| `anthropic-missing-max-tokens` | `messages.create()` without `max_tokens=` | py, js/ts |
| `anthropic-missing-metadata-user-id` | `messages.create()` without `metadata=` for user tracking | py, js/ts |
| `gemini-missing-safety-settings` | `generate_content()` without `safety_settings=` | py, js/ts |
| `gemini-missing-system-instruction` | `GenerativeModel()` without `system_instruction=` | py, js/ts |
| `mistral-missing-safe-prompt` | `chat.complete()` without `safe_prompt=` | py, js/ts |
| `cohere-missing-safety-mode` | `chat()` without `safety_mode=` | py, js/ts |

### Prompt Injection (taint analysis)

| Rule | What it catches | Languages |
|------|----------------|-----------|
| `openai-user-input-in-system-prompt` | Request data &rarr; system message content | py, js/ts |
| `anthropic-user-input-in-system-prompt` | Request data &rarr; `system=` parameter | py, js/ts |
| `gemini-user-input-in-system-prompt` | Request data &rarr; `system_instruction=` | py, js/ts |

### Missing Safeguards

| Rule | What it catches | Languages |
|------|----------------|-----------|
| `openai-missing-system-message` | Chat completion without a system message | py, js/ts |
| `openai-missing-moderation` | Chat completion without moderation in same function | py |
| `openai-missing-moderation-check` | Moderation response accessed without checking `.flagged` | py |
| `mistral-missing-moderation` | Chat completion without `classifiers.moderate()` in same function | py |
| `cohere-safety-mode-off` | `safety_mode="OFF"` explicitly disabling safety | py, js/ts |
| `openai-no-error-handling` | OpenAI call outside try/except | py |
| `anthropic-no-error-handling` | Anthropic call outside try/except | py |
| `gemini-no-error-handling` | Gemini call outside try/except | py |
| `cohere-no-error-handling` | Cohere call outside try/except | py |
| `mistral-no-error-handling` | Mistral call outside try/except | py |
| `huggingface-no-error-handling` | HF Inference call outside try/except | py |

## Suppressing False Positives

```python
# nosemgrep: openai-missing-moderation
response = client.chat.completions.create(...)  # moderation handled in middleware
```

## Known Limitations

- **Go/Java**: Only credential detection rules (struct/builder patterns prevent reliable missing-field detection)
- **Taint sources**: Flask, Django, and Express only (Sanic, Koa, Hapi, FastAPI query params not covered)
- **Error handling**: Python only (JS/TS async patterns too varied for reliable detection)
- **Moderation rule**: Same-function scope (middleware-based moderation will false-positive)

## Contributing

1. Create a rule directory: `rules/<rule-id>/`
2. Write test files with `# ruleid:` and `# ok:` annotations
3. Write the YAML rule
4. Validate: `semgrep --validate --config rules/<rule-id>/`
5. Test: `cd rules/<rule-id>/ && semgrep --test`

See [rules/README.md](rules/README.md) for detailed documentation.

## References

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

## License

See [LICENSE](LICENSE) for details.
