"""
Plugins — Chat Subpackage.
Re-exporta ChatPlugin para que `from plugins.chat import ChatPlugin` funcione.
"""
from plugins.chat.chat_plugin import ChatPlugin

__all__ = ["ChatPlugin"]
