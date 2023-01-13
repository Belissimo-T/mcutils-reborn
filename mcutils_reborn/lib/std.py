from .. import *

std_namespace = Namespace("mcutils_reborn_std")
STD_OBJECTIVE = UniqueScoreboardObjective("mcutils_reborn", std_namespace)

STD_ARG = std_namespace.get_unique_scoreboard_var("arg")
STD_RET = std_namespace.get_unique_scoreboard_var("ret")

from . import object, stack
