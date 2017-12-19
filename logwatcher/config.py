from typing import List, Dict
import yaml
from logwatcher.parser import LineParser, Matcher
from logwatcher.reader import LogReader
from logwatcher.output import SlackReportWriter, StdOutReportWriter, OutputBuffer


class ConfigError(RuntimeError):
    pass


class App(object):
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as stream:
            try:
                self.config = yaml.load(stream)
            except yaml.YAMLError as exc:
                raise ConfigError("Failed to load config") from exc

    def get_reader(self) -> LogReader:
        try:
            return LogReader(
                parser=LineParser(
                    self.__create_matchers(self.config['parser']['matchers']),
                    self.config['parser'].get('whitelist')
                ),
                buffer=OutputBuffer(
                    writers=self.__create_writers(self.config['report']['writers']),
                    thresholds=self.config['report']['thresholds']
                ),
                paths=self.config['reader']['paths']
            )
        except KeyError as error:
            raise ConfigError("Missing required config: {0}".format(error)) from error

    @staticmethod
    def __create_matchers(config: Dict[str, dict]) -> List[Matcher]:
        if len(config) == 0:
            raise ConfigError("Must configure at least one matcher")

        matchers = []
        for k in config:
            try:
                matcher = Matcher(**config[k])
            except TypeError as error:
                raise ConfigError("Misconfigured matcher: {0}".format(error)) from error
            matchers.append(matcher)

        return matchers

    @staticmethod
    def __create_writers(config: Dict[str, dict]) -> List[dict]:
        if len(config) == 0:
            raise ConfigError("Must configure at least one writer")

        factories = {
            'slack': lambda c: SlackReportWriter(c['webhook_url'], c['channel']),
            'stdout': lambda c: StdOutReportWriter()
        }
        writers = []
        for type in config:
            try:
                w = factories[type](config[type])
            except (KeyError, TypeError) as error:
                raise ConfigError("Misconfigured writer: {0}".format(error)) from error
            writers.append(w)

        return writers
