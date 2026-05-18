.PHONY: install setup test lint verify clean

setup:
	@python3 -m venv .venv
	@. .venv/bin/activate && pip install -e ".[dev]" -q
	@python3 scripts/preflight.py
	@echo "✓ Environment ready"

test:
	pytest -v --cov=driftcheck

install:
	pip install -e ".[dev]"

lint:
	ruff check . && mypy driftcheck/

verify:
	@python3 -c "import driftcheck; print(f'v{driftcheck.__version__} OK')"

clean:
	rm -rf dist/ build/ *.egg-info .venv
