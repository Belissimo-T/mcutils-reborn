import typing

from .commands import UniqueString
from .expressions import ScoreboardVar


class Condition:
    def __init__(self, *args: str | UniqueString):
        self.args = args

    def to_str(self) -> tuple[str, tuple[UniqueString]]:
        return (
            " ".join([("%s" if isinstance(arg, UniqueString) else arg) for arg in self.args]),

            tuple(arg for arg in self.args if isinstance(arg, UniqueString))
        )


class ScoreCondition(Condition):
    def __init__(self, expr1: ScoreboardVar, cmp: typing.Literal["=", "<", ">", "<=", ">="], expr2: ScoreboardVar):
        super().__init__("score", *expr1, cmp, *expr2)


class ScoreConditionMatches(Condition):
    def __init__(self, expr1: ScoreboardVar, value: str | UniqueString):
        super().__init__("score", *expr1, "matches", value)