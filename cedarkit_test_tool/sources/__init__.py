"""
Data sources for downloading test data.
"""
from .base import DataSource
from .gfs import GfsWisSource, GfsMusicDirSource

__all__ = [
    "DataSource",
    "GfsWisSource",
    "GfsMusicDirSource",
]
