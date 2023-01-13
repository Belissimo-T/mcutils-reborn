import typing

Path = typing.Sequence[str]


def path_to_str(path: Path) -> str:
    first, *rest = path

    return f"{first}:{'/'.join(rest)}"


def path_to_str2(path: Path) -> str:
    """Only use these allowed characters: (+-._A-Za-z0-9)"""

    first, *rest = path

    return f"{first}.{'.'.join(rest)}"
