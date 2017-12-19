from datetime import datetime

import requests

from logwatcher.level import LogLevel
from logwatcher.parser import LogRecord


class Report(object):
    def __init__(self, file: str, message: str, severity: str, count: int, last_occurrence: datetime):
        self.last_occurrence = last_occurrence
        self.message = message
        self.file = file
        self.count = count
        self.severity = severity


class ReportWriter(object):
    def write(self, report: Report):
        pass


class StdOutReportWriter(ReportWriter):
    def write(self, report: Report):
        print(report.__dict__)


class SlackReportWriter(ReportWriter):
    def __init__(self, webhook_url: str, channel: str):
        self.channel = channel
        self.webhook_url = webhook_url

    def write(self, report: Report):
        emoji = 'warning'
        username = 'Problem: ' + report.severity
        if report.severity == LogLevel.EMERGENCY:
            emoji = 'ambulance'
            username = 'Emergency: ' + report.severity

        text = '[' + report.last_occurrence.isoformat() + '] ' + report.message \
               + (' *encountered ' + str(report.count) + ' times*' if report.count > 1 else '')

        data = {
            'text': text,
            'username': username,
            'file': report.file,
            'channel': '#' + self.channel,
            'icon_emoji': ':' + emoji + ':'
        }

        requests.post(url=self.webhook_url, json=data)


class OutputBuffer(object):
    def __init__(self, writers: list, thresholds: dict):
        self.writers = writers
        self.buffers = {
            LogLevel.NOTICE: {},
            LogLevel.WARNING: {},
            LogLevel.ERROR: {},
            LogLevel.CRITICAL: {},
            LogLevel.EMERGENCY: {}
        }
        self.thresholds = thresholds

    def add(self, record: LogRecord):
        try:
            level = record.level
            message = record.message
            if self.buffers[level].get(message) is None:
                self.buffers[level][message] = []
                self.buffers[level][message].append(record)
        except KeyError:
            pass

    def flush(self):
        write_buffer = {}
        for level in self.buffers:
            lists = self.buffers[level]
            threshold = self.thresholds[level]
            for message in lists:
                records = lists[message]
                count = 0
                hour = None
                for record in records:
                    t = record.time
                    record_hour = str(t.day) + ' ' + str(t.hour)
                    count += 1
                    if hour is None or hour != record_hour:
                        if count >= threshold:
                            if write_buffer.get(message) is not None:
                                count += write_buffer.get(message).count
                            write_buffer[message] = Report(
                                severity=level,
                                message=message,
                                count=count,
                                file=record.file,
                                last_occurrence=t
                            )
                        hour = record_hour
                        count = 0
        for k in write_buffer:
            for writer in self.writers:
                report = write_buffer[k]
                # Escalate on higher count
                if (report.severity == LogLevel.ERROR or report.severity == LogLevel.CRITICAL) and report.count > 10:
                    report.severity = LogLevel.EMERGENCY

                writer.write(report)