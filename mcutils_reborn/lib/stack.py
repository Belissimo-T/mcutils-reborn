from .std import *
from .. import *

with std_namespace.create_namespace("stack") as std_stack_namespace:
    STD_STACK_INDEX_OBJECTIVE = UniqueScoreboardObjective("stack_index", std_stack_namespace)
    STD_STACK_TAG = UniqueTag("stack", std_stack_namespace)

    with std_stack_namespace.create_function("load", tags={STD_LOAD_TAG}) as std_stack_load:
        std_stack_load.add_command(
            Comment("create the stack objective"),

            LiteralCommand("scoreboard objectives add %s dummy", STD_STACK_INDEX_OBJECTIVE),

            *tools.log("mcutils_reborn", " * Loaded stack library!"),
        )

    _STD_STACK_TAGS = {}


    def tag_of_stacknr(stacknr: int):
        if stacknr not in _STD_STACK_TAGS:
            _STD_STACK_TAGS[stacknr] = UniqueTag(f"stack{stacknr}", std_stack_namespace)

        return _STD_STACK_TAGS[stacknr]

    def stack_len_of_stacknr(stacknr: int):
        return ScoreboardVar(tag_of_stacknr(stacknr), STD_OBJECTIVE)


    def std_stack_peek_any_template(stack_nr: int) -> Function:
        out = Function(f"peek_any_{stack_nr}")

        out.add_command(
            SayCommand(f"!! HIT {out.name} STUB !!")
        )

        return out


    def std_stack_peek_template(stack_nr: int) -> Function:
        out = Function(f"peek_{stack_nr}")

        out.add_command(
            SayCommand(f"!! HIT {out.name} STUB !!")
        )

        return out


    def std_stack_push_template(stack_nr: int) -> Function:
        out = Function(f"push_{stack_nr}")

        out.c_call_function(std_object_object_new)

        out.add_command(
            Comment("add necessary tags"),
            LiteralCommand("tag %s add %s", STD_OBJ_RET_SEL, STD_STACK_TAG),
            LiteralCommand("tag %s add %s", STD_OBJ_RET_SEL, tag_of_stacknr(stack_nr)),

            Comment("increment the stack length"),
            LiteralCommand("scoreboard players add %s %s 1", *stack_len_of_stacknr(stack_nr)),

            Comment("set the stack index"),
            LiteralCommand("scoreboard players operation %s %s = %s %s",
                           STD_OBJ_RET_SEL, STD_STACK_INDEX_OBJECTIVE, *stack_len_of_stacknr(stack_nr)),
        )

        return out


    def std_stack_pop_template(stack_nr: int) -> Function:
        out = Function(f"pop_{stack_nr}")

        out.add_command(
            SayCommand(f"!! HIT {out.name} STUB !!")
        )

        return out


    std_stack_peek_any = std_stack_namespace.create_template("peek_any", std_stack_peek_any_template)
    std_stack_peek = std_stack_namespace.create_template("peek", std_stack_peek_template)
    std_stack_push = std_stack_namespace.create_template("push", std_stack_push_template)
    std_stack_pop = std_stack_namespace.create_template("pop", std_stack_pop_template)
