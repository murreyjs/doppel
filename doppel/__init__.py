__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .scanner import DuplicateScanner
from .remover import InteractiveRemover
from .utils import format_size, get_file_hash

__all__ = [
    "DuplicateScanner",
    "InteractiveRemover",
    "format_size",
    "get_file_hash"
]