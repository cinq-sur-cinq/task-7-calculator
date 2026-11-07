from src.calculator.__main__ import main


def test_session_keeps_the_last_successful_result(monkeypatch, capsys):
    lines = iter(["_", "2 + 3", "2 +", "", "_ * 4", "0/0", "_ + 1"])

    def read_line(prompt):
        try:
            return next(lines)
        except StopIteration:
            raise EOFError from None

    monkeypatch.setattr("builtins.input", read_line)
    main()

    assert capsys.readouterr().out.splitlines() == [
        "Error: no previous result",
        "5.0",
        "Error: expected a value before the end of the expression",
        "20.0",
        "nan",
        "nan",
        "",
    ]
