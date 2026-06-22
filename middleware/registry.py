

from .tools import store_artifact


class MiddlewareRegistry:

    def __init__(self):
        self._builders = {
            'store_artifact': lambda: store_artifact()
        }

    def create(self, key:str):
        if key not in self._builders:
            raise KeyError(f'Unknown middleware key - {key}')
        return self._builders[key]()
        
    def create_many(self, keys: list[str]):
        return [self.create(k) for k in keys]