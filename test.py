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

    with test_namespace.create_function("return_test") as return_test:
        with return_test.create_function("add_one") as return_test_add_one:
            return_test_add_one.add_command(
                var_to_var(STD_ARG, STD_RET),
                *add_in_place(STD_RET, ConstInt(1)),
            )

        return_test.c_call_function(
            return_test_add_one,
            arg=ConstInt(5),
        )

        return_test.add_command(
            *tools.print_(" * 5 + 1: ", {"color": "gold"}, STD_RET),

            var_to_var(STD_RET, STD_ARG),
        )

        with return_test.c_if(ScoreCondition(STD_RET, "=", STD_ARG)) as return_test_if:
            return_test_if.add_command(
                *tools.print_("STD RET == STD ARG"),
            )

            with return_test_if.c_if(ScoreConditionMatches(STD_RET, "=", "6")) as return_test_if_if:
                return_test_if_if.add_command(
                    *tools.print_("STD RET == 6"),
                )

            return_test_if.add_command(
                *tools.print_("END if")
            )

        return_test.add_command(
            *tools.print_("END")
        )

    with test_namespace.create_function("test_function2") as test_function2:
        test_function2.c_call_function(stack_test)

dp = Datapack("test_datapack")
dp.add(test_namespace, std_namespace)
dp.export().save(overwrite=True)
