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


class Function(Namespace):
    """Represents a function. May contain multiple mcfunctions."""

    def __init__(self, name: str, args: tuple[str] = (), *, description: str = "", tags: set[str | FunctionTag] = None,
                 entry_point_name: str | None = None):
        super().__init__(name)

        tags = set() if tags is None else tags

        self.args = args

        self.continuation: MCFunction | None = None
        self.entry_point = self.create_mcfunction(
            entry_point_name if entry_point_name is not None else self.name,
            tags=tags,
            description=description
        )
        self.current_mcfunction = self.entry_point

        self.was_ended = False

        self.init()

    def describe(self, description: str):
        self.entry_point.description = description

    def init(self):
        # pop arguments from stack into scoreboard vars
        # create local scope
        ...

    def add_command(self, *commands_: "Command"):
        assert not self.was_ended

        self.current_mcfunction.add_command(*commands_)

    def comment(self, *args, **kwargs):
        self.add_command(Comment(*args, **kwargs))

    def c_if(self, condition: "Condition") -> "Function":
        if_name = f"if{len(self.children)}"

        if_function = self.create_function(
            if_name,
            entry_point_name="branch",
            description=f"If-branch of {self.name}",
        )

        continuation_mcfunc = self.create_mcfunction(f"{if_name}-continue")

        cond_temp_var = self.get_unique_scoreboard_var("_cond")
        is_true_cond = ScoreConditionMatches(cond_temp_var, "1")

        is_true_cond_string, is_true_cond_u_strings = is_true_cond.to_str()
        cond_string, cond_u_strings = condition.to_str()
        self.add_command(
            # store condition result in (global!) temp var, recursion is prohibited!
            conversion.const_to_score(ConstInt(0), cond_temp_var),
            ComposedCommand(
                LiteralCommand(f"execute if {cond_string} run", *cond_u_strings),
                conversion.const_to_score(ConstInt(1), cond_temp_var)
            ),

            # if cond is true, call if_function
            ComposedCommand(
                LiteralCommand(f"execute if {is_true_cond_string} run", *is_true_cond_u_strings),
                FunctionCall(if_function.entry_point)
            ),
            # else just call the continuation
            ComposedCommand(
                LiteralCommand(f"execute unless {is_true_cond_string} run", *is_true_cond_u_strings),
                FunctionCall(continuation_mcfunc)
            )
        )

        if_function.continuation = self.current_mcfunction = continuation_mcfunc

        return if_function

    def c_while(self, condition: "Condition") -> "Function":
        while_name = f"while{len(self.children)}"
        while_function = self.create_function(
            while_name,
            entry_point_name="loop",
            description=f"While-loop of {self.name}",
        )

        iteration_number = self.get_unique_scoreboard_var("_iteration_number")
        while_function.add_command(
            *conversion.add_in_place(iteration_number, ConstInt(1))
        )

        check_cond_mcfunc = while_function.create_mcfunction(f"{while_name}-check-cond")

        continuation_mcfunc = self.create_mcfunction(f"{while_name}-continue")

        cond_str, ustr = condition.to_str()
        check_cond_mcfunc.add_command(
            ComposedCommand(
                LiteralCommand(f"execute if {cond_str} run", *ustr),
                FunctionCall(while_function.entry_point)
            )
        )
        check_cond_mcfunc.add_command(
            *add_in_place(iteration_number, ConstInt(-1))
        )

        is_first_iteration_cond = ScoreConditionMatches(iteration_number, "0")
        is_first_iteration_cond_str, is_first_iteration_cond_ustr = is_first_iteration_cond.to_str()
        check_cond_mcfunc.add_command(
            ComposedCommand(
                LiteralCommand(f"execute unless {cond_str} if {is_first_iteration_cond_str} run",
                               *ustr, *is_first_iteration_cond_ustr),
                FunctionCall(continuation_mcfunc)
            )
        )

        self.add_command(
            *var_to_var(ConstInt(0), iteration_number),
            FunctionCall(check_cond_mcfunc)
        )

        while_function.continuation = check_cond_mcfunc
        self.current_mcfunction = continuation_mcfunc

        return while_function

    def end(self):
        if self.was_ended:
            return

        self.current_mcfunction.continuation = self.continuation
        self.was_ended = True

    def return_(self, var: "Expression | None" = None):
        if var:
            from .lib.std import STD_RET

            self.add_command(
                *var_to_var(var, STD_RET)
            )

        self.continuation = None

    def __exit__(self, exc_type, exc_value, tb):
        self.end()


class Template(Namespace):
    def __init__(self, name: str, template: typing.Callable[[...], Function]):
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


from .commands import *
from .expressions import *
from .conversion import var_to_var, add_in_place
from .lib.std import *
from .exceptions import *
from .export import *
from .conditions import *
from . import tools
