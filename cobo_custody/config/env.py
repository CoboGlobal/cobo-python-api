from dataclasses import dataclass


@dataclass(frozen=True)
class Env:
    host: str
    coboPub: str
