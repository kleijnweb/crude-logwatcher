import json
from unittest.mock import mock_open, patch

import pytest

from logwatcher.config import App, ConfigError
from logwatcher.output import ReportWriter, SlackReportWriter
from logwatcher.reader import LogReader


def test_will_fail_if_config_file_does_not_exist():
    with pytest.raises(FileNotFoundError):
        App(config_path="faux")


def test_can_load_json():
    data = {"some": "data"}
    with patch("builtins.open", mock_open(read_data=json.dumps(data))) as mock_file:
        app = App(config_path="faux")
        mock_file.assert_called_with("faux", 'r')
        assert app.config['some'] == 'data'


def test_will_fail_if_no_writers_configured():
    data = {
        'parser': {
            'matchers': {"x": {'pattern': '.*'}}
        },
        'reader': {
            'paths': []
        },
        'report': {
            'thresholds': {},
            'writers': {}
        }
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(data))):
        app = App(config_path="faux")

    with pytest.raises(ConfigError) as exec_info:
        app.get_reader()
    assert 'writer' in str(exec_info.value)


def test_will_fail_if_no_matchers_configured():
    data = {
        'parser': {},
        'reader': {
            'paths': [],
        },
        'report': {
            'thresholds': {},
            'writers': {}
        }
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(data))):
        app = App(config_path="faux")

    with pytest.raises(ConfigError) as exec_info:
        app.get_reader()
    assert 'matcher' in str(exec_info.value)


def test_can_create_minimal_reader():
    data = {
        'parser': {
            'matchers': {"x": {'pattern': '.*'}}
        },
        'reader': {
            'paths': [],
        },
        'report': {
            'thresholds': {},
            'writers': {
                'stdout': None
            }
        }
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(data))):
        reader = App(config_path="faux")

    reader = reader.get_reader()
    assert isinstance(reader, LogReader)


def test_can_create_stdout_writer():
    data = {
        'parser': {
            'matchers': {"x": {'pattern': '.*'}}
        },
        'reader': {
            'paths': []
        },
        'report': {
            'thresholds': {},
            'writers': {
                'stdout': None
            }
        }
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(data))):
        assert isinstance(App(config_path="faux").get_reader().buffer.writers[0], ReportWriter)


def test_will_fail_when_writer_misconfigured():
    data = {
        'parser': {
            'matchers': {"x": {'pattern': '.*'}}
        },
        'reader': {
            'paths': []
        },
        'report': {
            'thresholds': {},
            'writers': {
                'slack': None
            }
        }
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(data))):
        app = App(config_path="faux")
        with pytest.raises(ConfigError) as exec_info:
            app.get_reader()
        assert 'Misconfigured writer' in str(exec_info.value)


def test_can_create_slack_writer():
    data = {
        'parser': {
            'matchers': {"x": {'pattern': '.*'}}
        },
        'reader': {
            'paths': []
        },
        'report': {
            'thresholds': {},
            'writers': {
                'slack': {
                    'webhook_url': 'something',
                    'channel': 'something_else'
                }
            }
        }
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(data))):
        assert isinstance(App(config_path="faux").get_reader().buffer.writers[0], SlackReportWriter)
