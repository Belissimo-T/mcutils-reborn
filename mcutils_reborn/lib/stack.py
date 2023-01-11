from .std import *
from .. import Function

with std_namespace.create_namespace("stack") as std_stack_namespace:
    def std_stack_peek_any_template(stack_nr: int) -> Function:
        out = Function(f"peek_any_{stack_nr}")

        out.add_command(
            SayCommand(f"!! HIT {out.name} STUB !!")
        )

        return out


    def std_stack_peek_template(stack_nr: int) -> Function:
        out = Function(f"peek_{stack_nr}")

        out.add_command(
            SayCommand(f"!! HIT {out.name} STUB !!")
        )

        return out


    def std_stack_push_template(stack_nr: int) -> Function:
        out = Function(f"push_{stack_nr}")

        out.add_command(
            SayCommand(f"!! HIT {out.name} STUB !!")
        )

        return out


    def std_stack_pop_template(stack_nr: int) -> Function:
        out = Function(f"pop_{stack_nr}")

        out.add_command(
            SayCommand(f"!! HIT {out.name} STUB !!")
        )

        return out


    std_stack_peek_any = std_stack_namespace.create_template("peek_any", std_stack_peek_any_template)
    std_stack_peek = std_stack_namespace.create_template("peek", std_stack_peek_template)
    std_stack_push = std_stack_namespace.create_template("push", std_stack_push_template)
    std_stack_pop = std_stack_namespace.create_template("pop", std_stack_pop_template)
