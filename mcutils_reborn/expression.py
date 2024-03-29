import abc
import typing

from .exception import CompilationError
from .generics import Generic
from . import tellraw


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
        dtype_obj = self.dtype_obj
        return getattr(dtype_obj, "dtype", None)

    @property
    def dtype_name(self) -> str:
        return self.dtype_obj.__name__

    def is_data_type(self,
                     *type_: typing.Type[DataType] | typing.Type[ConcreteDataType]
                     ) -> bool:
        return issubclass(self.dtype_obj, type_)

    def to_tellraw(self,
                   curr_text_kwargs: dict[str, typing.Any],
                   resolve: typing.Callable[["UniqueString | str"], str]
                   ) -> tuple[list[str], list["tellraw.TextComponent"]]:
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
                   curr_text_kwargs: dict[str, typing.Any],
                   unique_strings: dict["UniqueString", str]
                   ) -> tuple[list["str"], list["tellraw.TextComponent"]]:
        return [], [tellraw.PlainText(self.value, **curr_text_kwargs)]

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.dtype_name}]({self.value!r})"


class ConstInt(ConstExpr[WholeNumberType]):
    def __init__(self, value: int):
        super().__init__(str(value))


class ScoreboardVar(Variable[WholeNumberType]):
    def __init__(self, player: "str | UniqueString", objective: "str | UniqueString"):
        self.player = player
        self.objective = objective

    def __repr__(self):
        return f"{self.player}@{self.objective}"

    def to_tellraw(self,
                   curr_text_kwargs: dict[str, typing.Any],
                   resolve: typing.Callable[["UniqueString | str"], str]
                   ) -> tuple[list["str"], list["tellraw.TextComponent"]]:
        return [], [tellraw.ScoreboardValue(resolve(self.player), resolve(self.objective), **curr_text_kwargs)]

    def __eq__(self, other):
        return self.player == other.player and self.objective == other.objective

    def __iter__(self):
        yield self.player
        yield self.objective


class NbtVar(Variable):
    _nbt_container_type_literal = typing.Literal["block", "entity", "storage"]

    def __init__(self,
                 nbt_container_type: _nbt_container_type_literal,
                 nbt_container_argument: "str | UniqueString",
                 path: str = ""):
        self.nbt_container_type = nbt_container_type
        self.nbt_container_argument = nbt_container_argument
        self.path = path

    def to_tellraw(self,
                   curr_text_kwargs: dict[str, typing.Any],
                   resolve: typing.Callable[["UniqueString | str"], str]
                   ) -> tuple[list["str"], list["tellraw.TextComponent"]]:
        return [], [tellraw.NBT(self.path, **{self.nbt_container_type: resolve(self.nbt_container_argument)},
                                **curr_text_kwargs)]

    def __iter__(self):
        yield self.nbt_container_type
        yield self.nbt_container_argument
        yield self.path

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.dtype_name}]({self.nbt_container_type!r}, " \
               f"{self.nbt_container_argument!r}, {self.path!r})"


from .command import UniqueString
