import re
from datetime import datetime
from typing import List
import dateutil.parser
from logwatcher.level import LogLevel


class LogRecord(object):
    def __init__(self, message: str, level: str, file, time: datetime = None):
        self.file = file
        self.time = time
        self.level = level
        self.message = message


class Matcher(object):
    required_keys = ['ts', 'message', 'level']

    def __init__(self, pattern: str, defaults: dict=None, translate: dict=None):
        self.pattern = pattern
        self.defaults = {} if defaults is None else defaults
        self.translate = {} if translate is None else translate

    def match(self, line: str):
        matches = re.search(self.pattern, line, flags=0)
        if matches is not None:
            # TODO apply self.translate
            return self.__validate(dict(self.defaults, **matches.groupdict()))

    def __validate(self, data: dict) -> dict:
        diff = set(self.required_keys) - set(data)
        if len(diff):
            raise RuntimeError("Missing keys after match: " + ", ".join(diff))
        if data['level'] not in LogLevel.as_dict():
            raise ValueError("Invalid log level: " + data['level'])

        return data


class LineParser(object):
    def __init__(self, patterns: List[Matcher], whitelist=None):
        self.matchers = patterns
        self.whitelist = [] if whitelist is None else whitelist

    def parse(self, line: str, logfile: str):
        """

        :rtype: LogRecord|None
        """
        data = None
        for m in self.matchers:
            data = m.match(line)
            if data is not None:
                break

        if data is None:
            raise RuntimeError("Failed to parse line: " + line)

        message = data['message']
        if message in self.whitelist:
            return None

        return LogRecord(
            message=message,
            time=dateutil.parser.parse(data['ts']),
            file=logfile,
            level=data['level']
        )
