from .std import *
from .. import *

with std_namespace.create_namespace("stack") as std_stack_namespace:
    STD_STACK_INDEX_OBJECTIVE = UniqueScoreboardObjective("index", std_stack_namespace)
    STD_STACK_VALUE_OBJECTIVE = UniqueScoreboardObjective("value", std_stack_namespace)
    STD_STACK_TAG = UniqueTag("stack", std_stack_namespace)
    _STD_STACK_TEMP_TAG = UniqueTag("temp", std_stack_namespace)
    _STD_STACK_TEMP_SEL = CompositeString("@e[tag=%s]", _STD_STACK_TEMP_TAG)

    with std_stack_namespace.create_function("load", tags={STD_LOAD_TAG}) as std_stack_load:
        std_stack_load.add_command(
            Comment("create the stack objective"),
            LiteralCommand("scoreboard objectives add %s dummy", STD_STACK_INDEX_OBJECTIVE),
            LiteralCommand("scoreboard objectives add %s dummy", STD_STACK_VALUE_OBJECTIVE),

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
            *tag_remove_all(_STD_STACK_TEMP_TAG),

            Comment("select entity"),
            LiteralCommand("execute as @e[tag=%s] if score @s %s = %s %s run tag @s add %s",
                           tag_of_stacknr(stack_nr), STD_STACK_INDEX_OBJECTIVE, *stack_len_of_stacknr(stack_nr),
                           _STD_STACK_TEMP_TAG),

            *var_to_var(ScoreboardVar(_STD_STACK_TEMP_SEL, STD_STACK_VALUE_OBJECTIVE), STD_RET),
        )

        return out


    def std_stack_push_template(stack_nr: int) -> Function:
        out = Function(f"push_{stack_nr}")
        out.describe(
            "Push an item onto the stack."
        )

        out.add_command(
            *tag_remove_all(_STD_STACK_TEMP_TAG),

            Comment("summon the entity"),
            LiteralCommand('summon minecraft:marker 0 0 0 {Tags:["%s", "%s", "%s", "%s"]}',
                           tag_of_stacknr(stack_nr), STD_STACK_TAG, STD_TAG, _STD_STACK_TEMP_TAG),

            Comment("increment the stack length"),
            LiteralCommand("scoreboard players add %s %s 1", *stack_len_of_stacknr(stack_nr)),

            Comment("set the stack index"),
            LiteralCommand("scoreboard players operation %s %s = %s %s",
                           _STD_STACK_TEMP_SEL, STD_STACK_INDEX_OBJECTIVE, *stack_len_of_stacknr(stack_nr)),

            Comment("set value"),
            *var_to_var(STD_ARG, ScoreboardVar(_STD_STACK_TEMP_SEL, STD_STACK_VALUE_OBJECTIVE)),
        )

        return out


    def std_stack_pop_template(stack_nr: int) -> Function:
        out = Function(f"pop_{stack_nr}")
        out.describe(
            "Pop an item from the stack."
        )

        out.c_call_function(std_stack_peek(stack_nr=stack_nr))

        out.add_command(
            Comment("remove the entity"),
            LiteralCommand("kill %s", _STD_STACK_TEMP_SEL),

            Comment("decrement the stack length"),
            LiteralCommand("scoreboard players remove %s %s 1", *stack_len_of_stacknr(stack_nr)),
        )

        return out


    std_stack_peek_any = std_stack_namespace.create_template("peek_any", std_stack_peek_any_template)
    std_stack_peek = std_stack_namespace.create_template("peek", std_stack_peek_template)
    std_stack_push = std_stack_namespace.create_template("push", std_stack_push_template)
    std_stack_pop = std_stack_namespace.create_template("pop", std_stack_pop_template)
