from .expression import *
from .command import *
from . import tellraw
from . import conversion as conv
from . import tools


# noinspection PyAbstractClass
class DerivedVar(Variable):
    def to_primitive_var(self, dst: NbtVar | ScoreboardVar) -> list["Command"]:
        raise NotImplementedError

    def from_primitive_var(self, src: NbtVar | ScoreboardVar) -> list["Command"]:
        raise NotImplementedError


class ObjectAttributeVar(DerivedVar):
    def __init__(self, obj: Expression[WholeNumberType], attribute: str | UniqueString):
        self.obj = obj
        self.attribute = attribute

    def to_tellraw(self,
                   curr_text_kwargs: dict[str, typing.Any],
                   resolve: typing.Callable[[UniqueString | str], str]
                   ) -> tuple[list[str], list["tellraw.TextComponent"]]:
        return [], [tellraw.PlainText(f"ObjAttr[UNIMPLEMENTED]", **curr_text_kwargs)]

    def to_primitive_var(self, dst: NbtVar | ScoreboardVar) -> list["Command"]:
        from .lib import std

        return [
            *tools.call_function(std.std_object_fetch_object, arg=self.obj),
            *conv.var_to_var(NbtVar[self.dtype_obj]("entity", std.STD_OBJ_RET_SEL, path=f"data.{self.attribute}"), dst)
        ]

    def from_primitive_var(self, src: NbtVar | ScoreboardVar) -> list["Command"]:
        from .lib import std

        return [
            *tools.call_function(std.std_object_fetch_object, arg=self.obj),
            *conv.var_to_var(src, NbtVar[self.dtype_obj]("entity", std.STD_OBJ_RET_SEL, path=f"data.{self.attribute}"))
        ]

    def __iter__(self):
        yield self.obj
        yield self.attribute

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.dtype_name}]({self.obj!r}, {self.attribute!r})"
