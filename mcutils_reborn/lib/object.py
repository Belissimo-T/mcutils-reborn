from .std import *
from ..commands import *

with std_namespace.create_namespace("object") as std_object:
    with std_object.create_class("object") as std_object_object:
        with std_object_object.create_function("__new__") as std_object_object_new:
            """Creates a new object."""
            std_object_object_new.add_command(
                LiteralCommand('summon minecraft:marker 0 0 0 {Tags:[""]}')
            )

        with std_object_object.create_function("__init__", args=("self", )) as std_object_object_init:
            """Initializes an object."""
            std_object_object_init.add_command(
                SayCommand("!! HIT __init__ STUB !!")
            )

    with std_object.create_function("fetch_object", args=("obj_id", )) as std_object_fetch_object:
        """Fetches an object by its ID."""
        std_object_fetch_object.add_command(
            SayCommand("!! HIT fetch_object STUB !!")
        )

