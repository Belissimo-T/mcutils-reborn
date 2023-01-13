import abc
import re
import typing

from . import MCFunction, Pathable
from . import paths

_UNIQUE_STRING_ID = 0


class UniqueString:
    path_func = staticmethod(paths.path_to_str)

    def __init__(self, value: str, namespace: Pathable | None = None):
        self.value = value
        self.namespace = namespace

        global _UNIQUE_STRING_ID
        self.id, _UNIQUE_STRING_ID = _UNIQUE_STRING_ID, _UNIQUE_STRING_ID + 1

    def __hash__(self):
        return hash((self.id, self.__class__.__name__, self.value))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value!r})"

    def transform(self, value: str, mcfunc: Pathable) -> str:
        return f"{self.path_func(mcfunc.path())}.{value}"

    def get(self, existing_strings: set[str], namespace: Pathable) -> str:
        namespace = namespace if self.namespace is None else self.namespace

        i = 2
        out = self.transform(self.value, namespace)

        while out in existing_strings:
            out = self.transform(f"{self.value}.{i}", namespace)
            i += 1

        return out


class UniqueRestrictedString(UniqueString):
    pattern = re.compile(r"^[a-zA-Z0-9_+\-.]+$")
    path_func = staticmethod(paths.path_to_str2)


class UniqueTag(UniqueRestrictedString): pass


class UniqueScoreboardObjective(UniqueRestrictedString): pass


class UniqueScoreboardPlayer(UniqueRestrictedString): pass


class Command(abc.ABC):
    def get_str(self, path_of_func: typing.Callable[[MCFunction], str], strings: dict[UniqueString, str]) -> str:
        ...

    # noinspection PyMethodMayBeStatic
    def get_unique_strings(self) -> typing.Iterable[UniqueString]:
        return ()


class LiteralCommand(Command):
    def __init__(self, literal: str, *args: UniqueString | str):
        self.literal = literal
        self.args: tuple[UniqueString | str, ...] = args

    def get_str(self, path_of_func: typing.Callable[[MCFunction], str], strings: dict[UniqueString, str]) -> str:
        format_args = tuple(
            strings[arg] if isinstance(arg, UniqueString) else arg
            for arg in self.args
        )

        return self.literal % format_args

    def get_unique_strings(self) -> typing.Iterable[UniqueString]:
        return self.args


class FunctionCall(Command):
    def __init__(self, function: MCFunction):
        self.function = function

    def get_str(self, path_of_func: typing.Callable[[MCFunction], str], strings: dict[UniqueString, str]) -> str:
        return f"function {path_of_func(self.function)}"


class Comment(LiteralCommand):
    def __init__(self, comment: str):
        super().__init__(f"\n# {comment}")


class SayCommand(LiteralCommand):
    def __init__(self, message: str):
        super().__init__(f"say {message}")
