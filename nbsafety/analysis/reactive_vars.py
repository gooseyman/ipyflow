# -*- coding: future_annotations -*-
import re
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, List, Optional, Tuple
    from nbsafety.tracing.safety_ast_rewriter import SafetyAstRewriter


class AugmentedSymbol(Enum):
    reactive = '$'
    blocking = '$:'

    @property
    def marker(self):
        return self.value

    @property
    def escaped_marker(self):
        return re.escape(self.marker)


AUGMENTED_SYM_REGEX_TEMPLATE = "".join(
    r"^(?:"
    r"   (?:"
    r"      (?!')"
    r"      (?!{q})"
    r"      (?!''')"
    r"      (?!{tq})"
    r"      {any}"
    r"   ) "
    r"   |  {q}[^{q}]*{q}"
    r"   |  '[^']*'"
    r"   |  '''(?:(?!'''){any})*'''"
    r"   |  {tq}(?:(?!{tq}){any})*{tq}"
    r" )*?"
    r" ({{marker}}(?:(?!\d)\w)\w*"
    r" )".format(
        q='"',
        tq='"""',
        any=r"[\S\s]",
    ).split()
)


REACTIVE_VAR_REGEX = re.compile(AUGMENTED_SYM_REGEX_TEMPLATE.format(marker=AugmentedSymbol.reactive.escaped_marker))


def extract_reactive_vars(s: str) -> List[str]:
    reactive_vars = []
    while True:
        m = REACTIVE_VAR_REGEX.match(s)
        if m is None:
            break
        reactive_vars.append(m.group(1))
        s = s[m.span()[1]:]
    return reactive_vars


def get_augmented_syms_and_positions(
    s: str, regex: Optional[re.Pattern] = None, offset: int = 1
) -> Tuple[str, List[int]]:
    portions = []
    positions = []
    regex = regex or REACTIVE_VAR_REGEX
    while True:
        m = regex.match(s)
        if m is None:
            portions.append(s)
            break
        start, end = m.span(1)
        positions.append(start)
        portions.append(s[:start])
        portions.append(s[start + offset:end])
        s = s[end:]
    return "".join(portions), positions


def replace_reactive_vars(s: str) -> str:
    return get_augmented_syms_and_positions(s)[0]


def replace_reactive_vars_lines(lines: List[str]) -> List[str]:
    return [replace_reactive_vars(line) for line in lines]


def make_tracking_augmented_sym_replacer(
    rewriter: SafetyAstRewriter, symbol_type: AugmentedSymbol
) -> Callable[[List[str]], List[str]]:
    regex = re.compile(AUGMENTED_SYM_REGEX_TEMPLATE.format(marker=symbol_type.escaped_marker))

    def _input_transformer(lines: List[str]) -> List[str]:
        transformed_lines = []
        for idx, line in enumerate(lines):
            line, positions = get_augmented_syms_and_positions(line, regex=regex, offset=len(symbol_type.marker))
            transformed_lines.append(line)
            for pos in positions:
                rewriter.register_reactive_var_position(symbol_type, idx + 1, pos)
        return transformed_lines
    return _input_transformer
