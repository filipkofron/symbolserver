
from typing import NamedTuple, Optional

class Symbol(NamedTuple):
  hash: str
  filename: str
  url: Optional[str]
  store_path: Optional[str]

class Source(NamedTuple):
  path: str
  stored: bool
  failures: int
