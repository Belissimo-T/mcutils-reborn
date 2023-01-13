import abc
import typing

from .exceptions import CompilationError
from .generics import Generic
from .commands import UniqueString


class DataType:
    """Superclass of all data types."""


class ConcreteDataType(abc.ABC):
    """Represents one single data type and not a collection or superclass of them."""

    dtype: str


class AnyDataType(DataType):
    """Represents any data type."""


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


class Expression(Generic):
    """Something that has value. Assignments to expressions are invalid."""

    @property
    def dtype_obj(self) -> typing.Type[DataType]:
        # noinspection PyTypeChecker
        generic_args: tuple[typing.Type[DataType], ...] = self.__generic_args__

        if len(generic_args) == 1:
            return generic_args[0]

        if len(generic_args) == 0:
            return AnyDataType

        raise CompilationError(f"NbtVar has invalid dtype {generic_args!r}.")

    @property
    def dtype(self) -> str | None:
        try:
            dtype_obj = self.dtype_obj

            return getattr(dtype_obj, "dtype", None)
        except CompilationError:
            # no dtype set
            pass

    @property
    def dtype_name(self) -> str:
        return self.dtype_obj.__name__

    def is_datatype(self,
                    type_: typing.Type[DataType] | typing.Type[ConcreteDataType] |
                           tuple[typing.Type[DataType] | typing.Type[ConcreteDataType], ...]
                    ) -> bool:
        return issubclass(self.dtype_obj, type_)

    def to_tellraw(self,
                   curr_text_kwargs: dict[str, typing.Any]) -> tuple[list["Command"], list["tellraw.TextComponent"]]:
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError


# noinspection PyAbstractClass
class Variable(Expression):
    """Represents something that stores some sort of data somewhere."""


class ConstExpr(Expression):
    """An expression that holds a compile-time constant."""

    def __init__(self, value: str):
        self.value = value

    def to_tellraw(self,
                   curr_text_kwargs: dict[str, typing.Any]) -> tuple[list["Command"], list["tellraw.TextComponent"]]:
        return [], [tellraw.PlainText(self.value, **curr_text_kwargs)]

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.dtype_name}]({self.value!r})"


# this is temporary
class ConstInt(ConstExpr[WholeNumberType]):
    def __init__(self, value: int):
        super().__init__(str(value))


class ScoreboardVar(Variable[WholeNumberType]):
    def __init__(self, player: str | UniqueString, objective: str | UniqueString):
        self.player = player
        self.objective = objective

    def __repr__(self):
        return f"{self.player}@{self.objective}"

    def to_tellraw(self,
                   curr_text_kwargs: dict[str, typing.Any]) -> tuple[list["Command"], list["tellraw.TextComponent"]]:
        return [], [tellraw.ScoreboardValue(self, **curr_text_kwargs)]

    def __iter__(self):
        yield self.player
        yield self.objective


class NbtVar(Variable):
    _nbt_container_type_literal = typing.Literal["block", "entity", "storage"]

    def __init__(self,
                 nbt_container_type: _nbt_container_type_literal,
                 nbt_container_argument: str,
                 path: str = ""):
        self.nbt_container_type = nbt_container_type
        self.nbt_container_argument = nbt_container_argument
        self.path = path

    def to_tellraw(self,
                   curr_text_kwargs: dict[str, typing.Any]) -> tuple[list["Command"], list["tellraw.TextComponent"]]:

        return [], [tellraw.NBT(self.path, **{self.nbt_container_type: self.nbt_container_argument},
                                **curr_text_kwargs)]

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.dtype_name}]({self.nbt_container_type!r}, " \
               f"{self.nbt_container_argument!r}, {self.path!r})"


from .commands import Command
from . import tellraw
