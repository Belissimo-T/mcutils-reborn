from .. import Namespace
from ..commands import UniqueScoreboardObjective, Comment, FunctionCall, LiteralCommand
from .. import tools

std_namespace = Namespace("mcutils_reborn_std")
STD_OBJECTIVE = UniqueScoreboardObjective("mcutils_reborn", std_namespace)

STD_ARG = std_namespace.get_unique_scoreboard_var("arg")
STD_RET = std_namespace.get_unique_scoreboard_var("ret")

STD_LOAD_TAG = std_namespace.create_function_tag("load")

with std_namespace.create_function("load", tags={"minecraft:load"}) as load:
    load.describe("Load the mcutils_reborn standard library.")
    load.add_command(
        *tools.log("mcutils_reborn", "Load standard library..."),

        Comment("create the mcutils_reborn objective"),
        LiteralCommand("scoreboard objectives add %s dummy", STD_OBJECTIVE),

        FunctionCall(STD_LOAD_TAG),

        *tools.log("mcutils_reborn", "Loaded standard library!"),
    )

from .object import *
from .stack import *
