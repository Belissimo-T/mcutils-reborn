from .std import *
from ..commands import *

with std_namespace.create_namespace("object") as std_object:
    STD_OBJ_RET_TAG = UniqueTag("object_ret", std_object)
    STD_OBJ_RET_SEL = CompositeString("@e[tag=%s]", STD_OBJ_RET_TAG)
    STD_OBJ_ID_OBJECTIVE = UniqueScoreboardObjective("id", std_object)
    STD_OBJ_ID_COUNTER = std_object.get_unique_scoreboard_var("obj_id_counter")

    with std_object.create_function("load", tags={STD_LOAD_TAG}) as load:
        load.add_command(
            Comment("create the object id objective"),
            LiteralCommand("scoreboard objectives add %s dummy", STD_OBJ_ID_OBJECTIVE),
            *tools.log("mcutils_reborn", " * Loaded object library!"),
        )

    with std_object.create_class("object") as std_object_object:
        STD_OBJ_TAG = UniqueTag("object", std_object_object)
        _STD_OBJ_TEMP_TAG = UniqueTag("temp", std_object_object)


        def tag_remove_all(tag: UniqueTag | str) -> list[Command]:
            return [
                Comment("remove the temp tag from all entities"),
                LiteralCommand("tag @e remove %s", tag),
            ]


        with std_object_object.create_function("__new__") as std_object_object_new:
            std_object_object_new.describe(
                "Create a new object and return its object id."
            )

            std_object_object_new.add_command(
                *tag_remove_all(_STD_OBJ_TEMP_TAG),
                *tag_remove_all(STD_OBJ_RET_TAG),

                Comment("increment the object id counter"),
                LiteralCommand("# Selector is %s", STD_OBJ_RET_SEL),
                LiteralCommand('scoreboard players add %s %s 1', *STD_OBJ_ID_COUNTER),

                Comment("summon a marker with the temp tag"),
                LiteralCommand('summon minecraft:marker 0 0 0 {Tags:["%s", "%s", "%s"]}',
                               STD_OBJ_TAG, _STD_OBJ_TEMP_TAG, STD_OBJ_RET_TAG),

                Comment("set the object id of the marker"),
                LiteralCommand('scoreboard players operation @e[tag=%s] %s = %s %s',
                               _STD_OBJ_TEMP_TAG, STD_OBJ_ID_OBJECTIVE, *STD_OBJ_ID_COUNTER),
            )

            std_object_object_new.return_(STD_OBJ_ID_COUNTER)

        with std_object_object.create_function("__init__", args=("self",)) as std_object_object_init:
            std_object_object_init.describe(
                "Initialize an object. This function is supposed to be overridden."
            )

    with std_object.create_function("fetch_object", args=("obj_id",)) as std_object_fetch_object:
        std_object_fetch_object.describe(
            """Assign the object with the given id a tag."""
        )
        std_object_fetch_object.add_command(
            *tag_remove_all(STD_OBJ_RET_TAG),

            Comment("give the selected entity the tag"),
            LiteralCommand("execute as @e[tag=%s] if score @s %s = %s %s run tag @s add %s",
                           STD_OBJ_TAG, STD_OBJ_ID_OBJECTIVE, *STD_ARG, STD_OBJ_RET_TAG),
        )

    with std_object.create_namespace("garbage_collection") as std_object_garbage_collection:
        STD_OBJ_REF_COUNT_OBJECTIVE = UniqueScoreboardObjective("reference_count", std_object_garbage_collection)

        with std_object_garbage_collection.create_function("increment_reference_count", args=("obj_id",)) \
                as std_object_garbage_collection_increment_reference_count:
            std_object_garbage_collection_increment_reference_count.describe(
                "Increment the reference count of an object."
            )

            std_object_garbage_collection_increment_reference_count.add_command(
                SayCommand("!! HIT increment_reference_count STUB !!")
            )

        with std_object_garbage_collection.create_function("decrement_reference_count", args=("obj_id",)) \
                as std_object_garbage_collection_decrement_reference_count:
            std_object_garbage_collection_decrement_reference_count.describe(
                "Decrement the reference count of an object."
            )

            std_object_garbage_collection_decrement_reference_count.add_command(
                SayCommand("!! HIT decrement_reference_count STUB !!")
            )

        with std_object_garbage_collection.create_function("garbage_collect") as std_object_garbage_collect:
            std_object_garbage_collect.describe(
                "Run the garbage collector."
            )

            std_object_garbage_collect.add_command(
                SayCommand("!! HIT garbage_collect STUB !!")
            )
