from mcutils_reborn import *

with Namespace("mcutils_test") as test_namespace:
    with test_namespace.create_function("stack_test") as stack_test:
        for i in range(5):
            stack_test.add_command(
                *tools.print_("push ", {"color": "gold"}, str(50 + i)),
                *tools.call_function(
                    std_stack_push(stack_nr=0),
                    arg=ConstInt(50 + i),
                )
            )

        for i in range(5):
            stack_test.add_command(
                *tools.call_function(
                    std_stack_pop(stack_nr=0),
                ),

                *tools.print_("pop ", {"color": "gold"}, STD_RET),
            )

    with test_namespace.create_function("nbt_test") as nbt_test:
        nbt_test.add_command(
            *tools.print_(" * player pos x + 0: ", {"color": "gold"}, NbtVar("entity", "@s", "Pos[0]")),

            *var_to_var(NbtVar("entity", "@s", "Pos[0]"), NbtVar("storage", "my:storage", "testtest")),
            *add_in_place(NbtVar[DoubleType]("storage", "my:storage", "testtest"), ConstInt(1)),

            *tools.print_(" * player pos x + 1: ", {"color": "gold"}, NbtVar("storage", "my:storage", "testtest")),
        )

    with test_namespace.create_function("return_test") as return_test:
        with return_test.create_function("add_one") as return_test_add_one:
            return_test_add_one.add_command(
                *var_to_var(STD_ARG, STD_RET),
                *add_in_place(STD_RET, ConstInt(1)),
            )

        return_test.add_command(
            *tools.call_function(
                return_test_add_one,
                arg=ConstInt(5),
            ),

            *tools.print_(" * 5 + 1: ", {"color": "gold"}, STD_RET),

            *var_to_var(STD_RET, STD_ARG),
        )

        with return_test.c_if(ScoreCondition(STD_RET, "=", STD_ARG)) as return_test_if:
            return_test_if.add_command(
                *tools.print_("STD RET == STD ARG"),
            )

            with return_test_if.c_if(ScoreConditionMatches(STD_RET, "6")) as return_test_if_if:
                return_test_if_if.add_command(
                    *tools.print_("STD RET == 6"),
                )

            return_test_if.add_command(
                *tools.print_("END if")
            )

        return_test.add_command(
            *tools.print_("END")
        )

    with test_namespace.create_function("early_return_test") as early_return_test:
        with early_return_test.create_function("func1") as early_return_test_func1:
            with early_return_test_func1.c_if(ScoreConditionMatches(STD_ARG, "1..")) as early_return_test_func1_if:
                early_return_test_func1_if.add_command(
                    *tools.log("test", "a >= 1")
                )
                # check if a % 2 == 0
                early_return_test_func1_if.add_command(
                    *conversion.score_expr_op_in_place(STD_ARG, "%=", ConstInt(2)),
                )
                with early_return_test_func1_if.c_if(ScoreConditionMatches(STD_ARG, "0")) as ert_func1_if_if:
                    ert_func1_if_if.add_command(
                        *tools.log("test", "a mod 2 == 0, early return (3)")
                    )
                    ert_func1_if_if.return_(ConstInt(3))

                early_return_test_func1_if.add_command(
                    *tools.log("test", "a mod 2 != 0, early return (5)")
                )
                early_return_test_func1_if.return_(ConstInt(5))

            early_return_test_func1.add_command(
                *tools.log("test", "a < 1, normal return (1)")
            )
            early_return_test_func1.return_(ConstInt(1))

        test_vals = -10, 1, 2, 3, 4

        for i in test_vals:
            early_return_test.add_command(
                *tools.call_function(
                    early_return_test_func1,
                    arg=ConstInt(i),
                ),
                *tools.print_("func1(", {"color": "gold"}, str(i), {"color": "white"}, ") = ", {"color": "gold"},
                              STD_RET),
            )

    with test_namespace.create_function("while_test") as while_test:
        while_test_i = while_test.get_unique_scoreboard_var("i")
        while_test.add_command(
            LiteralCommand("gamerule maxCommandChainLength 1000"),
            *var_to_var(ConstInt(0), while_test_i),
            *tools.print_("START1"),
        )

        with while_test.c_while(ScoreConditionMatches(while_test_i, "..5")) as while_test_while:
            while_test_while.add_command(
                *tools.print_("i: ", {"color": "gold"}, while_test_i),
                *add_in_place(while_test_i, ConstInt(1))
            )

        while_test.add_command(
            *tools.print_("END"),
            *var_to_var(ConstInt(0), while_test_i),
            *tools.print_("START2"),
        )

        with while_test.c_while(ScoreConditionMatches(while_test_i, "..5")) as while_test_while2:
            while_test_while2.add_command(
                *tools.print_("i: ", {"color": "gold"}, while_test_i),
            )

            with while_test_while2.c_if(ScoreConditionMatches(while_test_i, "3")) as while_test_while2_if:
                while_test_while2_if.add_command(
                    *tools.print_("i == 3"),
                )
                while_test_while2_if.return_()

            while_test_while2.add_command(
                *add_in_place(while_test_i, ConstInt(1))
            )

    with test_namespace.create_function("class_test") as class_test:
        with class_test.create_class("myclass", inherits_from=(std_object_object,)) as myclass:
            with myclass.create_function("__init__", args=("age",)) as myclass_test:
                myclass_test.add_command(
                    *tools.call_function(std_stack_pop(stack_nr=STD_ARGSTACK)),

                    *tools.print_("INIT: ", {"color": "gold"}, STD_RET),

                    *var_to_var(STD_RET, ObjectAttributeVar[IntType](STD_ARG, "age")),
                )

            with myclass.create_function("print_age") as myclass_print_age:
                myclass_print_age.add_command(
                    *var_to_var(ObjectAttributeVar[IntType](STD_ARG, "age"), STD_RET),
                    *tools.print_("Age: ", {"color": "gold"}, STD_RET),
                )

        temps = []
        for i in range(5):
            temp = test_namespace.get_unique_scoreboard_var("temp", objective=STD_TEMP_OBJECTIVE)
            class_test.add_command(
                *tools.create_object(myclass, args=(ConstInt(50 + i),), target=temp),
            )
            temps.append(temp)

        for temp in temps:
            class_test.add_command(
                *tools.call_function(myclass_print_age, arg=temp),
            )

dp = Datapack("test_datapack")
dp.add(test_namespace, std_namespace)
dp.export().save(overwrite=True)
