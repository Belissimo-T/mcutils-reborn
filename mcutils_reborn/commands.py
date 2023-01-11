import abc
import typing

from . import MCFunction


class Command(abc.ABC):
    def get_str(self, path_of_func: typing.Callable[[MCFunction], str]) -> str:
        ...


class LiteralCommand(Command):
    def __init__(self, literal: str):
        self.literal = literal

    def get_str(self, path_of_func: typing.Callable[[MCFunction], str]) -> str:
        return self.literal


class FunctionCall(Command):
    def __init__(self, function: MCFunction):
        self.function = function

    def get_str(self, path_of_func: typing.Callable[[MCFunction], str]) -> str:
        return f"function {path_of_func(self.function)}"


class Comment(LiteralCommand):
    def __init__(self, comment: str):
        super().__init__(f"\n# {comment}")


class SayCommand(LiteralCommand):
    def __init__(self, message: str):
        super().__init__(f"say {message}")
