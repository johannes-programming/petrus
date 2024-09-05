import tomllib

import tomli_w


class TOML:
    def __init__(self, *, text):
        self._data = tomllib.loads(text)

    def __delitem__(self, index):
        self.__setitem__(index, None)

    def __getitem__(self, index):
        keys = self._keys(index)
        ans = self.clone()._data
        for k in keys:
            try:
                ans = ans[k]
            except KeyError:
                return None
        return ans

    def __setitem__(self, index, value):
        keys = self._keys(index)
        ans = self._data
        while len(keys) > 1:
            if type(ans) is dict and type(keys[1]) is str:
                ans.setdefault(keys[0], {})
            ans = ans[keys.pop(0)]
        if value is None:
            del ans[keys[0]]
            return
        if len(keys) > 0:
            ans[keys[0]] = TOML._purge(value)
        elif type(value) is dict:
            self._data = TOML._purge_dict(value)
        else:
            raise TypeError(value)

    def __str__(self):
        return tomli_w.dumps(self._data)

    @staticmethod
    def _keys(index):
        if type(index) is str:
            return [index]
        else:
            return list(index)

    @staticmethod
    def _purge(value):
        if type(value) is dict:
            return TOML._purge_dict(value)
        if type(value) in (list, tuple):
            return TOML._purge_list(value)
        if type(value) in (bool, float, int, str):
            return value
        raise TypeError

    @staticmethod
    def _purge_dict(value):
        ans = dict()
        for k, v in value.items():
            if v is not None:
                ans[k] = v
        return ans

    @staticmethod
    def _purge_list(value):
        ans = list()
        for x in value:
            if x is not None:
                ans.append(x)
        return ans

    def clone(self):
        return type(self)(text=str(self))
