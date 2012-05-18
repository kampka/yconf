import os
import types
import yaml
import argparse

from yconf.util import NestedDict


class _Loader(yaml.Loader):

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

    def construct_mapping(self, node, deep=False):
        mapping = yaml.Loader.construct_mapping(self, node, deep)
        for key in mapping.keys():
            if type(key) in types.StringTypes:
                new = key.replace("-", "_")
                if new != key:
                    mapping[new] = mapping[key]
                    del mapping[key]
        return mapping


PRODUCTION  = 10
STAGING     = 20
DEVELOPMENT = 30

_environmentNames = {
    PRODUCTION      : "production",
    STAGING         : "staging",
    DEVELOPMENT     : "development",
    "production"    : PRODUCTION,
    "staging"       : STAGING,
    "development"   : DEVELOPMENT
    }


class BaseConfiguration(NestedDict):

    _environments = ("production", "staging", "development")

    def __init__(self, merge=True):

        NestedDict.__init__(self, {})

        self.merge = merge

        self.configPath = None
        self.environment = "production"
        self.parser = self.makeParser()

    def getEnvironment(self, environment):
        if isinstance(environment, int):
            return environment
        elif str(environment) == environment:
            if environment not in _environmentNames:
                raise ValueError("Unknown environment: %s", environment)
            return _environmentNames[environment]
        else:
            raise TypeError("Environment value is not an integer or a valid string: %r" % environment)

    def makeParser(self):
        self._configParser = argparse.ArgumentParser(add_help=False)
        self._configParser.add_argument("-c", "--config", dest="configPath",
                                        help="Configuration file or directory containing the configuration files.")
        self._configParser.add_argument("-e", "--environment", default="production",
                                        choices=("production", "staging", "development"),
                                        help="The environment used for configuration. (default: production)")

        parser = argparse.ArgumentParser(parents=[self._configParser])
        return parser

    def parse(self, args):

        args, remaining_argv = self._configParser.parse_known_args(args=args, namespace=self)
        if self.configPath:
            self.loadConfig()
        self.parser.parse_args(remaining_argv, self)

    def loadConfig(self):
        d = {}

        path = os.path.abspath(self.configPath)
        if os.path.isfile(path):
            with open(path, "r") as f:
                d = yaml.load(f.read(), Loader=_Loader)
        elif os.path.isdir(self.configPath):
            for e in self._environments:
                if os.path.exists(os.path.join(path, "%s.yml" % e)):
                    with open(os.path.join(path, "%s.yml" % e), "r") as f:
                        d[e] = yaml.load(f.read(), Loader=_Loader)
        if self.merge:
            for e in self._environments:
                if e in d and self.getEnvironment(e) <= self.getEnvironment(self.environment):
                    self.update(d[e])
        else:
            self.update(d.get(self.environment, {}))


__all__ = ["BaseConfiguration"]
