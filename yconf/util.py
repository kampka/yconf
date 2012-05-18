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

import types


class NestedDict(object):

    def __init__(self, dict={}):
        object.__setattr__(self, "parent", None)
        object.__setattr__(self, "data", {})
        self.update(dict)

    def __getitem__(self, key):
        rv = self.data[key]
        if type(rv) in (types.DictionaryType, types.DictType):
            rv = NestedDict(rv)
        if type(rv) is type(self) and not rv.parent:
            object.__setattr__(rv, "parent", self)
            return rv
        return rv

    def __getattr__(self, key):
        return self[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, IndexError):
            return default

    def __setattr__(self, key, value):
        r = d = {}
        keys = key.split(".")
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        self.update(r)

    def has(self, key):
        return key in self.data

    def __call__(self):
        return self.data

    def update(self, other):
        if type(other) in (types.DictType, NestedDict):
            for (key, value) in other.iteritems():
                if key in self.data and \
                   type(self[key]) in (types.DictType, NestedDict) and \
                   type(value) in (types.DictType, NestedDict):
                    self.data[key] = NestedDict(self[key])
                    object.__setattr__(self.data[key], "parent", self)
                    self.data[key].update(value)
                else:
                    self.data[key] = value
        else:
            self.data.update(other)

    def lookup(self, path, default=None):
        b = self.data.copy()
        for i in path[:-1]:
            b = b.get(i, {})
        return b.get(path[-1], default)

    def __iter__(self):
        return self.data.__iter__()

    def iteritems(self):
        return self.data.iteritems()

__all__ = ["NestedDict"]
