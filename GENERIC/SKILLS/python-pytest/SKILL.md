---
name: python-pytest
description: Modern Python (3.11+) development and testing - project layout with uv and pyproject, typing, dataclasses and pydantic, API development with FastAPI, and pytest (fixtures, parametrize, monkeypatch, tmp_path, coverage.py). Use when writing, testing, reviewing or debugging Python code.
license: MIT
metadata:
  harness.type: skill
  harness.scope: generic
  harness.version: 1.0.0
  harness.status: active
  harness.applies-to: "stack:python,pytest,fastapi"
  harness.sources: "https://docs.pytest.org/en/stable/, https://docs.astral.sh/uv/, https://typing.python.org/en/latest/, https://fastapi.tiangolo.com/tutorial/testing/, https://coverage.readthedocs.io/, https://github.com/trailofbits/skills/tree/main/plugins/modern-python"
  harness.reviewed: "2026-10-12"
  harness.tags: "python,pytest,api"
---

# Python and pytest

## Project setup

- Declare everything in `pyproject.toml` (PEP 621). Use **uv** to manage the environment and the lockfile (`uv sync`, `uv run pytest`, `uv add <pkg>`) and commit `uv.lock` for applications. Use what the project already has (Poetry, pip-tools) and don't migrate unasked.
- Prefer the src layout (`src/<package>/`) for libraries, with tests in `tests/` mirroring the package.
- Lint and format with `ruff` and type-check with `mypy` or `pyright` in strict mode for new code. Run them in CI.
- Run scripts that read untrusted files in isolated mode (`python -I`).

## Code

- Use type hints everywhere public, with built-in generics (`list[str]`, `dict[str, int]`) and `X | None`. Use `dataclass(frozen=True, slots=True)` for value objects and pydantic models at I/O boundaries (API, config, files).
- Use `pathlib.Path` instead of `os.path`, and f-strings. Open files with `with` and an explicit `encoding="utf-8"`.
- Never use mutable default arguments or a bare `except:`. Catch specific exceptions and re-raise with context (`raise X from err`).
- Use `logging` (module-level `logger = logging.getLogger(__name__)`), never `print`, in libraries.
- Configuration comes from the environment (pydantic-settings) and secrets never go in code.
- Async: don't block the event loop (no `requests` or `time.sleep` inside `async def`). Use `httpx.AsyncClient` and `asyncio.TaskGroup`.

## APIs (FastAPI)

- Request and response models are pydantic classes, separate from persistence models. Validation happens at the edge.
- Use dependency injection (`Depends`) for sessions, auth and settings, and override it in tests with `app.dependency_overrides`.
- Return explicit status codes and problem-style errors, without leaking stack traces.
- Test through `fastapi.testclient.TestClient` (sync) or `httpx.AsyncClient` with `ASGITransport` (async).

## pytest

- Write plain `assert` statements, and test names that describe behaviour: `test_rejects_negative_amount`.
- **Fixtures** for setup, with the narrowest scope that works. Put shared fixtures in `conftest.py`. Prefer factory fixtures over global state.
- Use `@pytest.mark.parametrize` for input or output tables, with `ids=` for readability.
- Use the built-ins: `tmp_path` for files, `monkeypatch` for env vars and attributes, `caplog` for logs, `capsys` for stdout.
- Mock only at boundaries (HTTP, clock, external services) using `unittest.mock`/`pytest-mock`. Don't mock the code under test.
- Use `pytest.raises(Error, match="...")` for errors.
- Integration tests run against real dependencies (Testcontainers or a dedicated test database), never the database the app uses. Mark slow ones (`@pytest.mark.integration`) and register the markers in `pyproject.toml`.
- Property-based testing (`hypothesis`) suits parsers, serializers and invariants.

## Coverage

- `uv run pytest --cov=<package> --cov-branch --cov-report=term-missing --cov-report=xml`. Branch coverage (`--cov-branch`) is what reveals untested conditions.
- Read the `Missing` column and add meaningful tests. Reserve `# pragma: no cover` for truly unreachable code, and justify it.

## Review checklist

- [ ] Types on public functions, and no `Any` leaks at the boundary.
- [ ] Errors are specific and keep their context.
- [ ] Tests cover the happy path, the edge cases and the failure paths, and they fail without the change.
- [ ] No network or real database in unit tests, and integration tests are isolated.
