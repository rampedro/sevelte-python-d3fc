"""
🧩 Vizora Core Modules

This package contains the core modules that power Vizora's functionality.
Each module is designed to be modular, extensible, and human-friendly.
"""

# Make core components easily accessible
from .dashboard import VizoraDashboard, DashboardConfig
from .data_manager import DataManager
from .visualization_engine import VisualizationEngine, VisualizationType
from .utils import PortManager, PathHelper, setup_logging, check_system_requirements

__all__ = [
    "VizoraDashboard",
    "DashboardConfig", 
    "DataManager",
    "VisualizationEngine",
    "VisualizationType",
    "PortManager",
    "PathHelper",
    "setup_logging",
    "check_system_requirements"
]