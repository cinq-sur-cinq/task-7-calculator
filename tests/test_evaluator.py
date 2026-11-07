import math

import pytest

from calculator import evaluate


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2 + 3 * 4", 14.0),
        ("(2 + 3) * 4", 20.0),
        ("10 - 3 - 2", 5.0),
        ("24 / 3 / 2", 4.0),
        ("2 * 3^2 + 1", 19.0),
        ("2^3**2", 512.0),
        ("2**3^2", 512.0),
        ("-2^2", -4.0),
        ("(-2)^2", 4.0),
        ("2^-2^2", 0.0625),
        ("2*-3 - -1", -5.0),
        ("--2 + +3", 5.0),
        ("  .5 + 1.5e-1 + 1.\t", 1.65),
    ],
)
def test_arithmetic(expression, expected):
    assert evaluate(expression) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("inf", math.inf),
        ("+inf", math.inf),
        ("-inf", -math.inf),
        ("1 / 0", math.inf),
        ("1 / -0", -math.inf),
        ("-1 / 0", -math.inf),
        ("-1 / -0", math.inf),
        ("inf / -0", -math.inf),
        ("1 / inf", 0.0),
        ("3 + inf", math.inf),
        ("-inf * -2", math.inf),
        ("(-inf)^3", -math.inf),
        ("2^inf", math.inf),
        ("0^-inf", math.inf),
        ("(-0)^-3", -math.inf),
        ("(-2)^1025", -math.inf),
        ("nan^0", 1.0),
    ],
)
def test_infinities_and_zero(expression, expected):
    assert evaluate(expression) == expected


@pytest.mark.parametrize(
    "expression", ["nan", "nan + 2", "0 / 0", "nan / 0", "inf / inf", "inf - inf", "0 * inf"]
)
def test_nan(expression):
    assert math.isnan(evaluate(expression))


def test_negative_zero_is_preserved():
    assert math.copysign(1.0, evaluate("1 / -inf")) == -1.0


def test_previous_result():
    assert evaluate("_ * 2 + _", previous=4.0) == 12.0
    assert evaluate("_", previous=0.0) == 0.0
    assert math.isnan(evaluate("_", previous=math.nan))
    with pytest.raises(ValueError, match="no previous result"):
        evaluate("_")


@pytest.mark.parametrize(
    "expression", ["", "1 +", "(1 + 2", "1 + 2)", "()", "1 2", "2(3)", "2***3", "2$3", "1e+"]
)
def test_invalid_expression(expression):
    with pytest.raises(ValueError):
        evaluate(expression)


def test_nonreal_power():
    with pytest.raises(ValueError, match="no real result"):
        evaluate("(-2)^0.5")
