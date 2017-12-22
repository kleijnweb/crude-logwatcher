import pytest

from logwatcher.parser import LineParser, Matcher


def test_will_fail_when_date_is_not_parseable():
    matcher = Matcher(pattern="(?P<level>[A-Z]+)\-(?P<ts>[0-9]+)\-(?P<message>.*)")
    parser = LineParser([matcher])
    with pytest.raises(ValueError) as exception_info:
        parser.parse("DEBUG-123456-fooooo", 'foo.log')
    assert 'out of range' in str(exception_info.value)
