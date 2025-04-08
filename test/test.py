
import pytest
from lexical_analyzer import cilly_lexer


def test_var():
    source = "var x = 10;"
    tokens = cilly_lexer(source)
    expected_tokens = [
        ['var', None, 1, 1],
        ['id', 'x', 1, 5],
        ['=', None, 1, 7],
        ['num', 10, 1, 9],
        [';', None, 1, 11]
    ]
    assert tokens == expected_tokens


def test_string():
    source = 'var s = "hello";'
    tokens = cilly_lexer(source)
    expected_tokens = [
        ['var', None, 1, 1],
        ['id', 's', 1, 5],
        ['=', None, 1, 7],
        ['str', 'hello', 1, 9],
        [';', None, 1, 16]
    ]
    assert tokens == expected_tokens


def test_comments():
    source = "# This is a comment\nvar x = 10;"
    tokens = cilly_lexer(source)
    expected_tokens = [
        ['var', None, 2, 1],
        ['id', 'x', 2, 5],
        ['=', None, 2, 7],
        ['num', 10, 2, 9],
        [';', None, 2, 11]
    ]
    assert tokens == expected_tokens


def test_operators():
    source = "1 + 2 - 3 * 4 / 5 ^ 6;"
    tokens = cilly_lexer(source)
    expected_tokens = [
        ['num', 1, 1, 1],
        ['+', None, 1, 3],
        ['num', 2, 1, 5],
        ['-', None, 1, 7],
        ['num', 3, 1, 9],
        ['*', None, 1, 11],
        ['num', 4, 1, 13],
        ['/', None, 1, 15],
        ['num', 5, 1, 17],
        ['^', None, 1, 19],
        ['num', 6, 1, 21],
        [';', None, 1, 22]
    ]
    assert tokens == expected_tokens


def test_keywords():
    source = "if (x > 0) { return true; } else { return false; }"
    tokens = cilly_lexer(source)
    expected_tokens = [
        ['if', None, 1, 1],
        ['(', None, 1, 4],
        ['id', 'x', 1, 5],
        ['>', None, 1, 7],
        ['num', 0, 1, 9],
        [')', None, 1, 10],
        ['{', None, 1, 12],
        ['return', None, 1, 14],
        ['id', 'true', 1, 21],
        [';', None, 1, 25],
        ['}', None, 1, 27],
        ['else', None, 1, 29],
        ['{', None, 1, 34],
        ['return', None, 1, 36],
        ['id', 'false', 1, 43],
        [';', None, 1, 48],
        ['}', None, 1, 50]
    ]
    assert tokens == expected_tokens


def test_identifiers():
    source = "var _x1 = 10; var y_z = 20;"
    tokens = cilly_lexer(source)
    expected_tokens = [
        ['var', None, 1, 1],
        ['id', '_x1', 1, 5],
        ['=', None, 1, 9],
        ['num', 10, 1, 11],
        [';', None, 1, 13],
        ['var', None, 1, 15],
        ['id', 'y_z', 1, 19],
        ['=', None, 1, 23],
        ['num', 20, 1, 25],
        [';', None, 1, 27]
    ]
    assert tokens == expected_tokens


def test_numbers():
    source = "var x = 3.14; var y = 0.5; var z = 10;"
    tokens = cilly_lexer(source)
    expected_tokens = [
        ['var', None, 1, 1],
        ['id', 'x', 1, 5],
        ['=', None, 1, 7],
        ['num', 3.14, 1, 9],
        [';', None, 1, 13],
        ['var', None, 1, 15],
        ['id', 'y', 1, 19],
        ['=', None, 1, 21],
        ['num', 0.5, 1, 23],
        [';', None, 1, 26],
        ['var', None, 1, 28],
        ['id', 'z', 1, 32],
        ['=', None, 1, 34],
        ['num', 10, 1, 36],
        [';', None, 1, 38]
    ]
    assert tokens == expected_tokens


def test_whitespace_and_newlines():
    source = "var\nx\t=\r10;"
    tokens = cilly_lexer(source)
    expected_tokens = [
        ['var', None, 1, 1],
        ['id', 'x', 2, 1],
        ['=', None, 2, 3],
        ['num', 10, 2, 5],
        [';', None, 2, 7]
    ]
    assert tokens == expected_tokens


def test_fun():
    source = "fun test(a, b) { return a + b; }"
    tokens = cilly_lexer(source)
    expected_tokens = [
        ['fun', None, 1, 1],
        ['id', 'test', 1, 5],
        ['(', None, 1, 9],
        ['id', 'a', 1, 10],
        [',', None, 1, 11],
        ['id', 'b', 1, 13],
        [')', None, 1, 14],
        ['{', None, 1, 16],
        ['return', None, 1, 18],
        ['id', 'a', 1, 25],
        ['+', None, 1, 27],
        ['id', 'b', 1, 29],
        [';', None, 1, 30],
        ['}', None, 1, 32]
    ]
    assert tokens == expected_tokens


def test_errors():
    source = "var x = \"unfinished string;"
    with pytest.raises(Exception) as excinfo:
        cilly_lexer(source)
    assert 'cilly lexer : 第1行第28列 : 期望", 实际eof' in str(excinfo.value)


if __name__ == "__main__":
    pytest.main()
