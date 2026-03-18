"""
Plugins — Filesystem Subpackage.
Re-exporta FilesystemPlugin para que `from plugins.filesystem import FilesystemPlugin` funcione.
"""
from plugins.filesystem.fs_plugin import FilesystemPlugin

__all__ = ["FilesystemPlugin"]
