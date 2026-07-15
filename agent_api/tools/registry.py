

from tools.decorators import TOOLS_REGISTRY

class ToolRegistry:

    def __init__(self):
        self.tools = []

    def load(self):
        self.tools = TOOLS_REGISTRY[:]

    def all(self):
        return self.tools