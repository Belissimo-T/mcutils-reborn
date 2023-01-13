from mcutils_reborn import *

with Namespace("mcutils_test") as test_namespace:
    with test_namespace.create_function("stack_test") as test_function:
        for i in range(5):
            test_function.add_command(
                *tools.print_("push ", {"color": "gold"}, str(50 + i)),
                *var_to_var(ConstInt(50 + i), STD_ARG),
            )

            test_function.c_call_function(
                std_stack_push(stack_nr=0)
            )

        for i in range(5):
            test_function.c_call_function(
                std_stack_pop(stack_nr=0),
            )
            test_function.add_command(
                *tools.print_("pop ", {"color": "gold"}, STD_RET),
            )

    with test_namespace.create_function("test_function2") as test_function2:
        test_function2.c_call_function(test_function)

dp = Datapack("test_datapack")
dp.add(test_namespace, std_namespace)
dp.export().save(overwrite=True)
