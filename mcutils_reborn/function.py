from .namespace import Namespace, FunctionTag, MCFunction
from .command import *
from . import conversion as conv
from .expression import *
from .condition import Condition, ScoreConditionMatches


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
            conv.const_to_score(ConstInt(0), cond_temp_var),
            ComposedCommand(
                LiteralCommand(f"execute if {cond_string} run", *cond_u_strings),
                conv.const_to_score(ConstInt(1), cond_temp_var)
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
            *conv.add_in_place(iteration_number, ConstInt(1))
        )

        check_cond_mcfunc = while_function.create_mcfunction(f"check-cond")

        continuation_mcfunc = self.create_mcfunction(f"{while_name}-continue")

        cond_str, ustr = condition.to_str()
        check_cond_mcfunc.add_command(
            ComposedCommand(
                LiteralCommand(f"execute if {cond_str} run", *ustr),
                FunctionCall(while_function.entry_point)
            )
        )
        check_cond_mcfunc.add_command(
            *conv.add_in_place(iteration_number, ConstInt(-1))
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
            *conv.var_to_var(ConstInt(0), iteration_number),
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
                *conv.var_to_var(var, STD_RET)
            )

        self.continuation = None

    def __exit__(self, exc_type, exc_value, tb):
        self.end()


class FunctionWithElse(Function):
    else_: Function
