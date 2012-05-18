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
