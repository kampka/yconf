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
