# mac-control-mcp Agent Rules

## Python Stack
- **Package manager:** `uv` only (no pip, pipx, poetry, conda)
- **Lint:** `uvx ruff check`
- **Format:** `uvx ruff format`
- **Type check:** `uvx pyright`
- **Test:** `uv run pytest --cov --cov-branch --cov-fail-under=90`
- **Mutation:** `uv run mutmut run`

## CI/CD
- **SonarCloud:** project key `Jonathangadeaharder_mac-control-mcp`, organization `jonathangadeaharder`
- **PR gate:** runs on `ubuntu-latest`, unit tests only (integration/e2e auto-skipped on non-macOS)
- **Merge gate:** adds CodeQL, mutation testing, SonarCloud scan
- **PR-Agent:** self-hosted macOS runner, slash-command only (`/review`, `/describe`, etc.)

## macOS-Specific Testing
- Unit tests (`@pytest.mark.unit`) are pure logic — no system calls, run anywhere
- Integration tests (`@pytest.mark.integration`) require macOS + accessibility permissions
- E2E tests (`@pytest.mark.e2e`) require full macOS stack
- Set `LIVE_TESTS=0` to skip live macOS calls

## Git Workflow
- No direct pushes to `main`/`master`
- Branch: `feature/*`, `fix/*`, `chore/*`
- PR → automated review (CodeRabbit, fallback PR-Agent) → squash merge
