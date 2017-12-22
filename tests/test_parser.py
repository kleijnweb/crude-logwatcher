import datetime

import pytest

from logwatcher.parser import LineParser, LogRecord, Matcher


def test_will_fail_when_missing_keys():
    with pytest.raises(RuntimeError) as exception_info:
        matcher = Matcher(pattern="foo")
        matcher.match("foo")
    assert 'level' in str(exception_info.value)
    assert 'ts' in str(exception_info.value)
    assert 'message' in str(exception_info.value)


def test_will_return_none_when_no_match():
    matcher = Matcher(pattern="bar")
    assert matcher.match("foo") is None


def test_can_match_line():
    matcher = Matcher(pattern="(?P<level>[A-Z]+)\-(?P<ts>[0-9]+)\-(?P<message>.*)")
    matches = matcher.match("DEBUG-123456-fooooo")
    assert isinstance(matches, dict)
    assert 'level' in matches
    assert 'ts' in matches
    assert 'message' in matches


def test_will_raise_value_error_on_invalid_loglevel():
    with pytest.raises(ValueError) as exception_info:
        matcher = Matcher(pattern="(?P<level>[A-Z]+)\-(?P<ts>[0-9]+)\-(?P<message>.*)")
        matcher.match("HELLO-123456-fooooo")
    assert 'HELLO' in str(exception_info.value)


def test_will_fail_when_line_does_not_match():
    with pytest.raises(RuntimeError) as exception_info:
        parser = LineParser([])
        parser.parse('foo', 'bar')
    assert 'foo' in str(exception_info.value)


def test_will_fail_when_date_is_not_parseable():
    matcher = Matcher(pattern="(?P<level>[A-Z]+)\-(?P<ts>[0-9]+)\-(?P<message>.*)")
    parser = LineParser([matcher])
    with pytest.raises(ValueError) as exception_info:
        parser.parse("DEBUG-123456-fooooo", 'foo.log')
    assert 'out of range' in str(exception_info.value)


def test_can_parse_line():
    matcher = Matcher(pattern="(?P<level>[A-Z]+)\-(?P<ts>.*)\-(?P<message>.*)")
    parser = LineParser([matcher])
    record = parser.parse("DEBUG-2017/12/01-fooooo", 'foo.log')
    assert isinstance(record, LogRecord)
    assert 'fooooo' == record.message
    assert isinstance(record.time, datetime.datetime)
    assert record.time.isoformat() == '2017-12-01T00:00:00'
    assert record.level == 'DEBUG'


def test_will_skip_message_in_whitelist():
    matcher = Matcher(pattern="(?P<level>[A-Z]+)\-(?P<ts>.*)\-(?P<message>.*)")
    parser = LineParser([matcher], whitelist="Don't match me")
    actual = parser.parse("DEBUG-2017/12/01-Don't match me", 'foo.log')
    assert actual is None
