import typing

from .expressions import Expression
from .commands import UniqueString, Command, LiteralCommand, DynamicCommand
from .exceptions import CompilationError
from . import tellraw


def _print(*args: str | dict[str, str | bool] | Expression | tellraw.TextComponent,
           player: str | UniqueString = "@a", resolve: typing.Callable[[UniqueString | str], str]) -> list[str]:
    out = []

    text_components: list[tellraw.TextComponent] = []
    curr_text_kwargs = {}
    i = 0

    clean_ups = {}

    for arg in args:
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
        DynamicCommand(lambda resolve: "\n".join(_print(*args, player=player, resolve=resolve)))
    ]


def log(prefix: str, *args):
    """Print [prefix] *args."""
    return print_({"color": "light_purple"}, f"[{prefix}]", {"color": tellraw.UNSET}, " ", *args)
