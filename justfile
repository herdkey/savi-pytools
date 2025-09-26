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

# Run linting checks
[group('lint')]
lint:
    poetry run ruff check

# Auto-fix linting issues
[group('lint')]
lint-fix:
    poetry run ruff check --fix

# Format code
[group('lint')]
format:
    poetry run ruff format

# Check formatting without making changes
[group('lint')]
format-check:
    poetry run ruff format --check
