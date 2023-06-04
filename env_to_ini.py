import yaml
import configparser
from rich.console import Console
from rich.table import Table

import typer
from typing import Optional, Tuple

app = typer.Typer()
console = Console()


# NOTE: utility function to print colored text
def cprint(style:str, text:str) -> None:
    console.print(f"[{style}]{text}[/{style}]")

def has_channel(requirements_str:str) -> bool:
    return '::' in requirements_str

def extract_channel(requirements_str:str) -> Tuple[Optional[str], str]:
    channel = None    
    if has_channel(requirements_str):
        channel, requirements_str = requirements_str.split('::', 1)        
    return channel, requirements_str

def is_not_valid_package_char(s:str) -> bool:
    return not (s.isalnum() or s in ['-', '_', '.'])

def split_str_at_first_non_alpha(s:str) -> Tuple[str, str]:
    idx = next((
            i for i, char in enumerate(s) 
            if is_not_valid_package_char(char)
        ), len(s))
    return s[:idx], s[idx:]

def split_package_version(s:str) -> Tuple[str, str]:
    # NOTE: alias for split_str_at_first_non_alpha
    return split_str_at_first_non_alpha(s)


# NOTE: this parses requirements from the settings.ini file. Thus there is one line and each package is separated by a space.
def parse_requirements(requirements_str):
    requirements = {}
    for req in requirements_str.split():
        package, version = split_package_version(req)
        requirements[package] = version
    return requirements

# NOTE: this parse depdencies form the env.yml file.
def extract_packages(dependencies):
    packages = {}
    for dep in dependencies:

        if isinstance(dep, str):
            channel, package_version = extract_channel(dep)
            package, version = split_package_version(package_version)


            # TODO: IMPROVEMENT 1: utilize a list of packages to exclude.
            #       by default this would include python and pip.
            
            # NOTE: we do not need to add python to the requirements
            if package == 'python':
                continue

            # NOTE: likewise we do not need pip
            elif package == 'pip':
                continue


            packages[package] = version
        
        elif isinstance(dep, dict):
            for key, values in dep.items():                
                if key == 'pip':
                    for pip_dep in values:                        
                        package, version = split_package_version(pip_dep)                        
                        packages[package] = version                        
    return packages

# NOTE: check if the depdencies in the env.yml file vary from the ones in the settings.ini file.
def compare_requirements(old, new):
    added = {k: v for k, v in new.items() if k not in old}
    removed = {k: v for k, v in old.items() if k not in new}
    changed = {k: (old[k], new[k]) for k in old if k in new and old[k] != new[k]}
    remained = {k: (old[k], new[k]) for k in old if k in new and old[k] == new[k]}
    return added, removed, changed, remained

# NOTE: I like pretty terminals
def print_changes(added, removed, changed, remained):
    table = Table(title="Changes")
    table.add_column("Package", style="cyan")
    table.add_column("Old Version", style="magenta")
    table.add_column("New Version", style="green")
    table.add_column("Status", style="yellow")

    for package, version in added.items():
        table.add_row(f':package: {package}', "", version, "Added")
    for package, version in removed.items():
        table.add_row(f':package: {package}', version, "", "Removed")        
    for package, versions in changed.items():
        table.add_row(f':package: {package}', versions[0], versions[1], "Changed")
    for package, versions in remained.items():
        table.add_row(f':package: {package}', versions[0], versions[1], "Unchanged")

    console.print(table)


def requirements_to_ini(requirments:dict) -> str:
    ini = ''
    for package, version in requirments.items():
        # TODO: IMPROVEMENT 2: utilize a map of packages to rename.
        #       by default this would include pytorch --> torch.
        #       Ideally, this would figure it out automatically.

        # NOTE: this is a hack to make the env.yml file compatible with the settings.ini file
        #       since the env.yml file uses pytorch and the settings.ini file uses torch.
        #       Add more elif statements if you need to change other package names.
        if package == 'pytorch':
            package = 'torch'

        if version:
            ini += f"{package}{version} "
        else:
            ini += f"{package} "
    return ini


@app.command()
def update_requirements(
    file: Optional[str] = typer.Option(
        'env.mac.yml', 
        help="YAML file to extract the new requirements from.",
    ),
    unchanged: Optional[bool] = typer.Option(
        False,
        help="Whether to print all packages, including the ones whose versions haven't changed.",
    ),
):
    # NOTE: notice that file is `env.mac.yml` and not `env.yml`. Now with Apple Silicon I have 
    #       one env file for more common CUDA versions and one for Apple Silicon.
    
    cprint("bold cyan", f"Loading environment yaml file {file}...")
    with open(file, 'r') as f:
        env = yaml.safe_load(f)


    # NOTE: read in the current dependencies from the conda env.yml file
    cprint("bold cyan", "Extracting packages and their versions...")
    new_requirements = extract_packages(env['dependencies'])

    # NOTE: read in the previous requirements from the settings.ini file
    cprint("bold cyan", "Loading settings.ini file...")
    config = configparser.ConfigParser()
    config.read('settings.ini')

    cprint("bold cyan", "Comparing the old and new requirements...")
    old_requirements = parse_requirements(config['DEFAULT']['requirements'])

    # NOTE: check for changes
    added, removed, changed, remained = compare_requirements(old_requirements, new_requirements)

    # If --unchanged option is given, print unchanged packages as well
    if unchanged:
        print_changes(added, removed, changed, remained)
    else:
        print_changes(added, removed, changed, {})

    # NOTE: update the requirements in the settings.ini file
    cprint("bold cyan", "Updating the requirements...")
    config['DEFAULT']['requirements'] = requirements_to_ini(new_requirements)

    cprint("bold cyan", "Saving the updated settings.ini file...")
    with open('settings.ini', 'w') as f:
        config.write(f)

    cprint("bold green", "Successfully updated the requirements in settings.ini!")

if __name__ == "__main__":
    app()
