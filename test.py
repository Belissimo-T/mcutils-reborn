from mcutils_reborn import *
from mcutils_reborn.conversion import var_to_var
from mcutils_reborn.export import *
from mcutils_reborn.lib.std import std_namespace, stack

with Namespace("test_namespace") as test_namespace:
    with test_namespace.create_function("test_function") as test_function:
        test_function.add_command(LiteralCommand("say Hello, world!"))
        test_function.add_command(
            *var_to_var(ConstExpr("[1, 2]"), NbtVar("storage", "test", "path")),
            *var_to_var(NbtVar[ListType]("storage", "test", "path"),
                        NbtVar[IntType]("storage", "test", "path2")),
        )

        test_function.c_call_function(
            stack.std_stack_push(stack_nr=0)
        )

    with test_namespace.create_function("test_function2") as test_function2:
        test_function2.c_call_function(test_function)

dp = Datapack("test_datapack")
dp.add(test_namespace, std_namespace)
dp.export().save(overwrite=True)
