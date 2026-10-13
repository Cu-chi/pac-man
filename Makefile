PYTHON = python3
MAIN = pac-man.py
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
--disallow-untyped-defs --check-untyped-defs
VENV = .venv
CONFIG = src/config.json
ITCH_TARGET ?= $(ITCH_USER)/pac-man
ITCH_CHANNEL ?= $(shell uname -s | tr A-Z a-z)

install:
	uv sync

run:
	uv run $(PYTHON) $(MAIN) $(CONFIG)

debug:
	uv run $(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	@rm -rf $$(find . -type d -name "__pycache__") $$(find . -type d -name ".mypy_cache")
	@rm -rf build dist

package:
	uv run --with pyinstaller pyinstaller pac-man.spec --noconfirm
	cp $(CONFIG) packaging/HOW_TO_PLAY.txt dist/pac-man/

publish: package
	butler push dist/pac-man $(ITCH_TARGET):$(ITCH_CHANNEL)

lint:
	uv run $(PYTHON) -m flake8 . --exclude $(VENV)
	uv run $(PYTHON) -m mypy . $(MYPY_FLAGS)

lint-strict:
	uv run $(PYTHON) -m flake8 . --exclude $(VENV)
	uv run $(PYTHON) -m mypy . $(MYPY_FLAGS) --strict

.PHONY: install run debug clean lint lint-strict package publish
