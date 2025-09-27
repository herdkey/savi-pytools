import '.justfiles/base.just'

# Install source & dependency packages into venv.
[group('setup')]
install:
    poetry install

# Install this package globally (in editable mode) to make available for use anywhere on this system.
[group('setup')]
global-install:
    pipx install --force --editable "{{ justfile_dir() }}"

# Remove the global installation.
[group('setup')]
global-uninstall:
    pipx uninstall savi-pytools

# Run linting (auto-fix in dev mode, check-only in CI)
[group('linters')]
lint:
    poetry run ruff check {{ if dev_mode == "true" { "--fix" } else { "" } }}

# Format code (auto-fix in dev mode, check-only in CI)
[group('linters')]
format:
    poetry run ruff format {{ if dev_mode == "true" { "" } else { "--check" } }}

# Run mypy type checking
[group('typecheck')]
mypy:
    poetry run mypy

# Run pyright type checking
[group('typecheck')]
pyright:
    poetry run pyright

# Run both type checkers
[group('typecheck')]
typecheck:
    poetry run mypy
    poetry run pyright

# Run all checks (lint + format + typecheck)
[group('check')]
check-all: lint format typecheck
