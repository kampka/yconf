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

from testtools import TestCase
from testtools.matchers import IsInstance, KeysEqual

from yconf.util import NestedDict


class ConfigEntryTest(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.data = {"a": {"b": {"c": "d"}, "e": "f"}}

    def nestedToDict(self, nested):
        if type(nested) not in (NestedDict, dict):
            self.fail("Unexprected type %s, expected NestedDict" % type(nested))

        result = {}
        for (key, value) in nested.items():
            if type(value) is NestedDict:
                result[key] = self.nestedToDict(value)
            else:
                result[key] = value
        return result

    def test_dictAccess(self):

        nd = NestedDict(self.data)

        self.assertThat(nd["a"], IsInstance(NestedDict))
        self.assertEqual(self.nestedToDict(nd["a"].data), self.data["a"])
        self.assertEqual(nd["a"]["e"], "f")
        self.assertEqual(nd["a"]["b"]["c"], "d")

    def test_attrAccess(self):
        nd = NestedDict(self.data)

        self.assertThat(nd.a, IsInstance(NestedDict))
        self.assertEqual(self.nestedToDict(nd.a.data), self.data["a"])
        self.assertEqual(nd.a.e, nd["a"]["e"])
        self.assertEqual(nd.a.b.c, "d")

    def test_setattr(self):
        nd = NestedDict()
        setattr(nd, "a.b.c", "d")

        self.assertEqual("d", nd.data["a"]["b"]["c"])

    def test_get(self):

        nd = NestedDict(self.data)

        self.assertThat(nd.get("a"), IsInstance(NestedDict))
        self.assertEqual(self.nestedToDict(nd.get("a").data), self.data["a"])
        self.assertEqual(nd.get("a").get("e"), nd["a"]["e"])
        self.assertEqual(nd.a.get("b").c, "d")

        self.assertIsNone(nd.get("x"), None)
        self.assertEqual(nd.get("x", "y"), "y")

    def test_has(self):

        nd = NestedDict(self.data)

        self.assertTrue(nd.has("a"))
        self.assertFalse(nd.has("b"))
        self.assertFalse(nd.has("parent"))

    def test_call(self):

        nd = NestedDict(self.data)

        self.assertEqual(self.data, self.nestedToDict(nd()))
        self.assertEqual(self.data["a"], self.nestedToDict(nd.a()))

    def test_update(self):

        nd = NestedDict({})
        nd.update(self.data)
        nd.update({"a": {"b": {"i": "j"}}})
        nd.update({"a": {"b": {"c": "x"}}})
        nd.update({"a": {"g": "h"}})

        self.assertTrue(nd.a.has("g"))
        self.assertTrue(nd.a.b.has("c"))
        self.assertEqual(nd.a.b.c, "x")
        self.assertTrue(nd.a.b.has("i"))
        self.assertEqual(nd.a.b.i, "j")
        self.assertEqual(nd.a.g, "h")
        self.assertEqual(nd.a.e, "f")

    def test_nested_update(self):

        nd = NestedDict({"a.b": "c"})

        self.assertEquals(nd.a.b, "c")
        nd.update({"a.b": {"d": "e"}})
        self.assertThat(nd.a.b, KeysEqual({"d": "e"}))

        nd.update({"a": "d"})
        self.assertEquals(nd.a, "d")

    def test_setdefault(self):

        nd = NestedDict()

        self.assertFalse(nd.get("a", None))
        self.assertEquals(nd.setdefault("a", "b"), "b")
        self.assertEquals(nd["a"], "b")
        self.assertEquals(nd.setdefault("a", "c"), "b")

        self.assertEquals(nd.setdefault("b.c", "d"), "d")
        self.assertEquals(nd.b.c, "d")

    def test_lookup(self):

        nd = NestedDict(self.data)

        self.assertEqual("d", nd.lookup(("a", "b", "c")))
        self.assertIsNone(None, nd.lookup(("a", "x", "y")))
        self.assertEqual(self.data["a"], self.nestedToDict(nd.lookup(["a"])))

    def test_items(self):

        nd = NestedDict(self.data)

        for k, v in nd.items():
            self.assertIn(k, self.data)
            self.assertEqual(self.data[k], self.nestedToDict(v))

    def test_parent(self):

        nd = NestedDict(self.data)
        self.assertEqual(nd, nd.a.parent)
        self.assertIsNone(nd.parent)

        nd.update({"parent": "foo"})
        self.assertIsNone(nd.parent)
        self.assertEqual("foo", nd.get("parent"))

    def test_in(self):

        nd = NestedDict(self.data)
        self.assertIn("a", nd)
        self.assertNotIn("g", nd)

    def test_delete(self):

        nd = NestedDict(self.data)

        self.assertIn("b", nd["a"])
        delattr(nd["a"], "b")
        self.assertNotIn("b", nd["a"])

        self.assertIn("e", nd["a"])
        del nd["a"]["e"]
        self.assertNotIn("e", nd["a"])

        self.assertIn("a", nd)
        nd.delete("a")
        self.assertNotIn("a", nd)

    def test_length(self):

        nd = NestedDict(self.data)

        self.assertEqual(len(nd), len(self.data))

    def test_repr(self):

        nd = NestedDict()

        self.assertEqual(repr(nd), "<NestedDict ({})>")

        nd.update(self.data)

        self.assertEqual(repr(nd), "<NestedDict (%s)>" % repr(nd.data))

    def test_keys(self):

        nd = NestedDict(self.data)
        keys = nd.keys()

        for key in keys:
            self.assertIn(key, self.data)

    def test_values(self):

        nd = NestedDict(self.data)

        self.assertEqual(list(self.data.values()), [self.nestedToDict(x) for x in nd.values()])

    def test_haskey(self):

        nd = NestedDict(self.data)

        for key in self.data.keys():
            self.assertTrue(nd.has_key(key))

    def test_contains(self):

        nd = NestedDict(self.data)

        for key in self.data.keys():
            self.assertTrue(key in nd)

    def test_mapping(self):

        nd = NestedDict(self.data)

        d = {}
        for key, value in self.data.items():
            d[key] = nd[key]

        self.assertEqual(dict(nd), dict(**nd))
        self.assertEqual(dict(nd), d)

    def test_hasattr(self):
        nd = NestedDict(self.data)

        self.assertTrue(hasattr(nd, "a"))
        self.assertTrue(hasattr(nd, "a.e"))
        self.assertTrue(hasattr(nd, "a.b.c"))
        self.assertFalse(hasattr(nd, "b"))
        self.assertFalse(hasattr(nd, "a.b.c.d"))

    def test_setitem(self):
        nd = NestedDict(self.data)

        nd['a'] = 'b'
        self.assertEqual(nd.a, 'b')

        nd['a.b.c'] = 'd'
        self.assertTrue(hasattr(nd, "a.b.c"))
        self.assertEqual(nd.a.b.c, 'd')

def test_suite():
    from unittest import TestLoader
    return TestLoader().loadTestsFromName(__name__)
