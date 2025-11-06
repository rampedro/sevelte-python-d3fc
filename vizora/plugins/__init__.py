"""
🧩 Vizora Plugin System

This module contains the plugin architecture that makes Vizora infinitely extensible.
Create custom data sources, visualizations, and processing pipelines with ease!
"""

from .base_plugin import (
    BasePlugin,
    PluginMetadata,
    DataSourcePlugin,
    VisualizationPlugin,
    ProcessingPlugin,
    PluginManager
)

__all__ = [
    "BasePlugin",
    "PluginMetadata",
    "DataSourcePlugin", 
    "VisualizationPlugin",
    "ProcessingPlugin",
    "PluginManager"
]