"""
🚀 Vizora - Interactive Data Visualization Platform

A cutting-edge Python framework that seamlessly combines FastAPI backends with 
modern Svelte frontends, featuring advanced 3D visualizations through DeckGL 
and MapLibre GL integration.

Key Features:
    🎯 Zero-config setup with intelligent port detection
    🌐 Real-time 3D geospatial visualizations 
    📊 Extensible plugin architecture for custom charts
    🔧 CLI tools for rapid project scaffolding
    💫 WebGL-accelerated rendering for smooth animations

Example:
    >>> from vizora import VizoraDashboard
    >>> dashboard = VizoraDashboard("My Analytics App")
    >>> dashboard.add_data_source("sales.csv")
    >>> dashboard.add_visualization("deckgl_overlay", center=[139.7672, 35.6812])
    >>> dashboard.run()

Author: Pedro Ramirez (@rampedro)
Version: 1.0.0
License: MIT
"""

from .core.dashboard import VizoraDashboard
from .core.data_manager import DataManager
from .core.visualization_engine import VisualizationEngine
from .plugins.base_plugin import BasePlugin
from .__version__ import __version__

# Make the main classes easily accessible
__all__ = [
    "VizoraDashboard",
    "DataManager", 
    "VisualizationEngine",
    "BasePlugin",
    "__version__"
]

# Package metadata
__author__ = "Pedro Ramirez"
__email__ = "pedro@vizora.dev"
__license__ = "MIT"
__url__ = "https://github.com/rampedro/vizora"

# 🎨 ASCII Art Banner for CLI
BANNER = """
██╗   ██╗██╗███████╗ ██████╗ ██████╗  █████╗ 
██║   ██║██║╚══███╔╝██╔═══██╗██╔══██╗██╔══██╗
██║   ██║██║  ███╔╝ ██║   ██║██████╔╝███████║
╚██╗ ██╔╝██║ ███╔╝  ██║   ██║██╔══██╗██╔══██║
 ╚████╔╝ ██║███████╗╚██████╔╝██║  ██║██║  ██║
  ╚═══╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
                                              
🚀 Interactive Data Visualization Platform
"""

def get_version() -> str:
    """
    Returns the current version of Vizora.
    
    This is a human-friendly way to check which version you're running,
    especially useful when debugging or when you want to make sure you're
    using the latest features.
    
    Returns:
        str: The semantic version string (e.g., "1.0.0")
    """
    return __version__

def show_banner() -> None:
    """
    Displays the beautiful Vizora banner.
    
    Because every great tool deserves a memorable first impression! 
    This shows our ASCII art logo along with version info.
    """
    print(BANNER)
    print(f"Version {__version__} | {__url__}")
    print("-" * 50)