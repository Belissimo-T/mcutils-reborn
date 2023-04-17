from .exception import issue_warning, CompilationWarning
from .expression import *
from .command import *

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


def expr_to_score(src: Expression, dst: ScoreboardVar, scale: float = 1) -> list[Command]:
    if isinstance(src, ConstExpr):
        assert scale == 1
        return [const_to_score(src, dst)]

    if isinstance(src, ScoreboardVar):
        assert scale == 1
        return [score_to_score(src, dst)]

    if isinstance(src, NbtVar):
        return [nbt_to_score(src, dst, scale)]

    raise NotImplementedError(f"Cannot store {src!r} in ScoreboardVar.")


def nbt_to_nbt(src: NbtVar, dst: NbtVar, scale: float = 1) -> list[Command]:
    # For any conversion from one data type to the same data type:
    # if one of the data types is AnyDataType, we assume that the other one is the same
    if (src.is_data_type(AnyDataType) or dst.is_data_type(AnyDataType)
        # if the destination dtype is a supertype of the source dtype, we assume that they are the same, too
        # For example int -> Number = int -> int
        or dst.is_data_type(src.dtype_obj)
    ):
        # if both are AnyDataType, we assume that they are the same
        if src.is_data_type(AnyDataType) and not dst.is_data_type(AnyDataType):
            issue_warning(CompilationWarning(f"Assuming dtype of any-dtype source {src!r} is the same as any-dtype "
                                             f"destination {dst!r}."))

        if not dst.is_data_type(ConcreteDataType, AnyDataType):
            issue_warning(CompilationWarning(f"Assuming dtype of destination {dst!r} with non-concrete dtype is the "
                                             f"same as source {src!r}."))

        assert scale == 1
        return [nbt_to_same_nbt(src, dst)]

    # anything else requires a conversion to a *known* data type
    if not dst.is_data_type(ConcreteDataType):
        raise CompilationError(f"Destination {dst!r} is not a concrete datatype.")

    # Number to Number:
    if src.is_data_type(NumberType) and dst.is_data_type(NumberType):
        # check for non-concrete dtype -> double conversion, because that is hard to do and not yet implemented
        if dst.is_data_type(DoubleType) and not src.is_data_type(ConcreteDataType):
            # TODO:
            #   it is possible to get the dtype of an nbt tag at runtime through
            #   put the tag in a list, then
            #   execute store success ... run data modify ... set value 1.0d
            #   this will fail if the tag is not a double
            #   then, one can just do double->double
            issue_warning(CompilationWarning(
                f"Set from {src.dtype_name} NbtVar {src} to double NbtVar {dst}: It is not possible to do type "
                f"conversion from an unknown dtype to a double without rounding to a float when using scoreboards as "
                f"an intermediate. That means a (potential) double will be rounded to a float. "
                f"In case you want to actually fetch a nbt double into another nbt double, add type "
                f"information to both NbtVars."
            ))
        assert scale == 1
        return [nbt_number_to_nbt_number(src, dst)]

    # Counting items:
    if src.is_data_type(CompoundType, ListType, StringType) and dst.is_data_type(NumberType):
        return [nbt_to_nbt_execute_store(src, dst, scale)]

    raise CompilationError(f"Cannot set {src.dtype_name} NbtVar to {dst.dtype_name} NbtVar.")


def expr_to_nbt(src: Expression, dst: NbtVar, scale: float = 1) -> list[Command]:
    if isinstance(src, ConstExpr):
        assert scale == 1
        return [const_to_nbt(src, dst)]

    if isinstance(src, ScoreboardVar):
        return [score_to_nbt(src, dst, scale)]

    if isinstance(src, NbtVar):
        return nbt_to_nbt(src, dst, scale)

    raise NotImplementedError(f"Cannot store {src!r} in NbtVar.")


def var_to_var(src: Expression, dst: Variable, scale: float = 1) -> list[Command]:
    if isinstance(src, DerivedVar):
        if isinstance(dst, (NbtVar, ScoreboardVar)):
            return [
                *src.to_primitive_var(dst)
            ]

    if isinstance(dst, DerivedVar):
        if isinstance(src, (NbtVar, ScoreboardVar)):
            return [
                *dst.from_primitive_var(src)
            ]

    if isinstance(dst, ScoreboardVar):
        return expr_to_score(src, dst, scale)

    if isinstance(dst, NbtVar):
        return expr_to_nbt(src, dst, scale)

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
        if not src.is_data_type(NumberType, DataType):
            raise CompilationError(f"Cannot add {increment!r} to non-NumberType {src!r}.")

        if src.is_data_type(ConcreteDataType):
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
            if not increment.is_data_type(WholeNumberType):
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


from .derived_var import DerivedVar
