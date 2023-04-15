from .exceptions import issue_warning, CompilationWarning
from .expressions import *
from .commands import *

"""
# Conversions:

ScoreboardVar -> ScoreboardVar
 * scoreboard players operation <pl2> <ob2> = <pl1> <ob1>
 * execute store result score <pl2> <ob2> run scoreboard players get <pl1> <ob1>

ScoreboardVar -> NbtVar[number]:
 * execute store result <nbt_container_type> <nbt_container_arg> <path> <dtype> <scale> 
       run scoreboard players get <pl1> <ob1>

Const[int] -> ScoreboardVar:
 * scoreboard players set <pl1> <ob1> <const>

Const[T] -> NbtVar[T]:
 * data modify <nbt_container_type> <nbt_container_arg> <path> set value <const>

NbtVar[number | str | list | compound] -> ScoreboardVar:
 * execute store result score <pl1> <ob1> run data get <nbt_container_type> <nbt_container_arg> <path> 
   - dtype int, float or double will round down
   - dtype str, list or compound will yield length

NbtVar[T] -> NbtVar[T]:
 * data modify <nbt_container_type1> <nbt_container_arg1> <path1> 
       set from <nbt_container_type2> <nbt_container_arg2> <path2>

NbtVar[number] -> NbtVar[number <= float]:
 - check again, that it doesn't work for doubles as target
 * execute store result <nbt_container_type2> <nbt_container_arg2> <path2> <dtype2> 0.00000001 
       run data get <nbt_container_type1> <nbt_container_arg1> <path1> 100000000

NbtVar[compound | list | str] -> NbtVar[number]:
 * execute store result <nbt_container_type2> <nbt_container_arg2> <path2> <dtype2> <scale>
       run data get <nbt_container_type1> <nbt_container_arg1> <path1> 1
 - stores length of compound, list or str

NbtVar[number] -> NbtVar[compound | list | str]:
 - not sensible / impossible

NbtVar[str] -> NbtVar[list[str]]:
 - very hard, but possible

NbtVar[list[str]] -> NbtVar[str]:
 - sadly impossible
"""


def score_to_score(src: ScoreboardVar, dst: ScoreboardVar) -> Command:
    if src == dst:
        return Comment("scores are equal")

    return LiteralCommand(f"scoreboard players operation %s %s = %s %s",
                          dst.player, dst.objective, src.player, src.objective)


def score_to_nbt(src: ScoreboardVar, dst: NbtVar[NumberType], scale: float = 1) -> Command:
    return LiteralCommand(
        f"execute store result {dst.nbt_container_type} %s {dst.path} {dst.dtype} {scale} "
        f"run scoreboard players get %s %s",

        dst.nbt_container_argument,
        src.player, src.objective
    )


def const_to_score(src: ConstExpr[WholeNumberType], dst: ScoreboardVar) -> Command:
    return LiteralCommand(f"scoreboard players set %s %s {src.value}", dst.player, dst.objective)


def const_to_nbt(src: ConstExpr[T_concrete], dst: NbtVar[T_concrete]) -> Command:
    return LiteralCommand(
        f"data modify {dst.nbt_container_type} %s {dst.path} set value {src.value}",
        dst.nbt_container_argument
    )


def nbt_to_score(src: NbtVar, dst: ScoreboardVar, scale: float = 1) -> Command:
    return LiteralCommand(
        f"execute store result score %s %s run data get {src.nbt_container_type} "
        f"%s {src.path} {scale}",

        dst.player, dst.objective,
        src.nbt_container_argument
    )


def nbt_to_same_nbt(src: NbtVar[T_concrete], dst: NbtVar[T_concrete]) -> Command:
    return LiteralCommand(
        f"data modify {dst.nbt_container_type} %s {dst.path} "
        f"set from {src.nbt_container_type} %s {src.path}",
        dst.nbt_container_argument,
        src.nbt_container_argument
    )


def nbt_number_to_nbt_number(src: NbtVar[NumberType],
                             dst: NbtVar[NumberType]) -> Command:
    return nbt_to_nbt_execute_store(src, dst, scale=10e10, scale2=10e-10)


def nbt_to_nbt_execute_store(src: NbtVar[CompoundType | ListType | StringType | NumberType],
                             dst: NbtVar[NumberType],
                             scale: float = 1,
                             scale2: float = 1) -> Command:
    return LiteralCommand(
        f"execute store result {dst.nbt_container_type} %s {dst.path} {dst.dtype} {scale2} "
        f"run data get {src.nbt_container_type} %s {src.path} {scale}",
        dst.nbt_container_argument,
        src.nbt_container_argument
    )


def var_to_var(src: Expression, dst: Variable, scale: float = 1) -> list[Command]:
    if isinstance(src, ScoreboardVar):
        if isinstance(dst, ScoreboardVar):
            assert scale == 1
            return [score_to_score(src, dst)]

        if isinstance(dst, NbtVar):
            if not (dst.is_datatype(NumberType) or dst.is_datatype(AnyDataType)):
                raise CompilationError(
                    f"Cannot store ScoreboardVar of integer type in NbtVar of type {dst.dtype_name}.")

            if not dst.is_datatype(ConcreteDataType):
                raise CompilationError(f"Destination {dst!r} is not a concrete datatype.")

            return [score_to_nbt(src, dst, scale)]

    if isinstance(src, ConstExpr):
        assert scale == 1
        if isinstance(dst, ScoreboardVar):
            if not src.is_datatype(WholeNumberType):
                raise CompilationError(f"Only ConstExpr of WholeNumberType, not {src.dtype_name} can be stored in a "
                                       f"ScoreboardVar.")

            return [const_to_score(src, dst)]

        if isinstance(dst, NbtVar):
            if not (dst.is_datatype(AnyDataType) or (None is not src.dtype == dst.dtype)):
                raise CompilationError(f"Cannot store {src!r} in {dst!r}.")

            return [const_to_nbt(src, dst)]

    if isinstance(src, NbtVar):
        if isinstance(dst, ScoreboardVar):
            # no type guard needed, all types are valid
            return [nbt_to_score(src, dst, scale)]

        if isinstance(dst, NbtVar):
            if src.is_datatype(AnyDataType) or dst.is_datatype(AnyDataType) or (None is not src.dtype == dst.dtype):
                if src.is_datatype(AnyDataType) and not dst.is_datatype(AnyDataType):
                    issue_warning(CompilationWarning(f"Assuming dtype of source {src!r} is the same as {dst!r}."))

                assert scale == 1
                return [nbt_to_same_nbt(src, dst)]

            if src.is_datatype(NumberType) and dst.is_datatype(NumberType):
                if not dst.is_datatype(ConcreteDataType):
                    raise CompilationError(f"Destination {dst!r} is not a concrete datatype.")

                if src.dtype is None and dst.dtype == "double":
                    # TODO:
                    #   it is possible to get the dtype of an nbt tag at runtime through
                    #   put the tag in a list, then
                    #   execute store success ... run data modify ... set value 1.0d
                    #   this will fail if the tag is not a double
                    issue_warning(CompilationWarning(
                        f"Set from {src.dtype_name} NbtVar to double NbtVar: It is not possible to do type conversion "
                        f"from an unknown dtype to a double without rounding to a float when using scoreboards as an "
                        f"intermediate. That means a (potential) double will be rounded to a float. "
                        f"In case you want to actually fetch a nbt double into another nbt double, add type "
                        f"information to both NbtVars."
                    ))
                assert scale == 1
                return [nbt_number_to_nbt_number(src, dst)]

            if src.is_datatype((CompoundType, ListType, StringType)) and dst.is_datatype(NumberType):
                if not dst.is_datatype(ConcreteDataType):
                    raise CompilationError(f"Destination {dst!r} is not a concrete datatype.")

                return [nbt_to_nbt_execute_store(src, dst, scale)]

            raise CompilationError(f"Cannot set {src.dtype_name} NbtVar to {dst.dtype_name} NbtVar.")

    raise CompilationError(f"Cannot set {src!r} to {dst!r}.")


def add_const_to_score(src: ScoreboardVar, increment: ConstExpr[NumberType], scale: float = 1) -> list[Command]:
    val = int(int(increment.value) * scale)

    if val < 0:
        return [
            LiteralCommand(f"scoreboard players remove %s %s {abs(val)}", src.player, src.objective)
        ]

    return [
        LiteralCommand(f"scoreboard players add %s %s {val}", src.player, src.objective)
    ]


def add_const(src: Variable[NumberType], increment: ConstExpr[NumberType]) -> list[Command]:
    if isinstance(src, ScoreboardVar):
        return add_const_to_score(src, increment)

    if isinstance(src, NbtVar):
        if not src.is_datatype((NumberType, AnyDataType)):
            raise CompilationError(f"Cannot add {increment!r} to non-NumberType {src!r}.")

        if src.is_datatype(ConcreteDataType):
            if src.dtype == "double":
                temp_tag = UniqueTag("add_const_to_double_temp")
                temp_sel = CompositeString("@e[tag=%s, limit=1]", temp_tag)

                return [
                    # 1. summon an entity
                    LiteralCommand('summon minecraft:marker 0 0 0 {Tags:["%s"]}', temp_tag),

                    # 2. set pos
                    LiteralCommand('data modify entity %s Pos[0] set from %s %s %s', temp_sel, *src),

                    # 3. tp by increment
                    LiteralCommand(f"execute as %s at @s run tp @s ~{increment.value} ~ ~", temp_sel),

                    # 4. read pos
                    *var_to_var(NbtVar[DoubleType]("entity", temp_sel, "Pos[0]"), src),

                    # 5. kill
                    LiteralCommand("kill %s", temp_sel)
                ]
            from .lib.std import STD_TEMP_OBJECTIVE

            temp_var = ScoreboardVar("add_const_to_nbt", STD_TEMP_OBJECTIVE)
            return [
                *var_to_var(src, temp_var, scale=10e10),
                *add_const_to_score(temp_var, increment, scale=10e10),
                *var_to_var(temp_var, src, scale=10e-10),
            ]

        raise CompilationError(f"Adding to an unknown-dtype NbtVar is not supported yet.")

    raise CompilationError(f"Cannot add {increment!r} to {src!r}.")


def score_score_op_in_place(src: ScoreboardVar,
                            operation: typing.Literal["%=", "*=", "+=", "-=", "/=", "<", "=", ">", "><"],
                            other: ScoreboardVar
                            ) -> list[Command]:
    return [
        LiteralCommand(f"scoreboard players operation %s %s %s %s %s", *src, operation, *other)
    ]


def score_expr_op_in_place(src: ScoreboardVar,
                           operation: typing.Literal["%=", "*=", "+=", "-=", "/=", "<", "=", ">", "><"],
                           other: Expression[NumberType]) -> list[Command]:
    from .lib.std import STD_TEMP_OBJECTIVE
    temp_var = ScoreboardVar("score_expr_op_in_place_temp", STD_TEMP_OBJECTIVE)

    return [
        *var_to_var(other, temp_var),
        *score_score_op_in_place(src, operation, temp_var)
    ]


def add_in_place(src: Variable[NumberType], increment: Expression[NumberType]) -> list[Command]:
    if isinstance(increment, ConstExpr):
        return add_const(src, increment)

    if isinstance(src, ScoreboardVar):
        if isinstance(increment, ScoreboardVar):
            return score_score_op_in_place(src, "+=", increment)

        if isinstance(increment, NbtVar):
            if not increment.is_datatype(WholeNumberType):
                raise CompilationError(f"Cannot add {increment!r} to {src!r}. Increment must be a whole number.")

            from .lib.std import STD_TEMP_OBJECTIVE

            temp_var = ScoreboardVar("add_in_place_temp", STD_TEMP_OBJECTIVE)
            return [
                *var_to_var(increment, temp_var),
                *score_score_op_in_place(src, "+=", temp_var)
            ]

    if isinstance(src, NbtVar):
        if isinstance(increment, ScoreboardVar):
            raise CompilationError(f"Cannot add {increment!r} to {src!r} yet.")

        if isinstance(increment, NbtVar):
            raise CompilationError(f"Cannot add {increment!r} to {src!r} yet.")

    raise CompilationError(f"Cannot add {increment!r} to {src!r}.")
