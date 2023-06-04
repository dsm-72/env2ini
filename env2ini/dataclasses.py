# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_dataclasses.ipynb.

# %% auto 0
__all__ = ['Dependency', 'CondaDependency', 'IniRequirement', 'DependencyList']

# %% ../nbs/05_dataclasses.ipynb 3
from rich.repr import auto as rich_auto
from dataclasses import dataclass, field

from typing import (
    ClassVar, List, Dict, Union, Optional, Tuple, Sequence, Set,
    Any, TypeVar, Type, Callable, cast, no_type_check
)

# %% ../nbs/05_dataclasses.ipynb 4
from env2ini.constants import (
    PIP, DEP_SEP, PYPI_NAME, CONDA_NAME, 
    DEFAULT_DEPENDENCIES_TO_IGNORE
)

from .utils import (split_package_str_at_first_non_alpha)
from env2ini.types import (
    YamlDependencyStr, IniRequirementStr, YamlFileItem, 
    YamlDependencies, Dependencies, CondaDependencies, IniRequirements
)

# %% ../nbs/05_dataclasses.ipynb 6
@dataclass
@rich_auto(angular=True)
class Dependency(object):
    """
    Represents a software dependency with a package name and optional version.

    Parameters
    ----------
    package : str
        The name of the package.

    version : Optional[str], optional
        The version of the package.

    Attributes
    ----------
    _alias_kinds : ClassVar[List[str]]
        List of strings that represent aliases for the package name.

    Notes
    -----
    - version includes the version operator (e.g. `==`, `>=`, `~=`, etc.)
    """
    package: str
    version: Optional[str] = None
    _alias_kinds: ClassVar[List[str]] = [CONDA_NAME, PYPI_NAME]

    @staticmethod
    def separate_package_from_version(package_version: str) -> Tuple[str, str]:
        """
        Separates a package-version string into the package name and version.

        Parameters
        ----------
        package_version : str
            The package-version string.

        Returns
        -------
        Tuple[str, str]
            The package name and version.
        """
        package, version = split_package_str_at_first_non_alpha(package_version)
        return package, version

    def get_alias(self, kind: str, default: Optional[str] = None) -> str:
        """
        Returns an alias for the package name.

        Parameters
        ----------
        kind : str
            The kind of alias to return.
        default : Optional[str], optional
            The default value to return if no alias of the specified kind exists.

        Returns
        -------
        str
            The alias of the specified kind, or the default value.
        """
        alt_name = getattr(self, kind, None)
        fallback = (default or self.package)
        return alt_name or fallback

    def get_aliases(self) -> Set[str]:
        """
        Returns all aliases for the package name.

        Returns
        -------
        Set[str]
            A set of all aliases for the package name.
        """
        pkgs = [self.package]
        for kind in self._alias_kinds:
            pkgs.append(self.get_alias(kind))
        return set(pkgs)

    @property
    def aliases(self) -> Set[str]:
        """
        Returns all aliases for the package name.

        Returns
        -------
        Set[str]
            A set of all aliases for the package name.
        """
        try:
            return self._aliases
        except AttributeError:
            self._aliases = self.get_aliases()
            return self._aliases

    @property
    def conda_package(self) -> str:
        """
        Returns the Conda package name.

        Returns
        -------
        str
            The Conda package name.
        """
        try:
            return self._conda_package
        except AttributeError:
            self._conda_package = self.get_alias(CONDA_NAME)
            return self._conda_package

    @property
    def pypi_package(self) -> str:
        """
        Returns the PyPI package name.

        Returns
        -------
        str
            The PyPI package name.
        """
        try:
            return self._pypi_package
        except AttributeError:
            self._pypi_package = self.get_alias(PYPI_NAME)
            return self._pypi_package

    def is_same_package(self, other: 'Dependency') -> bool:
        """
        Checks if two dependencies are for the same package.

        Parameters
        ----------
        other : Dependency
            The other Dependency to compare.

        Returns
        -------
        bool
            True if they are for the same package, False otherwise.
        """
        return bool(set(self.aliases) & set(other.aliases))

    def is_same_version(self, other: 'Dependency') -> bool:
        """
        Checks if two dependencies are for the same version.

        Parameters
        ----------
        other : Dependency
            The other Dependency to compare.

        Returns
        -------
        bool
            True if they are for the same version, False otherwise.
        """
        return self.version == other.version

    def __eq__(self, other):
        """
        Checks if two dependencies are equal.

        Parameters
        ----------
        other : object
            The object to compare.

        Returns
        -------
        bool
            True if the dependencies are equal, False otherwise.
        """
        if isinstance(other, (Dependency, IniRequirement, CondaDependency)):
            return self.is_same_package(other) and self.version == other.version
        return super().__eq__(other)

    def __contains__(self, other):
        """
        Checks if the dependency contains the same package name as another dependency.

        Parameters
        ----------
        other : object
            The object to check.

        Returns
        -------
        bool
            True if the dependency contains the other dependency, False otherwise.

        Notes
        -----
            - This is equivalent to `self.is_same_package(other)`.
        """
        if isinstance(other, (Dependency, IniRequirement, CondaDependency)):
            return self.is_same_package(other)
        return super().__contains__(other)

    def to_conda_dependency(self, channel: Optional[str] = None) -> 'CondaDependency':
        """
        Converts the dependency to a CondaDependency.

        Parameters
        ----------
        channel : Optional[str], optional
            The Conda channel to use.

        Returns
        -------
        CondaDependency
            The converted CondaDependency object.
        """
        return CondaDependency(package=self.conda_package, version=self.version, channel=channel, pypi_name=self.package)

    def to_ini_requirement(self) -> 'IniRequirement':
        """
        Converts the dependency to an IniRequirement.

        Returns
        -------
        IniRequirement
            The converted IniRequirement object.
        """
        return IniRequirement(package=self.pypi_package, version=self.version, conda_name=self.package)

    def to_ini_str(self) -> IniRequirementStr:
        """
        Converts the dependency to an INI requirement string.

        Returns
        -------
        IniRequirementStr
            The INI requirement string.
        """
        ini_req = self.to_ini_requirement()

        if ini_req.version:
            return f'{ini_req.package}{ini_req.version}'
        return f'{ini_req.package}'

    def to_yml_str(self) -> str:
        """
        Converts the dependency to a YAML string.

        Returns
        -------
        str
            The YAML string representation of the dependency.
        """
        yml_dep = self.to_conda_dependency()
        yml_str = ''

        if yml_dep.channel:
            yml_str += f'{yml_dep.channel}{DEP_SEP}'

        yml_str += f'{yml_dep.package}'

        if yml_dep.version:
            yml_str += f'{yml_dep.version}'
        return yml_str


# %% ../nbs/05_dataclasses.ipynb 8
@dataclass
@rich_auto(angular=True)
class CondaDependency(Dependency):
    """
    Represents a dependency from a Conda environment.

    Attributes
    ----------
    channel : str, optional
        The channel where the dependency is hosted.
    pypi_name : str, optional
        The name of the package in the PyPI repository, if different from the Conda package name.
    """
    channel: Optional[str] = None
    pypi_name: Optional[str] = None

    @staticmethod
    def has_channel(dependency: YamlDependencyStr) -> bool:
        """
        Checks if a dependency string includes a channel.

        Parameters
        ----------
        dependency : YamlDependencyStr
            The dependency string to check.

        Returns
        -------
        bool
            True if the dependency string includes a channel, False otherwise.
        """
        return DEP_SEP in dependency

    @staticmethod
    def extract_channel(dependency: YamlDependencyStr, default_channel: Optional[str] = None) -> Tuple[Optional[str], str]:
        """
        Extracts the channel and the package from a dependency string.

        Parameters
        ----------
        dependency : YamlDependencyStr
            The dependency string to extract from.
        default_channel : str, optional
            The default channel to return if no channel is found in the dependency string.

        Returns
        -------
        Tuple[Optional[str], str]
            The extracted channel and the package.
        """
        channel = default_channel
        if CondaDependency.has_channel(dependency):
            channel, dependency = dependency.split(DEP_SEP, 1)
        return channel, dependency

    @staticmethod
    def from_yml_str(
        dependency: YamlDependencyStr, 
        dependencies_to_ignore: Optional[List[str]] = DEFAULT_DEPENDENCIES_TO_IGNORE,
        dependency_aliases: Optional[str] = None
    ) -> Optional['CondaDependency']:
        """
        Creates a CondaDependency from a YAML dependency string.

        Parameters
        ----------
        dependency : YamlDependencyStr
            The dependency string to create a CondaDependency from.
        dependencies_to_ignore : list, optional
            A list of dependencies to ignore.

        Returns
        -------
        CondaDependency
            The created CondaDependency.
        """
        assert isinstance(dependency, YamlDependencyStr)
        pypi_name = None
        channel, dependency = CondaDependency.extract_channel(dependency)
        package, version = CondaDependency.separate_package_from_version(dependency)

        if package in dependencies_to_ignore:
            return None
        
        if dependency_aliases and package in dependency_aliases:
            pypi_name = dependency_aliases[package]
        
        if pypi_name in dependencies_to_ignore:
            return None

        return CondaDependency(package, version, channel, pypi_name=pypi_name)

    @staticmethod
    def from_yml_dict(
        yml_dict: dict, 
        dependencies_to_ignore: Optional[List[str]] = DEFAULT_DEPENDENCIES_TO_IGNORE,
        dependency_aliases: Optional[str] = None
    ) -> CondaDependencies:
        """
        Creates a list of CondaDependencies from a YAML dictionary.

        Parameters
        ----------
        yml_dict : dict
            The YAML dictionary to create CondaDependencies from.
        dependencies_to_ignore : list, optional
            A list of dependencies to ignore.

        Returns
        -------
        CondaDependencies
            The created list of CondaDependencies.
        """
        assert isinstance(yml_dict, dict)

        dependencies = []
        if PIP not in yml_dict:
            return dependencies

        pip_yml_strs = yml_dict[PIP]
        for dependency in pip_yml_strs:
            dep = CondaDependency.from_yml_str(dependency, dependencies_to_ignore, dependency_aliases)
            if dep is None:
                continue
            dependencies.append(dep)

        return dependencies

    @staticmethod
    def from_yml_line(
        yml_line: YamlFileItem,
        dependencies_to_ignore: Optional[List[str]] = DEFAULT_DEPENDENCIES_TO_IGNORE,
        dependency_aliases: Optional[str] = None
    ) -> Union['CondaDependency', CondaDependencies]:
        """
        Creates a CondaDependency or a list of CondaDependencies from a YAML line.

        Parameters
        ----------
        yml_line : YamlFileItem
            The YAML line to create a CondaDependency or CondaDependencies from.
        dependencies_to_ignore : list, optional
            A list of dependencies to ignore.

        Returns
        -------
        Union[CondaDependency, CondaDependencies]
            The created CondaDependency or list of CondaDependencies.
        """        
        if isinstance(yml_line, YamlDependencyStr):
            return CondaDependency.from_yml_str(yml_line, dependencies_to_ignore, dependency_aliases)
        elif isinstance(yml_line, dict):
            return CondaDependency.from_yml_dict(yml_line, dependencies_to_ignore, dependency_aliases)
        else:
            raise ValueError(f'Unexpected type: {type(yml_line)}')

    @staticmethod
    def load_yml_dependencies(
        yml_env_dependencies: List[YamlFileItem],
        dependencies_to_ignore: Optional[List[str]] = DEFAULT_DEPENDENCIES_TO_IGNORE,
        dependency_aliases: Optional[str] = None
    ) -> CondaDependencies:
        """
        Loads CondaDependencies from a list of YAML environment dependencies.

        Parameters
        ----------
        yml_env_dependencies : List[YamlFileItem]
            The list of YAML environment dependencies to load from.
        dependencies_to_ignore : list, optional
            A list of dependencies to ignore.

        Returns
        -------
        CondaDependencies
            The loaded CondaDependencies.
        """
        dependencies = []
        for yml_item in yml_env_dependencies:
            dep = CondaDependency.from_yml_line(yml_item, dependencies_to_ignore, dependency_aliases)
            if dep is None:
                continue

            elif isinstance(dep, Sequence) and all(isinstance(x, CondaDependency) for x in dep):
                dependencies.extend(dep)

            elif dep.package not in dependencies_to_ignore:
                dependencies.append(dep)

            else:
                continue

        return dependencies

    @staticmethod
    def dump_ini_requirements(dependencies: CondaDependencies) -> IniRequirementStr:
        """
        Converts a list of CondaDependencies to an INI requirements string.

        Parameters
        ----------
        dependencies : CondaDependencies
            The list of CondaDependencies to convert.

        Returns
        -------
        IniRequirementStr
            The INI requirements string.
        """
        requirements = ''
        for dep in dependencies:
            requirements += dep.to_ini_str() + ' '
        return requirements


# %% ../nbs/05_dataclasses.ipynb 10
@dataclass
@rich_auto(angular=True)
class IniRequirement(Dependency):
    """
    Represents a requirement specified in an INI file.

    Attributes
    ----------
    conda_name : str, optional
        The name of the package in the Conda environment.

    Methods
    -------
    from_ini_str(requirement: IniRequirementStr) -> 'IniRequirement':
        Creates an IniRequirement from an INI requirement string.

    load_ini_requirements(ini_requirements_str: IniRequirementStr, dependencies_to_ignore: Optional[List[str]] = DEFAULT_DEPENDENCIES_TO_IGNORE) -> IniRequirements:
        Loads IniRequirements from an INI requirements string.

    """
    conda_name: Optional[str] = None

    @staticmethod
    def from_ini_str(requirement: IniRequirementStr) -> 'IniRequirement':
        """
        Creates an IniRequirement from an INI requirement string.

        Parameters
        ----------
        requirement : IniRequirementStr
            The INI requirement string to create an IniRequirement from.

        Returns
        -------
        IniRequirement
            The created IniRequirement.
        """
        assert isinstance(requirement, IniRequirementStr)
        package, version = IniRequirement.separate_package_from_version(requirement)
        return IniRequirement(package, version)

    @staticmethod
    def load_ini_requirements(
        ini_requirements_str: IniRequirementStr,
        dependencies_to_ignore: Optional[List[str]] = DEFAULT_DEPENDENCIES_TO_IGNORE
    ) -> IniRequirements:
        """
        Loads IniRequirements from an INI requirements string.

        Parameters
        ----------
        ini_requirements_str : IniRequirementStr
            The INI requirements string to load from.
        dependencies_to_ignore : list, optional
            A list of dependencies to ignore.

        Returns
        -------
        IniRequirements
            The loaded IniRequirements.
        """
        dependencies = []
        requirements = ini_requirements_str.split()
        for req in requirements:
            dep = IniRequirement.from_ini_str(req)
            if dep.package in dependencies_to_ignore:
                continue
            dependencies.append(dep)
        return dependencies


# %% ../nbs/05_dataclasses.ipynb 12
@rich_auto(angular=True)
class DependencyList(list):
    """
    Represents a list of dependencies.

    Methods
    -------
    __contains__(other: Dependency) -> bool:
        Checks if the list contains a specific dependency.
    index(other: Dependency) -> int:
        Returns the index of a specific dependency in the list.
    find(other: Dependency) -> Optional[Dependency]:
        Finds a specific dependency in the list.
    find_all(other: Dependency) -> List[Dependency]:
        Finds all occurrences of a specific dependency in the list.
    __getitem__(dependency: Dependency) -> Optional[Dependency]:
        Gets a specific dependency from the list.
    find_added_packages(old_packages: Dependencies, new_packages: Dependencies) -> Dependencies:
        Finds the packages that were added between two sets of dependencies.
    find_removed_packages(old_packages: Dependencies, new_packages: Dependencies) -> Dependencies:
        Finds the packages that were removed between two sets of dependencies.
    find_changed_packages(old_packages: Dependencies, new_packages: Dependencies) -> Dependencies:
        Finds the packages that were changed between two sets of dependencies.
    find_unchanged_packages(old_packages: Dependencies, new_packages: Dependencies) -> Dependencies:
        Finds the packages that remained unchanged between two sets of dependencies.
    compare_requirements(old_packages: Dependencies, new_packages: Dependencies) -> Dependencies:
        Compares two sets of dependencies and returns the added, removed, changed, and unchanged packages.
    """
    def __contains__(self, other: Dependency) -> bool:
        """
        Checks if the list contains a specific dependency.

        Parameters
        ----------
        other : Dependency
            The dependency to check for.

        Returns
        -------
        bool
            True if the dependency is found in the list, False otherwise.
        """
        return any(other in dep for dep in self)

    def index(self, other: Dependency) -> int:
        """
        Returns the index of a specific dependency in the list.

        Parameters
        ----------
        other : Dependency
            The dependency to find the index of.

        Returns
        -------
        int
            The index of the dependency in the list.

        Raises
        ------
        ValueError
            If the dependency is not found in the list.
        """
        for i, dep in enumerate(self):
            if other in dep:
                return i
        raise ValueError(f'{other} not in {self.dependencies}')

    def find(self, other: Dependency) -> Optional[Dependency]:
        """
        Finds a specific dependency in the list.

        Parameters
        ----------
        other : Dependency
            The dependency to find.

        Returns
        -------
        Optional[Dependency]
            The found dependency, or None if not found.
        """
        for dep in self:
            if other in dep:
                return dep
        return None

    def find_all(self, other: Dependency) -> List[Dependency]:
        """
        Finds all occurrences of a specific dependency in the list.

        Parameters
        ----------
        other : Dependency
            The dependency to find.

        Returns
        -------
        List[Dependency]
            A list of all occurrences of the dependency in the list.
        """
        results = []
        for dep in self:
            if other in dep:
                results.append(dep)
        return results

    def __getitem__(self, dependency: Dependency) -> Optional[Dependency]:
        """
        Gets a specific dependency from the list.

        Parameters
        ----------
        dependency : Dependency
            The dependency to get from the list.

        Returns
        -------
        Optional[Dependency]
            The found dependency, or None if not found.
        """
        return self.find(dependency)

    @staticmethod
    def find_added_packages(old_packages: Dependencies, new_packages: Dependencies) -> Dependencies:
        """
        Finds the packages that were added between two sets of dependencies.

        Parameters
        ----------
        old_packages : Dependencies
            The old set of dependencies.
        new_packages : Dependencies
            The new set of dependencies.

        Returns
        -------
        Dependencies
            The packages that were added between the two sets of dependencies.
        """
        old_pkgs = DependencyList(old_packages)
        new_pkgs = [pkg for pkg in new_packages if pkg not in old_pkgs]
        return new_pkgs

    @staticmethod
    def find_removed_packages(old_packages: Dependencies, new_packages: Dependencies) -> Dependencies:
        """
        Finds the packages that were removed between two sets of dependencies.

        Parameters
        ----------
        old_packages : Dependencies
            The old set of dependencies.
        new_packages : Dependencies
            The new set of dependencies.

        Returns
        -------
        Dependencies
            The packages that were removed between the two sets of dependencies.
        """
        new_pkgs = DependencyList(new_packages)
        old_pkgs = [pkg for pkg in old_packages if pkg not in new_pkgs]
        return old_pkgs

    @staticmethod
    def find_changed_packages(old_packages: Dependencies, new_packages: Dependencies) -> Dependencies:
        """
        Finds the packages that were changed between two sets of dependencies.

        Parameters
        ----------
        old_packages : Dependencies
            The old set of dependencies.
        new_packages : Dependencies
            The new set of dependencies.

        Returns
        -------
        Dependencies
            The packages that were changed between the two sets of dependencies.
        """
        old_pkgs = DependencyList(old_packages)
        new_pkgs = DependencyList(new_packages)

        old_as_new = list(map(lambda pkg: new_pkgs.find(pkg), old_pkgs))

        changed = [
            (pkg, old_as_new[i]) for i, pkg in enumerate(old_pkgs)
            if old_as_new[i] and not pkg.is_same_version(old_as_new[i])
        ]
        return changed

    @staticmethod
    def find_unchanged_packages(old_packages: Dependencies, new_packages: Dependencies) -> Dependencies:
        """
        Finds the packages that remained unchanged between two sets of dependencies.

        Parameters
        ----------
        old_packages : Dependencies
            The old set of dependencies.
        new_packages : Dependencies
            The new set of dependencies.

        Returns
        -------
        Dependencies
            The packages that remained unchanged between the two sets of dependencies.
        """
        old_pkgs = DependencyList(old_packages)
        new_pkgs = DependencyList(new_packages)
        old_as_new = list(map(lambda pkg: new_pkgs.find(pkg), old_pkgs))

        unchanged = [
            (pkg, old_as_new[i]) for i, pkg in enumerate(old_pkgs)
            if old_as_new[i] and pkg.is_same_version(old_as_new[i])
        ]
        return unchanged

    @staticmethod
    def compare_requirements(old_packages: Dependencies, new_packages: Dependencies) -> Dependencies:
        """
        Compares two sets of dependencies and returns the added, removed, changed, and unchanged packages.

        Parameters
        ----------
        old_packages : Dependencies
            The old set of dependencies.
        new_packages : Dependencies
            The new set of dependencies.

        Returns
        -------
        Dependencies
            A tuple containing the added, removed, changed, and unchanged packages.
        """
        added = DependencyList.find_added_packages(old_packages, new_packages)
        removed = DependencyList.find_removed_packages(old_packages, new_packages)
        changed = DependencyList.find_changed_packages(old_packages, new_packages)
        remained = DependencyList.find_unchanged_packages(old_packages, new_packages)
        return added, removed, changed, remained
