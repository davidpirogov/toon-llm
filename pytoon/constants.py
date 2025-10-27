from enum import StrEnum
from typing import Literal, TypeVar

# List markers
LIST_ITEM_MARKER: Literal["-"] = "-"
LIST_ITEM_PREFIX: Literal["- "] = "- "

# Structural characters
COMMA: Literal[","] = ","
COLON: Literal[":"] = ":"
SPACE: Literal[" "] = " "
PIPE: Literal["|"] = "|"


# Brackets and braces
OPEN_BRACKET: Literal["["] = "["
CLOSE_BRACKET: Literal["]"] = "]"
OPEN_BRACE: Literal["{"] = "{"
CLOSE_BRACE: Literal["}"] = "}"


# Literals
NULL_LITERAL: Literal["null"] = "null"
TRUE_LITERAL: Literal["true"] = "true"
FALSE_LITERAL: Literal["false"] = "false"


# Escape characters
BACKSLASH: Literal["\\"] = "\\"
DOUBLE_QUOTE: Literal['"'] = '"'
NEWLINE: Literal["\n"] = "\n"
CARRIAGE_RETURN: Literal["\r"] = "\r"
TAB: Literal["\t"] = "\t"


# Delimiters
class Delimiters(StrEnum):
    comma = ","
    tab = "\t"
    pipe = "|"


Delimiter = TypeVar("Delimiter", bound=Literal[",", "\t", "|"])

DEFAULT_DELIMITER: str = Delimiters.comma
