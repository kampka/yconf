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

import fixtures
from testtools import TestCase, ExpectedException
from testtools.matchers import LessThan, HasLength

from yconf.config import _Loader as Loader, BaseConfiguration


class BaseYamlFileFixture(fixtures.Fixture):

    default_config = {"production": {"a": "a", "b": "b", "c": "c", "e" : { "f": "g" }},
                      "staging": {"b": "B"},
                      "development": {"c": "C"}
    }

    def __init__(self, data=None):
        super(BaseYamlFileFixture, self).__init__()
        self.data = data or self.default_config

    def setUp(self):
        super(BaseYamlFileFixture, self).setUp()
        self.dir = self.useFixture(fixtures.TempDir())


class YamlFileFixture(BaseYamlFileFixture):

    def __init__(self, data=None, name="config.yml"):
        super(YamlFileFixture, self).__init__(data)
        self.name = name

    def setUp(self):
        super(YamlFileFixture, self).setUp()
        self.config = os.path.join(self.dir.path, self.name)
        with open(self.config, "w") as f:
            f.write(yaml.dump(self.data))


class YamlConfigDirFixture(BaseYamlFileFixture):

    def setUp(self):
        super(YamlConfigDirFixture, self).setUp()
        for key, value in self.data.items():
            with open(os.path.join(self.dir.path, "%s.yml" % key), "w") as f:
                f.write(yaml.dump(value))


class LoaderTest(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.data = {"testcase": {"test-level": 1}}

    def test_constructMapping(self):

        d = yaml.load(yaml.dump(self.data), Loader=Loader)

        self.assertTrue("test_level" in d["testcase"])
        self.assertEqual(d["testcase"]["test_level"],
                        self.data["testcase"]["test-level"])

    def test_throwOnMappingConflict(self):

        data = {"testcase": {"test-level": 1, "test_level": 2}}

        with ExpectedException(Exception, ".+'test_level'.+'test-level'.+"):
            yaml.load(yaml.dump(data), Loader=Loader)

class BaseConfigurationTest(TestCase):

    def test_getEnvironment(self):
        bc = BaseConfiguration()
        self.assertEqual(10, bc.getEnvironment(10))
        self.assertEqual(20, bc.getEnvironment(20))
        self.assertEqual(30, bc.getEnvironment(30))

        self.assertEqual(10, bc.getEnvironment("production"))
        self.assertEqual(20, bc.getEnvironment("staging"))
        self.assertEqual(30, bc.getEnvironment("development"))

        self.assertThat(bc.getEnvironment("production"),
                        LessThan(bc.getEnvironment("staging")))

        self.assertThat(bc.getEnvironment("staging"),
                        LessThan(bc.getEnvironment("development")))

    def test_mergeEnvironments(self):
        f = self.useFixture(YamlFileFixture())

        bc = BaseConfiguration()
        bc.parse(args=["-c", f.config])
        self.assertEqual("a", bc["a"])
        self.assertEqual("b", bc["b"])
        self.assertEqual("c", bc["c"])
        del bc

        bc = BaseConfiguration()
        bc.parse(args=["-c", f.config, "-e", "staging"])
        self.assertEqual("a", bc["a"])
        self.assertEqual("B", bc["b"])
        self.assertEqual("c", bc["c"])
        del bc

        bc = BaseConfiguration()
        bc.parse(args=["-c", f.config, "-e", "development"])
        self.assertEqual("a", bc["a"])
        self.assertEqual("B", bc["b"])
        self.assertEqual("C", bc["c"])
        del bc

    def test_noMergeEnvironments(self):
        f = self.useFixture(YamlFileFixture())

        bc = BaseConfiguration(merge=False)
        bc.parse(args=["-c", f.config])
        self.assertEqual("a", bc["a"])
        self.assertEqual("b", bc["b"])
        self.assertEqual("c", bc["c"])
        del bc

        bc = BaseConfiguration(merge=False)
        bc.parse(args=["-c", f.config, "-e", "staging"])
        self.assertFalse(bc.has("a"))
        self.assertEqual("B", bc["b"])
        self.assertFalse(bc.has("c"))
        del bc

        bc = BaseConfiguration(merge=False)
        bc.parse(args=["-c", f.config, "-e", "development"])
        self.assertFalse(bc.has("a"))
        self.assertFalse(bc.has("b"))
        self.assertEqual("C", bc["c"])

    def test_configDirectory(self):
        f = self.useFixture(YamlConfigDirFixture())

        bc = BaseConfiguration()
        bc.parse(args=["-c", f.dir.path])
        self.assertEqual("a", bc["a"])
        self.assertEqual("b", bc["b"])
        self.assertEqual("c", bc["c"])
        del bc

        bc = BaseConfiguration()
        bc.parse(args=["-c", f.dir.path, "-e", "staging"])
        self.assertEqual("a", bc["a"])
        self.assertEqual("B", bc["b"])
        self.assertEqual("c", bc["c"])
        del bc

        bc = BaseConfiguration()
        bc.parse(args=["-c", f.dir.path, "-e", "development"])
        self.assertEqual("a", bc["a"])
        self.assertEqual("B", bc["b"])
        self.assertEqual("C", bc["c"])

    def test_parse(self):

        class TestConfiguration(BaseConfiguration):

            def makeParser(_self):
                parser = super(TestConfiguration, _self).makeParser()
                parser.add_argument("-a", dest="a")
                parser.add_argument("-x", dest="x")
                return parser

        f = self.useFixture(YamlFileFixture())

        bc = TestConfiguration()
        bc.parse(args=["-c", f.config, "-e", "development", "-a", "1", "-x", "2"])
        self.assertEqual("1", bc["a"])
        self.assertEqual("B", bc["b"])
        self.assertEqual("C", bc["c"])
        self.assertEqual("2", bc["x"])

    def test_parse_default_args(self):

        class TestConfiguration(BaseConfiguration):

            def makeParser(_self):
                parser = super(TestConfiguration, _self).makeParser()
                parser.add_argument("-a", dest="a")
                parser.add_argument("-b", dest="b")
                parser.add_argument("-x", dest="x")
                return parser

        f = self.useFixture(YamlFileFixture())
        bc = TestConfiguration()
        bc.parse(args=["-c", f.config, "-e", "development", "-a", "1"])

        with ExpectedException(KeyError):
            bc["x"]

        self.assertEqual("1", bc["a"])
        self.assertEqual("B", bc["b"])

    def test_parseWithoutConfig(self):
        class TestConfiguration(BaseConfiguration):

            def makeParser(_self):
                parser = super(TestConfiguration, _self).makeParser()
                parser.add_argument("-a", dest="a")
                parser.add_argument("-x", dest="x")
                return parser

        bc = TestConfiguration()
        bc.parse(args=["-a", "1", "-x", "2"])
        self.assertEqual("1", bc["a"])
        self.assertEqual("2", bc["x"])

    def test_config_before_defaults(self):
        """
        In cases where an argument is unfulfilled but defaulted in the arg parser,
        the config file should take precedence over parser defaults.
        """
        f = self.useFixture(YamlConfigDirFixture())

        class TestConfiguration(BaseConfiguration):

            def makeParser(_self):
                parser = super(TestConfiguration, _self).makeParser()
                parser.add_argument("-a", dest="e.f", default="x")
                parser.add_argument("-b", dest="a", default="b")
                parser.add_argument("-x", dest="c.c", default="c")
                parser.add_argument("-y", dest="x", default="y")


                return parser

        bc = TestConfiguration()
        bc.parse(args=["-c", f.dir.path])
        self.assertEqual("a", bc.a)
        self.assertEqual("g", bc.e.f)
        self.assertEqual("c", bc.c.c)
        self.assertEqual("y", bc.x)

    def test_config_merge_args(self):

        class TestConfiguration(BaseConfiguration):

            def makeParser(_self):
                parser = super(TestConfiguration, _self).makeParser()
                parser.add_argument("-a", dest="a.a", default="a")
                parser.add_argument("-b", dest="a.b", default="b")

                return parser

        bc = TestConfiguration()
        bc.parse(args = [])
        self.assertEqual("a", bc.a.a)
        self.assertEqual("b", bc.a.b)


def test_suite():
    from unittest import TestLoader
    return TestLoader().loadTestsFromName(__name__)
