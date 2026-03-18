"""
Plugins — Memory Subpackage.
Re-exporta MemoryPlugin para que `from plugins.memory import MemoryPlugin` funcione.
"""
from plugins.memory.memory_plugin import MemoryPlugin

__all__ = ["MemoryPlugin"]
