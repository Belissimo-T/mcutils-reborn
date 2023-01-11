from .exceptions import issue_warning, CompilationWarning
from .expressions import *
from .commands import *

"""
# Conversions:

ScoreboardVar -> ScoreboardVar
 * scoreboard players operation <ob2> <pl2> = <ob1> <pl1>
 * execute store result score <ob2> <pl2> run scoreboard players get <ob1> <pl1>

ScoreboardVar -> NbtVar[number]:
 * execute store result <nbt_container_type> <nbt_container_arg> <path> <dtype> <scale> 
       run scoreboard players get <ob1> <pl1>

Const[int] -> ScoreboardVar:
 * scoreboard players set <ob1> <pl1> <const>

Const[T] -> NbtVar[T]:
 * data modify <nbt_container_type> <nbt_container_arg> <path> set value <const>

NbtVar[number | str | list | compound] -> ScoreboardVar:
 * execute store result score <ob1> <pl1> run data get <nbt_container_type> <nbt_container_arg> <path> 
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


def score_to_score(src: ScoreboardVar, dst: ScoreboardVar) -> list[Command]:
    return [
        LiteralCommand(f"scoreboard players operation {dst.objective} {dst.player} = {src.objective} {src.player}"
                       )
    ]


def score_to_nbt(src: ScoreboardVar, dst: NbtVar[NumberType]) -> list[Command]:
    return [
        LiteralCommand(
            f"execute store result {dst.nbt_container_type} {dst.nbt_container_argument} {dst.path} {dst.dtype} 1 "
            f"run scoreboard players get {src.objective} {src.player}"
        )
    ]


def const_to_score(src: ConstExpr[WholeNumberType], dst: ScoreboardVar) -> list[Command]:
    return [
        LiteralCommand(f"scoreboard players set {dst.objective} {dst.player} {src.value}"
                       )
    ]


def const_to_nbt(src: ConstExpr[T_concrete], dst: NbtVar[T_concrete]) -> list[Command]:
    return [
        LiteralCommand(
            f"data modify {dst.nbt_container_type} {dst.nbt_container_argument} {dst.path} set value {src.value}"
        )
    ]


def nbt_to_score(src: NbtVar, dst: ScoreboardVar) -> list[Command]:
    return [
        LiteralCommand(
            f"execute store result score {dst.objective} {dst.player} run data get {src.nbt_container_type} "
            f"{src.nbt_container_argument} {src.path}"
        )
    ]


def nbt_to_same_nbt(src: NbtVar[T_concrete], dst: NbtVar[T_concrete]) -> list[Command]:
    return [
        LiteralCommand(
            f"data modify {dst.nbt_container_type} {dst.nbt_container_argument} {dst.path} "
            f"set from {src.nbt_container_type} {src.nbt_container_argument} {src.path}"
        )
    ]


def nbt_number_to_nbt_number(src: NbtVar[NumberType],
                             dst: NbtVar[NumberType]) -> list[Command]:
    return [
        LiteralCommand(
            f"execute store result {dst.nbt_container_type} {dst.nbt_container_argument} {dst.path} {dst.dtype} "
            f"0.00000001 run data get {src.nbt_container_type} {src.nbt_container_argument} {src.path} 100000000"
        )
    ]


def nbt_container_to_number(src: NbtVar[CompoundType | ListType | StringType],
                            dst: NbtVar[NumberType]) -> list[Command]:
    return [
        LiteralCommand(
            f"execute store result {dst.nbt_container_type} {dst.nbt_container_argument} {dst.path} {dst.dtype} 1 "
            f"run data get {src.nbt_container_type} {src.nbt_container_argument} {src.path} 1"
        )
    ]


def _var_to_var(src: Expression, dst: Variable) -> list[Command]:
    if isinstance(src, ScoreboardVar):
        if isinstance(dst, ScoreboardVar):
            return score_to_score(src, dst)

        if isinstance(dst, NbtVar):
            if not (dst.is_datatype(NumberType) or dst.is_datatype(AnyDataType)):
                raise CompilationError(
                    f"Cannot store ScoreboardVar of integer type in NbtVar of type {dst.dtype_name}.")

            if not dst.is_datatype(ConcreteDataType):
                raise CompilationError(f"Destination {dst!r} is not a concrete datatype.")

            return score_to_nbt(src, dst)

    if isinstance(src, ConstExpr):
        if isinstance(dst, ScoreboardVar):
            if not src.is_datatype(WholeNumberType):
                raise CompilationError(f"Only ConstExpr of WholeNumberType, not {src.dtype_name} can be stored in a "
                                       f"ScoreboardVar.")

            return const_to_score(src, dst)

        if isinstance(dst, NbtVar):
            if not (dst.is_datatype(AnyDataType) or (None is not src.dtype == dst.dtype)):
                raise CompilationError(f"Cannot store {src!r} in {dst!r}.")

            return const_to_nbt(src, dst)

    if isinstance(src, NbtVar):
        if isinstance(dst, ScoreboardVar):
            # no type guard needed, all types are valid
            return nbt_to_score(src, dst)

        if isinstance(dst, NbtVar):
            if dst.is_datatype(AnyDataType) or (None is not src.dtype == dst.dtype):
                return nbt_to_same_nbt(src, dst)

            if src.is_datatype(NumberType) and dst.is_datatype(NumberType):
                if not dst.is_datatype(ConcreteDataType):
                    raise CompilationError(f"Destination {dst!r} is not a concrete datatype.")

                if src.dtype is None and dst.dtype == "double":
                    issue_warning(CompilationWarning(
                        f"Set from {src.dtype_name} NbtVar to double NbtVar: Due currently unknown reasons, it is not "
                        f"possible to do type conversion from an unknown type to a double without rounding to a float. "
                        f"That means a (potential) double will be rounded to a float."
                        f"In case you want to actually fetch a nbt double into another nbt double, add type "
                        f"information to both NbtVars."
                    ))
                return nbt_number_to_nbt_number(src, dst)

            if src.is_datatype((CompoundType, ListType, StringType)) and dst.is_datatype(NumberType):
                if not dst.is_datatype(ConcreteDataType):
                    raise CompilationError(f"Destination {dst!r} is not a concrete datatype.")

                return nbt_container_to_number(src, dst)

            raise CompilationError(f"Cannot set {src.dtype_name} NbtVar to {dst.dtype_name} NbtVar.")

    raise CompilationError(f"Cannot set {src!r} to {dst!r}.")


def var_to_var(src: Expression, dst: Variable) -> list[Command]:
    return [
        Comment(f"Set {src!r} to {dst!r}"),
        *_var_to_var(src, dst),
    ]
