import math
import operator
import re
from collections.abc import Iterator

_TOKEN = re.compile(
    r"\s+|(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?"
    r"|inf|nan|\*\*|[+*/^()_\-]"
)


def _divide(numerator: float, denominator: float) -> float:
    if denominator != 0.0:
        return numerator / denominator
    if numerator == 0.0 or math.isnan(numerator):
        return math.nan
    # Multiplying the operands would lose the sign if one is infinite.
    sign = math.copysign(1.0, numerator) * math.copysign(1.0, denominator)
    return math.copysign(math.inf, sign)


def _power(base: float, exponent: float) -> float:
    if base == 0.0 and exponent < 0.0:
        if exponent.is_integer() and exponent % 2.0 == 1.0:
            return math.copysign(math.inf, base)
        return math.inf

    try:
        return math.pow(base, exponent)
    except OverflowError:
        if base < 0.0 and exponent % 2.0 == 1.0:
            return -math.inf
        return math.inf
    except ValueError:
        raise ValueError("power has no real result") from None


_OPERATORS = {
    "+": (1, operator.add),
    "-": (1, operator.sub),
    "*": (2, operator.mul),
    "/": (2, _divide),
    "u+": (3, operator.pos),
    "u-": (3, operator.neg),
    "^": (4, _power),
    "**": (4, _power),
}


def _tokens(expression: str) -> Iterator[str]:
    position = 0
    while position < len(expression):
        match = _TOKEN.match(expression, position)
        if match is None:
            char = expression[position]
            raise ValueError(f"unexpected character {char!r} at column {position + 1}")
        token = match.group()
        if not token.isspace():
            yield token
        position = match.end()


def _apply(operators: list[str], values: list[float]) -> None:
    symbol = operators.pop()
    _, operation = _OPERATORS[symbol]
    right = values.pop()
    if symbol in ("u+", "u-"):
        values.append(operation(right))
    else:
        values.append(operation(values.pop(), right))


def evaluate(expression: str, previous: float | None = None) -> float:
    """Evaluate one line. The caller supplies the value of `_`, if there is one."""
    values: list[float] = []
    operators: list[str] = []
    expecting_value = True

    for token in _tokens(expression):
        if expecting_value:
            # A sign after a power operator belongs to its exponent, as in 2^-3.
            if token in ("+", "-"):
                operators.append("u" + token)
                continue
            if token == "(":
                operators.append(token)
                continue
            if token == ")" or token in _OPERATORS:
                raise ValueError(f"expected a value, got {token!r}")
            if token == "_":
                if previous is None:
                    raise ValueError("no previous result")
                values.append(float(previous))
            else:
                values.append(float(token))
            expecting_value = False
        elif token == ")":
            while operators and operators[-1] != "(":
                _apply(operators, values)
            if not operators:
                raise ValueError("unmatched ')'")
            operators.pop()
        elif token in _OPERATORS:
            priority = _OPERATORS[token][0]
            while operators and operators[-1] != "(":
                top = _OPERATORS[operators[-1]][0]
                # leave equal powers on the stack so they go right to left
                if top < priority or (top == priority and token in ("^", "**")):
                    break
                _apply(operators, values)
            operators.append(token)
            expecting_value = True
        else:
            raise ValueError(f"expected an operator, got {token!r}")

    if expecting_value:
        raise ValueError("expected a value before the end of the expression")
    while operators:
        if operators[-1] == "(":
            raise ValueError("missing ')'")
        _apply(operators, values)
    return values.pop()
