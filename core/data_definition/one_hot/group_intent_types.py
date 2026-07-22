"""Closed value types shared by One-hot group intents."""

from typing import Literal

SourceMode = Literal["static", "mapping_backed", "external"]
SelectorDisposition = Literal["remove", "detach", "block"]
