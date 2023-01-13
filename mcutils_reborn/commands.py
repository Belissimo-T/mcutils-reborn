import abc
import re
import typing

from . import Function, MCFunction, Pathable
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

    def __eq__(self, other: "UniqueString"):
        return self.id == other.id

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.id}]({self.value!r})"

    def add_path(self, value: str) -> str:
        return f"{self.path_func(self.namespace.path())}.{value}"

    def get(self, existing_strings: set[str], resolve: typing.Callable[["UniqueString"], str]) -> str:
        i = 2
        out = self.add_path(self.value)

        while out in existing_strings:
            out = self.add_path(f"{self.value}.{i}")
            i += 1

        return out


class CompositeString(UniqueString):
    def __init__(self, value: str, *args):
        super().__init__(value, None)
        self.args = args

    def get(self, existing_strings: set[str], resolve: typing.Callable[["UniqueString"], str]) -> str:
        return self.value % tuple([resolve(arg) for arg in self.args])


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
    def get_unique_strings(self) -> typing.Sequence[UniqueString]:
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
        return [arg for arg in self.args if isinstance(arg, UniqueString)]


class FunctionCall(Command):
    def __init__(self, function: Pathable):
        assert not isinstance(function, Function), \
            "Argument to FunctionCall must not be a Function object. Use MCFunction or FunctionTag instead."

        self.function = function

    def get_str(self, path_of_func: typing.Callable[[Pathable], str], strings: dict[UniqueString, str]) -> str:
        return f"function {path_of_func(self.function)}"


class Comment(LiteralCommand):
    def __init__(self, comment: str):
        super().__init__(f"\n# {comment}")


class SayCommand(LiteralCommand):
    def __init__(self, message: str):
        super().__init__(f"say {message}")


class DynamicCommand(Command):
    def __init__(self, func: typing.Callable[[typing.Callable[[UniqueString | str], str]], str]):
        self.func = func

    def get_str(self, path_of_func: typing.Callable[[MCFunction], str], strings: dict[UniqueString, str]) -> str:
        def resolve(arg: UniqueString | str) -> str:
            if isinstance(arg, str):
                return arg

            return strings[arg]

        return self.func(resolve)
