.PHONY: help install export run build docker-build docker-run clean

default: help

help:
	@echo "Available commands:"
	@echo "  make install         - Install dependencies"
	@echo "  make export          - Export dependencies to requirements.txt"
	@echo "  make run             - Run the CLI application"
	@echo "  make build           - Build the Python package"
	@echo "  make clean           - Clean up temporary files"

install:
	uv pip install --requirements requirements.txt

export:
	uv export --format requirements-txt > requirements.txt

run:
	./.venv/bin/python3 src/safai/main.py $(ARGS)

build:
	uv build

clean:
	rm -rf __pycache__
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf dist
	rm -rf build
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete

uv_export:
	uv export --format requirements-txt > requirements.txt  

test:
	make uv_export && .venv/bin/pytest -s -v tests/ --asyncio-mode=auto\
		--cov=src \
		--cov-report term \
		--cov-report term-missing

fmt:
	uv run ruff format