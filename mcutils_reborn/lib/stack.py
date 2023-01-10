from .std import *


with std_namespace.create_namespace("stack") as std_stack_namespace:



    std_stack_namespace.create_template("peek_any", std_stack_peek_any_template)
    std_stack_namespace.create_template("peek", std_stack_peek_template)
    std_stack_namespace.create_template("push", std_stack_push_template)
    std_stack_namespace.create_template("pop", std_stack_pop_template)
