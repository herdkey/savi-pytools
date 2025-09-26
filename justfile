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
