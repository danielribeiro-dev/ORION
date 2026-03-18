"""
Plugins — Web Subpackage.
Re-exporta WebPlugin para que `from plugins.web import WebPlugin` funcione.
"""
from plugins.web.web_plugin import WebPlugin

__all__ = ["WebPlugin"]
