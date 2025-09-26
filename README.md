# Savi PyTools

## Setup

1. **Install pyenv**: `brew install pyenv`.
2. **Set global python version**: `pyenv global 3.13`.
3. **Install python**: `pyenv install`.
4. **Install pipx**: `brew install pipx`.
5. **Set pipx python version**: Add this to your `~/.zshrc`:
    ```shell
    # Make pipx use pyenv's global python
    export PIPX_DEFAULT_PYTHON="$(
        # Get the first version in the list, since it can contain multiple, e.g. "3.13 3.12"
        first_global=$(pyenv global | awk '{print $1}')
        # Resolve aliases like 3.13 to the actual version, like 3.13.7
        pyenv prefix "$first_global"
    )/bin/python"
    ```
   Then run `source ~/.zshrc`.
6. **Install poetry**: `pipx install poetry`.
7. **Setup venv**: `poetry env use "$(pyenv which python)"`
8. **Install packages**: `poetry install`.

## Usage

This project is intended to be used globally throughout your system. However, for convenience, we expected developers to keep a copy of this repo cloned locally, and to use the tools from source.

To make this available globally, run `just global-install`

