from argparse import ArgumentParser
from testtools import TestCase
from yconf.util import NestedDict


class ArgumentParserTest(TestCase):
    """
    Make sure NestedDict can be used as an argparse namespace properly.
    """

    def test_storeAction(self):

        parser = ArgumentParser()
        parser.add_argument("--test", dest="a.b")
        ns = parser.parse_args(["--test", "c"], namespace=NestedDict())

        self.assertEqual("c", ns.a.b)

    def test_default(self):
        parser = ArgumentParser()
        parser.add_argument("--test", dest="a.b", default="c", action='store')
        ns = parser.parse_args([], namespace=NestedDict())

        self.assertEqual("c", ns.a.b)

    def test_storeCons(self):
        # taken from argparse docs
        parser = ArgumentParser()
        parser.add_argument('integers', metavar='N', type=int, nargs='+')
        parser.add_argument('--sum', dest='a.b', action='store_const',
                           const=sum, default=max)
        ns = parser.parse_args(["1", "2", "3", "4", "--sum"], namespace=NestedDict())

        self.assertEqual(10, ns.a.b(ns.integers))


def test_suite():
    from unittest import TestLoader
    return TestLoader().loadTestsFromName(__name__)
