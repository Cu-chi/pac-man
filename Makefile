PYTHON = python3
SRC = src
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
--disallow-untyped-defs --check-untyped-defs
VENV = .venv
CONFIG = config.json

install:
	uv sync

run:
	uv run $(PYTHON) $(SRC) $(CONFIG)

debug:
	uv run $(PYTHON) -m pdb $(SRC) $(CONFIG)

clean:
	@rm -rf $$(find . -type d -name "__pycache__") $$(find . -type d -name ".mypy_cache")

lint:
	uv run $(PYTHON) -m flake8 . --exclude $(VENV)
	uv run $(PYTHON) -m mypy . $(MYPY_FLAGS)

lint-strict:
	uv run $(PYTHON) -m flake8 . --exclude $(VENV)
	uv run $(PYTHON) -m mypy . $(MYPY_FLAGS) --strict

.PHONY: install run debug clean lint lint-strict
