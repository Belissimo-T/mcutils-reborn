import typing

from .expression import Expression, Variable
from . import conversion as conv
from .command import UniqueString, FunctionCall, PathString, DynamicCommand, UniqueTag, Command, Comment, \
    LiteralCommand, Function
from .exception import CompilationError
from .paths import path_to_str
from . import tellraw
from .namespace import Class


def call_function(function: "Function", *,
                  arg: "Expression | None" = None,
                  varargs: typing.Sequence["Expression"] = (),
                  target: Variable | None = None) -> list[Command]:
    out = [
        Comment(f"calling function %s"
                f"{' with STD_ARG' * bool(arg)}"
                f"{f' with {len(varargs)} varargs' * bool(varargs)}",
                PathString(function))
    ]

    if len(varargs) != len(function.args):
        raise CompilationError(
            f"Function {path_to_str(function.path())} has {len(function.args)} varargs, but {len(varargs)} were given.")

    for i, vararg in enumerate(varargs):
        from .lib.std import STD_ARGSTACK, std_stack_push

        out += call_function(std_stack_push(stack_nr=STD_ARGSTACK), arg=vararg)

    if arg is not None:
        from .lib.std import STD_ARG

        out += [
            *conv.var_to_var(arg, STD_ARG)
        ]

    out += [
        FunctionCall(function.entry_point)
    ]

    if target is not None:
        from .lib.std import STD_RET
        out += [
            *conv.var_to_var(STD_RET, target)
        ]

    return out


def create_object(class_: Class, args: tuple[Expression], target: Variable | None = None) -> list[Command]:
    from .lib import std

    return [
        *call_function(class_.get("__new__"), target=target),
        # STD_RET is the obj_id
        # STD_ARG is self argument
        *call_function(class_.get("__init__"), arg=std.STD_RET, varargs=args),
    ]


def _print(*args: str | dict[str, str | bool] | Expression | tellraw.TextComponent | UniqueString,
           player: str | UniqueString = "@a", resolve: typing.Callable[[UniqueString | str], str]) -> list[str]:
    out = []

    text_components: list[tellraw.TextComponent] = []
    curr_text_kwargs = {}
    i = 0

    clean_ups = {}

    for arg in args:
        if isinstance(arg, UniqueString):
            arg = resolve(arg)

        if isinstance(arg, str):
            text_components.append(tellraw.PlainText(arg, **curr_text_kwargs))
        elif isinstance(arg, Expression):
            commands, new_text_components = arg.to_tellraw(curr_text_kwargs, resolve)
            out += commands
            text_components += new_text_components

            clean_ups |= {i: arg}

            i += 1

        elif isinstance(arg, tellraw.TextComponent):
            text_components.append(arg)
        elif isinstance(arg, dict):
            curr_text_kwargs.update(arg)
        else:
            raise CompilationError(f"Can't print {arg!r}, must be one of str, dict, TextComponent, Expression.")

    out += [
        f"tellraw %s {tellraw.get_raw_json(*text_components)}" % resolve(player)
    ]

    # for i, clean_up in clean_ups.items():
    #     clean_up.post_to_tellraw()

    return out


def print_(*args: str | dict[str, str | bool] | Expression | tellraw.TextComponent,
           player: str | UniqueString = "@a") -> list[Command]:
    return [
        DynamicCommand(lambda path_of_func, resolve: "\n".join(_print(*args, player=player, resolve=resolve)))
    ]


def log(prefix: str | UniqueString | Expression | tellraw.TextComponent, *args):
    """Print [prefix] *args."""
    return print_({"color": "light_purple"}, "[", prefix, "]", {"color": tellraw.UNSET}, " ", *args)


def tag_remove_all(tag: UniqueTag | str) -> list[Command]:
    return [
        Comment("remove the temp tag from all entities"),
        LiteralCommand("tag @e remove %s", tag),
    ]
