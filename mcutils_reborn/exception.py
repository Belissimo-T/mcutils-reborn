import sys
import traceback
import warnings


class CompilationError(Exception):
    """Exception raised when a compile error occurs."""


class CompilationWarning(Warning):
    def __init__(self, message: str, traceback_cutoff: int = 1):
        super().__init__(f"{message}")

        self.traceback_cutoff = traceback_cutoff


def issue_warning(warning: CompilationWarning):
    sys.stderr.write("".join(traceback.format_stack()[:-warning.traceback_cutoff]))
    warnings.warn(warning)
    sys.stderr.write("\n")
