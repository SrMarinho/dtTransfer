# Contributing

## Development Setup

```bash
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

## Running Tests

```bash
pytest                           # all tests
pytest -m unit                   # unit tests only
pytest -m integration            # integration tests (requires DB)
pytest tests/unit/test_cli.py    # single file
```

## Code Style

- Type hints required for all public functions
- Docstrings in English (Google style)
- Line length: 120

## Pull Request Process

1. Create a feature branch from `main`
2. Write tests for your change
3. Run `pytest` — all tests must pass
4. Open a PR with a clear description
