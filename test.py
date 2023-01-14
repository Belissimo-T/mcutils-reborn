from mcutils_reborn import *

with Namespace("mcutils_test") as test_namespace:
    with test_namespace.create_function("stack_test") as stack_test:
        for i in range(5):
            stack_test.add_command(
                *tools.print_("push ", {"color": "gold"}, str(50 + i)),
            )

            stack_test.c_call_function(
                std_stack_push(stack_nr=0),
                arg=ConstInt(50 + i),
            )

        for i in range(5):
            stack_test.c_call_function(
                std_stack_pop(stack_nr=0),
            )
            stack_test.add_command(
                *tools.print_("pop ", {"color": "gold"}, STD_RET),
            )

    with test_namespace.create_function("nbt_test") as nbt_test:
        nbt_test.add_command(
            *tools.print_(" * player pos x + 0: ", {"color": "gold"}, NbtVar("entity", "@s", "Pos[0]")),

            var_to_var(NbtVar("entity", "@s", "Pos[0]"), NbtVar("storage", "my:storage", "testtest")),
            *add_in_place(NbtVar[DoubleType]("storage", "my:storage", "testtest"), ConstInt(1)),

            *tools.print_(" * player pos x + 1: ", {"color": "gold"}, NbtVar("storage", "my:storage", "testtest")),
        )

    with test_namespace.create_function("test_function2") as test_function2:
        test_function2.c_call_function(stack_test)

dp = Datapack("test_datapack")
dp.add(test_namespace, std_namespace)
dp.export().save(overwrite=True)
