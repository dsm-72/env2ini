# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_utils.ipynb.

# %% auto 0
__all__ = ['read_ini_file', 'to_macos_env_file', 'is_valid_conda_package_name_char', 'split_package_str_at_first_non_alpha',
           'parse_aliases']

# %% ../nbs/04_utils.ipynb 3
import os
import configparser
from typing import (Tuple, Optional)

# %% ../nbs/04_utils.ipynb 4
from .constants import SETTINGS_INI

# %% ../nbs/04_utils.ipynb 5
def read_ini_file(file: str = SETTINGS_INI) -> configparser.ConfigParser:    
    ini_cfg = configparser.ConfigParser()
    ini_cfg.read_file(file)    
    return ini_cfg

def to_macos_env_file(file: str) -> str:
    base_dir = os.path.dirname(file)
    yml_file = os.path.basename(file)
    mac_file = yml_file.replace('.yml', '.mac.yml')
    

    if os.path.exists(os.path.join(base_dir, mac_file)):
        return os.path.join(base_dir, mac_file)
    return file

# %% ../nbs/04_utils.ipynb 6
def is_valid_conda_package_name_char(char: str) -> bool:
    '''
    Used to split a package name from a version number.
    This is achieved by checking if a character is valid for 
    a conda package name. Since between the package name and
    the version number there is a space, or conditional (`>`, `<`, `=`, etc).    
    '''
    return char.isalnum() or char in ['-', '_', '.']

def split_package_str_at_first_non_alpha(package_str: str) -> Tuple[str, str]:
    idx = next((
        i for i, char in enumerate(package_str) 
        if not is_valid_conda_package_name_char(char)
    ), len(package_str))
    return package_str[:idx], package_str[idx:]

# %% ../nbs/04_utils.ipynb 7
def parse_aliases(alias_str: Optional[str]) -> dict:
    if alias_str is None:
        return {}

    packages = alias_str.split(';')
    result = {}
    for pkg_als in pkgs:
        pkg, als = pkg_als.split(':')
        pkg = pkg.strip()
        als = als.strip()
        result[pkg] = als
    return result