from .std import *
from .object import *
from ..expression import *
from .. import tellraw
from ..condition import *
from .. import conversion as conv

with std_namespace.create_namespace("debug") as std_debug:
    with std_debug.create_function("objdump") as std_debug_objdump:
        std_debug_objdump_obj_id = std_debug_objdump.get_unique_scoreboard_var("obj_id")
        std_debug_objdump.add_command(
            *tools.print_({"underlined": True}, "All objects:", {"underlined": False, "color": "gray"},
                          " (ID: data, tags)"),
            *conv.var_to_var(ConstInt(0), std_debug_objdump_obj_id),
        )

        with std_debug_objdump.c_while(ScoreCondition(std_debug_objdump_obj_id, "<", STD_OBJ_ID_COUNTER)) \
                as std_debug_objdump_loop:
            std_debug_objdump_loop.add_command(
                *tools.call_function(
                    std_object_fetch_object,
                    arg=std_debug_objdump_obj_id,
                )
            )

            std_debug_objdump_loop.add_command(
                *tools.print_(
                    {"color": "light_purple"}, std_debug_objdump_obj_id, ": ",
                    {"color": tellraw.UNSET}, NbtVar("entity", STD_OBJ_RET_SEL, path="data"),
                    {"color": "gray"}, " (", NbtVar("entity", STD_OBJ_RET_SEL, path="Tags"), ")"
                ),

                *conv.add_in_place(std_debug_objdump_obj_id, ConstInt(1))
            )
