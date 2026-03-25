# AI Best Practices — Semgrep Rules

> **This repository has been deprecated.** All rules have been migrated to the official Semgrep registry.

## Where to find the rules

The rules now live in the official Semgrep rules repository:

**Source:** [github.com/semgrep/semgrep-rules/tree/develop/ai/ai-best-practices](https://github.com/semgrep/semgrep-rules/tree/develop/ai/ai-best-practices)

**Rule pack:** [semgrep.dev/p/ai-best-practices](https://semgrep.dev/p/ai-best-practices)

## Quick Start

```bash
pip install semgrep
semgrep --config "p/ai-best-practices" /path/to/your/project/
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
      - uses: semgrep/semgrep-action@v1
        with:
          config: "p/ai-best-practices"
```

### GitLab CI

```yaml
semgrep:
  image: semgrep/semgrep
  script:
    - semgrep --config "p/ai-best-practices" --error .
  rules:
    - if: $CI_MERGE_REQUEST_IID
```

## License

See [LICENSE](LICENSE) for details.
