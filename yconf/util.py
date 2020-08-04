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


class NestedDict(object):

    def __init__(self, dict={}):
        object.__setattr__(self, "parent", None)
        object.__setattr__(self, "data", {})
        self.update(dict)

    def __getitem__(self, key):
        rv = self.data[key]
        if type(rv) is type(self) and not rv.parent:
            object.__setattr__(rv, "parent", self)
            return rv
        return rv

    def __getattr__(self, key):
        keys = key.split(".")
        try:
            r = self[keys[0]]
            if not len(keys[1:]):
                return r
            if type(r) not in (dict, NestedDict):
                raise AttributeError("No attribute found for %s" % keys[1:])

            return getattr(r, ".".join(keys[1:]))
        except KeyError as e:
            raise AttributeError(e)

    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, IndexError):
            return default

    def __setattr__(self, key, value):
        self.update({key: value})

    def __setitem__(self, key, value):
        self.update({key: value})

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        self[key] = default
        return default

    def has(self, key):
        return key in self.data

    def __call__(self):
        return self.data

    def update(self, other):
        for (key, value) in other.items():
            value = NestedDict(value) if type(value) is dict else value

            if '.' in key:
                key, remainder = key.split('.', 1)
                value = NestedDict({remainder: value})
            if key in self.data and \
                type(self[key]) in (dict, NestedDict) and \
                    type(value) in (dict, NestedDict):
                self.data[key] = NestedDict(self[key])
                object.__setattr__(self.data[key], "parent", self)
                self.data[key].update(value)
            else:
                self.data[key] = value

    def lookup(self, path, default=None):
        b = self.data.copy()
        for i in path[:-1]:
            b = b.get(i, {})
        return b.get(path[-1], default)

    def __iter__(self):
        return self.data.__iter__()

    def items(self):
        return self.data.items()

    def delete(self, key):
        del self.data[key]

    def __delitem__(self, key):
        self.delete(key)

    def __delattr__(self, name):
        self.delete(name)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return "<NestedDict (%s)>" % repr(dict(self.items()))

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def has_key(self, key):
        return self.has(key)

    def __contains__(self, key):
        return self.has(key)


__all__ = ["NestedDict"]
