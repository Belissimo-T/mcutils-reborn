from .command import *
from .expression import *
from .paths import *

import typing


class Pathable:
    parent: typing.Optional["Namespace"] = None
    name: str

    def path(self) -> list[str]:
        if self.parent is None:
            return [self.name]

        return [*self.parent.path(), self.name]


class Namespace(Pathable):
    def __init__(self, name: str):
        self.name = name
        self.children: dict[str, Pathable] = {}

    def create_namespace(self, *args, **kwargs) -> "Namespace":
        namespace = Namespace(*args, **kwargs)
        self.add(namespace)

        return namespace

    def create_function(self, *args, **kwargs) -> "Function":
        function = Function(*args, **kwargs)
        self.add(function)

        return function

    def create_mcfunction(self, *args, **kwargs) -> "MCFunction":
        mcfunction = MCFunction(*args, **kwargs)
        self.add(mcfunction)

        return mcfunction

    def create_function_tag(self, name: str) -> "FunctionTag":
        function_tag = FunctionTag(name, self)
        function_tag.parent = self

        return function_tag

    def create_class(self, *args, **kwargs) -> "Class":
        cls = Class(*args, **kwargs)
        self.add(cls)

        return cls

    def create_template(self, *args, **kwargs) -> "Template":
        template = Template(*args, **kwargs)
        self.add(template)

        return template

    def get_unique_scoreboard_var(self, player: str, objective: "str | UniqueString | None" = None) -> "ScoreboardVar":
        if objective is None:
            from .lib.std import STD_OBJECTIVE
            objective = STD_OBJECTIVE

        return ScoreboardVar(UniqueScoreboardPlayer(player, self), objective)

    def get(self, name: str):
        return self.children[name]

    def get_all_mcfunctions(self) -> dict[tuple[str, ...], "MCFunction"]:
        mcfunctions = {}

        for child in self.children.values():
            if isinstance(child, MCFunction):
                mcfunctions[tuple(child.path())] = child

            elif isinstance(child, Namespace):
                if isinstance(child, Function):
                    assert child.was_ended, f"Function {path_to_str(child.path())} was not ended"

                mcfunctions |= child.get_all_mcfunctions()

        return mcfunctions

    def add(self, *namespaces: Pathable):
        for namespace in namespaces:
            self.children[namespace.name] = namespace
            namespace.parent = self

    def __repr__(self):
        return path_to_str(self.path())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        pass


class FunctionTag(Pathable):
    def __init__(self, name: str, parent: Namespace):
        self.name = name
        self.parent = parent


class MCFunction(Pathable):
    """Represents a single .mcfunction file."""

    def __init__(self, name: str, tags: set[str | FunctionTag] | None = None, description: str = ""):
        self.description = description
        self.name = name
        self.tags = set() if tags is None else tags
        self.commands: list[Command] = []
        self.continuation: MCFunction | None = None

    def add_command(self, *commands_: "Command"):
        self.commands.extend(commands_)


class Template(Namespace):
    def __init__(self, name: str, template: typing.Callable[[...], "Function"]):
        super().__init__(name)

        self.template = template
        self.functions: dict[tuple[tuple[str, typing.Any], ...], Function] = {}

    def __call__(self, **kwargs):
        # noinspection PyTypeChecker
        converted_kwargs: tuple[tuple[str, typing.Any]] = tuple(kwargs.items())

        if converted_kwargs not in self.functions:
            func = self.template(**kwargs)
            func.end()
            self.functions[converted_kwargs] = func
            self.add(func)

        return self.functions[converted_kwargs]


class Class(Namespace):
    def __init__(self, name: str, inherits_from: typing.Iterable["Class"] = ()):
        super().__init__(name)

        self.inherits_from = inherits_from

    def get(self, name: str):
        try:
            return super().get(name)
        except KeyError:
            for parent in self.inherits_from:
                try:
                    return parent.get(name)
                except KeyError:
                    continue

            raise


from .function import Function
