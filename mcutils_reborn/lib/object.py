from .std import *
from ..commands import *

with std_namespace.create_namespace("object") as std_object:
    with std_object.create_class("object") as std_object_object:
        with std_object_object.create_function("__new__") as std_object_object_new:
            """Create a new object."""
            std_object_object_new.add_command(
                LiteralCommand('summon minecraft:marker 0 0 0 {Tags:[""]}')
            )

        with std_object_object.create_function("__init__", args=("self",)) as std_object_object_init:
            """Initialize an object."""
            std_object_object_init.add_command(
                SayCommand("!! HIT __init__ STUB !!")
            )

    with std_object.create_function("fetch_object", args=("obj_id",)) as std_object_fetch_object:
        """Fetches an object by its ID."""
        std_object_fetch_object.add_command(
            SayCommand("!! HIT fetch_object STUB !!")
        )

    with std_object.create_namespace("garbage_collection") as std_object_garbage_collection:
        with std_object_garbage_collection.create_function("increment_reference_count", args=("obj_id",)) \
                as std_object_garbage_collection_increment_reference_count:
            """Increment the reference count of an object."""
            std_object_garbage_collection_increment_reference_count.add_command(
                SayCommand("!! HIT increment_reference_count STUB !!")
            )

        with std_object_garbage_collection.create_function("decrement_reference_count", args=("obj_id",)) \
                as std_object_garbage_collection_decrement_reference_count:
            """Decrement the reference count of an object."""
            std_object_garbage_collection_decrement_reference_count.add_command(
                SayCommand("!! HIT decrement_reference_count STUB !!")
            )

        with std_object_garbage_collection.create_function("garbage_collect") as std_object_garbage_collect:
            """Run the garbage collector."""
            std_object_garbage_collect.add_command(
                SayCommand("!! HIT garbage_collect STUB !!")
            )
