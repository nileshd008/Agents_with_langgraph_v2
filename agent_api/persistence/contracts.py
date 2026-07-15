

from dataclasses import dataclass, field


@dataclass(frozen = True)
class CheckPointerConfig:
    kind : str
    connection_str : str


@dataclass(frozen = True)
class StoreConfig:
    kind : str
    connection_str : str


