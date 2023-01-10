import abc
import typing

from .exceptions import CompilationError
from .generics import Generic


class DataType:
    """Superclass of all data types."""


class ConcreteDataType(abc.ABC):
    """Represents one single data type and not a collection or superclass of them."""

    dtype: str


class NumberType(DataType):
    """A number. May be whole or floating point."""


class WholeNumberType(NumberType):
    """A whole number such as a byte, short, int or long."""


class ByteType(WholeNumberType, ConcreteDataType):
    dtype = "byte"


class ShortType(WholeNumberType, ConcreteDataType):
    dtype = "short"


class IntType(WholeNumberType, ConcreteDataType):
    dtype = "int"


class LongType(WholeNumberType, ConcreteDataType):
    dtype = "long"


class FloatingPointType(NumberType):
    """A floating point number."""


class DoubleType(FloatingPointType, ConcreteDataType):
    dtype = "double"


class FloatType(FloatingPointType, ConcreteDataType):
    dtype = "float"


class StringType(DataType, ConcreteDataType):
    dtype = "str"


T_concrete = typing.TypeVar("T_concrete", bound=ConcreteDataType)
T_item = typing.TypeVar("T_item", bound=ConcreteDataType)


class ListType(DataType, typing.Generic[T_item]):
    """A list of items that each have the same type."""


class CompoundType(DataType):
    """A compound type, i.e. a collection of named fields."""


class Expression(Generic[T_concrete]):
    """Something that has value. Assignments to expressions are invalid."""

    @property
    def dtype_obj(self) -> DataType:
        # noinspection PyTypeChecker
        generic_args: tuple[DataType, ...] = self.__generic_args__

        assert len(generic_args) == 1, CompilationError("NbtVar has no dtype.")

        return generic_args[0]

    @property
    def dtype(self) -> str | None:
        try:
            return self.dtype_obj.dtype
        except CompilationError:
            # no dtype set
            pass
        except AttributeError:
            # dtype is not a ConcreteDataType
            pass

    def is_datatype(self, type_: typing.Type[DataType]) -> bool:
        return isinstance(self.dtype_obj, type_)


class Variable(Expression[T_concrete]):
    """Represents something that stores some sort of data somewhere."""


class ConstExpr(Expression[T_concrete]):
    """An expression that holds a compile-time constant."""

    def __init__(self, value: str):
        self.value = value


# this is temporary
class ConstInt(ConstExpr[WholeNumberType]):
    def __init__(self, value: int):
        super().__init__(str(value))


class ScoreboardVar(Variable[WholeNumberType]):
    def __init__(self, objective: str, player: str):
        self.objective = objective
        self.player = player


class NbtVar(Variable[T_concrete]):
    _nbt_container_type_literal = typing.Literal["block", "entity", "storage"]

    def __init__(self,
                 nbt_container_type: _nbt_container_type_literal,
                 nbt_container_argument: str,
                 path: str = ""):
        self.nbt_container_type = nbt_container_type
        self.nbt_container_argument = nbt_container_argument
        self.path = path
