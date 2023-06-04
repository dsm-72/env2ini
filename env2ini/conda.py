# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/09_conda.ipynb.

# %% auto 0
__all__ = []

# %% ../nbs/09_conda.ipynb 3
#| eval: false
from conda.plugins import hookimpl, CondaSubcommand

# %% ../nbs/09_conda.ipynb 4
from .commands import run_export_conda_to_ini

# %% ../nbs/09_conda.ipynb 5
#| eval: false
@hookimpl
def conda_subcommands():
    yield CondaSubcommand(name='env2ini', action=run_export_conda_to_ini, summary=run_export_conda_to_ini.__doc__)

