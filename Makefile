.PHONY: install test lint verify clean

install:
	pip install -e ".[dev]"

test:
	@python3 scripts/preflight.py
	pytest -v --cov=driftcheck

lint:
	ruff check . && mypy driftcheck/

verify:
	@python -c "import driftcheck; print(f'v{driftcheck.__version__} OK')"

clean:
	rm -rf dist/ build/ *.egg-info
