"""
Memory — History Subpackage.
Re-exporta HistoryMemory para que `from memory.history import HistoryMemory` funcione.
"""
from memory.history.history import HistoryMemory

__all__ = ["HistoryMemory"]
