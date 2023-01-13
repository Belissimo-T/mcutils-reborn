from mcutils_reborn import *

with Namespace("mcutils_test") as test_namespace:
    with test_namespace.create_function("stack_test") as test_function:
        test_function.c_call_function(
            std_stack_push(stack_nr=0)
        )

    with test_namespace.create_function("test_function2") as test_function2:
        test_function2.c_call_function(test_function)

dp = Datapack("test_datapack")
dp.add(test_namespace, std_namespace)
dp.export().save(overwrite=True)
