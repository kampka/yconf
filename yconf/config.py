# Copyright (c) 2012, Christian Kampka
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import yaml
import argparse

from yconf.util import NestedDict


class _Loader(yaml.SafeLoader):

    def __init__(self, *args, **kwargs):
        super(_Loader, self).__init__(*args, **kwargs)

    def construct_mapping(self, node, deep=False):
        result = dict()
        mapping = super(_Loader, self).construct_mapping(node, deep)
        for key, value in mapping.items():
            result[key] = value
            if type(key) == str and "-" in key:
                print(mapping)
                new = key.replace("-", "_")
                if new in mapping:
                    raise Exception("Key '%s' causes a mapping conflict with key '%s'." % (new, key))
                result[new] = value
        return result


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

        parser = argparse.ArgumentParser(parents=[self._configParser], argument_default=argparse.SUPPRESS)
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
