# AI Best Practices — Semgrep Rules

Semgrep rules that catch common trust & safety mistakes in LLM-powered applications. Scan any codebase in seconds to find hardcoded API keys, missing safety checks, prompt injection risks, and unhandled errors across all major AI providers.

**58 rules | 102 sub-rules | 6 providers + MCP + Claude Code & Cursor hooks + LangChain | 7 languages**

## Quick Start

```bash
pip install semgrep
git clone https://github.com/semgrep/ai-best-practices.git
semgrep --config ai-best-practices/rules/ /path/to/your/project/
```

## What It Catches

| Category | Example | Severity |
|----------|---------|----------|
| **Hardcoded API keys** | `OpenAI(api_key="sk-abc123...")` | ERROR |
| **Prompt injection** | User input flowing into system prompts | ERROR |
| **Missing refusal handling** | Accessing response content without checking for refusals | WARNING |
| **Missing safety settings** | Gemini calls without `safety_settings` | WARNING |
| **No error handling** | API calls outside try/except blocks | WARNING |
| **Missing moderation** | Chat completions without moderation checks | WARNING |
| **Hooks security** | Unsafe input handling, path traversal, command injection in Claude Code and Cursor hooks | WARNING/ERROR |
| **MCP server flaws** | Command injection, SSRF, tool poisoning, credential leaks in MCP servers | ERROR |
| **Agentic code execution** | LLM output flowing to `eval`/`exec`/`subprocess`, dangerous LangChain utilities | ERROR |
| **Config file attacks** | Hidden Unicode in AI config files, unsafe IDE/agent settings | ERROR |

## Providers & Languages

|  | Python | JS/TS | Go | Java | Ruby | Bash/Generic |
|--|:------:|:-----:|:--:|:----:|:----:|:----:|
| **OpenAI** | X | X | X | X | X | |
| **Anthropic** | X | X | X | X | X | |
| **Google Gemini** | X | X | X | X | | |
| **Cohere** | X | X | | | | |
| **Mistral** | X | X | | | | |
| **Hugging Face** | X | X | | | | |
| **MCP Servers** | X | | | | | X |
| **LangChain** | X | | | | | |
| **Claude Code & Cursor Hooks** | X | | | | | X |
| **IDE/Agent Config** | | | | | | X |

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
        uses: semgrep/semgrep-action@v1
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

## Suppressing False Positives

```python
# nosemgrep: openai-missing-moderation
response = client.chat.completions.create(...)  # moderation handled in middleware
```

## Known Limitations

- **Go/Java**: Only credential detection rules (struct/builder patterns prevent reliable missing-field detection)
- **Taint sources**: Flask, Django, and Express only (Sanic, Koa, Hapi, FastAPI query params not covered)
- **Error handling**: Most rules Python-only; OpenAI and Anthropic also support JS/TS try/catch detection
- **Moderation rule**: Same-function scope (middleware-based moderation will false-positive)
- **Ruby SDK patterns may vary**: The `ruby-openai` and Anthropic Ruby gems use different conventions than official SDKs

## Rule Catalog

### Hardcoded Credentials (7 rules)

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `openai-hardcoded-api-key` | ERROR | `OpenAI(api_key="sk-...")` and variants | py, js/ts, go, java, rb |
| `anthropic-hardcoded-api-key` | ERROR | `Anthropic(api_key="sk-ant-...")` and variants | py, js/ts, go, java, rb |
| `gemini-hardcoded-api-key` | ERROR | `genai.configure(api_key="AIza...")` and variants | py, js/ts, go, java |
| `cohere-hardcoded-api-key` | ERROR | `cohere.Client(api_key="...")` and variants | py, js/ts |
| `mistral-hardcoded-api-key` | ERROR | `Mistral(api_key="...")` and variants | py, js/ts |
| `huggingface-hardcoded-api-key` | ERROR | `InferenceClient(token="hf_...")` and variants | py, js/ts |
| `llm-api-key-in-source` | ERROR | Any variable assigned a string matching known AI key prefixes (`sk-`, `sk-ant-`, `sk-proj-`, `AIza`, `hf_`) | py, js/ts, go, java, rb |

### Missing Safety Checks (12 rules)

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

### Prompt Injection (5 taint rules)

Uses Semgrep's taint analysis to trace data flow from web framework request objects (Flask, Django, Express) to LLM API system prompt parameters.

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `openai-user-input-in-system-prompt` | ERROR | User input &rarr; `{"role": "system", "content": X}` | py, js/ts |
| `anthropic-user-input-in-system-prompt` | ERROR | User input &rarr; `system=` parameter | py, js/ts |
| `gemini-user-input-in-system-prompt` | ERROR | User input &rarr; `system_instruction=` parameter | py, js/ts |
| `mistral-user-input-in-system-prompt` | ERROR | User input &rarr; `{"role": "system", "content": X}` | py, js/ts |
| `cohere-user-input-in-system-prompt` | ERROR | User input &rarr; `preamble=` parameter | py, js/ts |

### Missing Safeguards (11 rules)

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `openai-missing-system-message` | WARNING | `messages=[...]` with no `{"role": "system", ...}` | py, js/ts |
| `openai-missing-moderation` | WARNING | `chat.completions.create()` without `moderations.create()` in same function | py |
| `openai-missing-moderation-check` | WARNING | Moderation response accessed without checking `.flagged` | py |
| `mistral-missing-moderation` | WARNING | `chat.complete()` without `classifiers.moderate()` in same function | py |
| `cohere-safety-mode-off` | ERROR | `safety_mode="OFF"` explicitly disabling all safety guardrails | py, js/ts |
| `openai-no-error-handling` | WARNING | OpenAI API call not in try/except or try/catch | py, js/ts |
| `anthropic-no-error-handling` | WARNING | Anthropic API call not in try/except or try/catch | py, js/ts |
| `gemini-no-error-handling` | WARNING | Gemini API call not in try/except | py |
| `cohere-no-error-handling` | WARNING | Cohere API call not in try/except | py |
| `mistral-no-error-handling` | WARNING | Mistral API call not in try/except | py |
| `huggingface-no-error-handling` | WARNING | Hugging Face Inference API call not in try/except | py |

### Claude Code & Cursor Hooks Security (9 rules)

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `hooks-no-input-validation` | WARNING | `json.loads(sys.stdin.read())` without try/except; piping to eval/bash | py, bash |
| `hooks-unquoted-variable` | ERROR | Tainted stdin data flowing to `eval`, `bash -c`, `sh -c`, `exec` | bash |
| `hooks-path-traversal` | ERROR | Stdin JSON data used in file operations without `os.path.realpath()` | py, bash |
| `hooks-relative-script-path` | WARNING | `source ./...`, `bash ./...` — relative path script invocations | bash |
| `hooks-sensitive-file-access` | WARNING | Stdin JSON data used in file operations without sensitive file filtering | py, bash |
| `hooks-unconditional-allow` | ERROR | Hook always outputs `permissionDecision: "allow"` without conditional checks | generic |
| `hooks-stop-missing-active-check` | WARNING | Stop hook outputs `"block"` without checking `stop_hook_active` (infinite loop) | generic |
| `hooks-dns-exfiltration` | ERROR | DNS commands (`ping`, `nslookup`, `dig`) with variable expansion for data exfiltration | generic |
| `hooks-wget-pipe-bash` | ERROR | `curl ... \| bash` or `wget ... \| sh` remote code execution | generic |

### MCP Server Security (6 rules)

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `mcp-command-injection` | ERROR | `os.system()`, `subprocess(shell=True)`, `eval()` in `@mcp.tool()` handlers | py |
| `mcp-ssrf` | ERROR | Unvalidated URLs passed to `requests.get()`/`urllib` in MCP tools | py |
| `mcp-tool-poisoning` | ERROR | Suspicious directives (`<IMPORTANT>`, sensitive paths, "do not mention") in tool docstrings | generic |
| `mcp-unsanitized-return` | WARNING | External HTTP responses returned directly from MCP tools without sanitization | py |
| `mcp-credential-in-response` | WARNING | MCP tool return values containing credential keys (`api_key`, `token`, etc.) | py |
| `mcp-hardcoded-config-secret` | ERROR | Plaintext API keys (`sk-*`, `hf_*`, `AIza*`) in MCP config JSON files | generic |

### Agent Config File Security (5 rules)

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `ai-config-hidden-unicode` | ERROR | Invisible zero-width Unicode characters in `.cursorrules`, `copilot-instructions.md`, `CLAUDE.md` | generic |
| `ide-settings-executable-path` | WARNING | Executable path overrides in `.vscode/settings.json` pointing to relative paths | generic |
| `claude-settings-bypass-permissions` | ERROR | `bypassPermissions`, `allowUnsandboxedCommands`, `enableWeakerNestedSandbox` in settings | generic |
| `claude-settings-env-url-override` | ERROR | `ANTHROPIC_BASE_URL`/`OPENAI_BASE_URL` overrides redirecting API traffic | generic |
| `claude-settings-auto-enable-mcp` | WARNING | `enableAllProjectMcpServers: true` auto-loading untrusted MCP servers | generic |

### Agentic Code Execution Safety (3 rules)

| Rule ID | Severity | What it Detects | Languages |
|---------|----------|----------------|-----------|
| `llm-output-to-exec` | ERROR | LLM API response flowing to `eval()`, `exec()`, `subprocess(shell=True)`, `os.system()` | py, js/ts |
| `langchain-dangerous-exec` | ERROR | `PythonREPL.run()`, `BashProcess.run()`, `PythonAstREPLTool` usage | py |
| `agent-unbounded-loop` | WARNING | `while True` loop with LLM API calls and no `break` condition | py |

## Contributing

### Project structure

```
rules/<rule-id>/
  <rule-id>.yaml       # Semgrep rule definition (one or more sub-rules)
  <rule-id>.py         # Python test file
  <rule-id>.js         # JS/TS test file (if applicable)
  <rule-id>.go         # Go test file (if applicable)
```

### Adding a rule

1. Create a rule directory: `rules/<rule-id>/`
2. Write test files with `# ruleid:` and `# ok:` annotations
3. Write the YAML rule
4. Validate: `semgrep --validate --config rules/<rule-id>/`
5. Test: `semgrep --test rules/<rule-id>/`

### Running the full suite

```bash
# Validate all rules
semgrep --validate --config rules/

# Run all tests
semgrep --test rules/
```

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
- [Claude Code Hooks](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [Cursor Hooks](https://cursor.com/docs/agent/hooks)
- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)
- [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/)
- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [Pillar Security — Rules File Backdoor](https://www.pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents)
- [Trail of Bits — claude-code-config](https://github.com/trailofbits/claude-code-config)

## License

See [LICENSE](LICENSE) for details.
