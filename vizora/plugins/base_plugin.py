"""
🧩 Vizora Plugin System - Extend the Impossible

The plugin system is where Vizora becomes truly limitless. Want to add 
support for a new data source? Custom visualization type? Integration 
with your favorite ML library? This is your gateway to infinite possibilities!

We've designed this to be incredibly developer-friendly - you can create
powerful plugins with just a few lines of code.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Type
import logging
from dataclasses import dataclass
import importlib
import sys
from pathlib import Path


@dataclass
class PluginMetadata:
    """
    📋 Metadata about a plugin.
    
    This helps users understand what a plugin does and how to use it.
    It's also used by the plugin manager for discovery and validation.
    """
    name: str
    version: str
    author: str
    description: str
    category: str  # data_source, visualization, processing, integration
    tags: List[str]
    dependencies: List[str]
    min_vizora_version: str = "1.0.0"
    homepage: Optional[str] = None
    license: str = "MIT"


class BasePlugin(ABC):
    """
    🧩 Base class for all Vizora plugins.
    
    This defines the interface that all plugins must implement. It's designed
    to be minimal but powerful - you only need to implement what you use!
    
    Example:
        >>> class MyAwesomePlugin(BasePlugin):
        ...     def get_metadata(self):
        ...         return PluginMetadata(
        ...             name="awesome-viz",
        ...             version="1.0.0", 
        ...             author="You!",
        ...             description="Creates awesome visualizations"
        ...         )
        ...     
        ...     def initialize(self, dashboard):
        ...         # Register your custom visualization
        ...         pass
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"vizora.plugin.{self.__class__.__name__}")
        self.is_initialized = False
        self._dashboard_reference = None
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Return metadata about this plugin.
        
        This is used for plugin discovery, validation, and user information.
        Make it descriptive and helpful!
        """
        pass
    
    def initialize(self, dashboard) -> None:
        """
        Initialize the plugin with a dashboard instance.
        
        This is called when the plugin is loaded. Use this to register
        custom visualization types, data processors, or any other setup.
        
        Args:
            dashboard: The VizoraDashboard instance
        """
        self._dashboard_reference = dashboard
        self.is_initialized = True
        self.logger.info(f"🔌 {self.get_metadata().name} plugin initialized")
    
    def cleanup(self) -> None:
        """
        Clean up plugin resources.
        
        Called when the dashboard is shutting down. Use this to close
        connections, save state, or clean up temporary files.
        """
        self.logger.info(f"🧹 {self.get_metadata().name} plugin cleaning up")
    
    @property
    def name(self) -> str:
        """Get the plugin name."""
        return self.get_metadata().name
    
    @property
    def dashboard(self):
        """Get reference to the dashboard (available after initialization)."""
        if not self.is_initialized:
            raise RuntimeError("Plugin not initialized - call initialize() first")
        return self._dashboard_reference


class DataSourcePlugin(BasePlugin):
    """
    📊 Base class for data source plugins.
    
    Want to load data from APIs, databases, or custom formats? 
    This is your starting point! Data source plugins can:
    - Connect to external APIs
    - Query databases
    - Parse custom file formats
    - Stream real-time data
    
    Example:
        >>> class PostgreSQLPlugin(DataSourcePlugin):
        ...     def load_data(self, connection_string, query):
        ...         # Connect to PostgreSQL and execute query
        ...         return data
    """
    
    @abstractmethod
    def load_data(self, **config) -> List[Dict[str, Any]]:
        """
        Load data from this data source.
        
        Args:
            **config: Configuration specific to this data source
            
        Returns:
            List of dictionaries representing the data
        """
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration for this data source.
        
        Override this to provide helpful error messages when configuration
        is incorrect. Better to catch issues early!
        """
        return True
    
    def get_schema(self, **config) -> Dict[str, str]:
        """
        Get the data schema from this source.
        
        Returns a dictionary mapping column names to data types.
        Helps with validation and automatic visualization suggestions.
        """
        return {}


class VisualizationPlugin(BasePlugin):
    """
    🎨 Base class for visualization plugins.
    
    Want to create custom chart types or integrate with specialized
    visualization libraries? This is your canvas! Visualization plugins can:
    - Create completely new chart types
    - Integrate with D3, Three.js, or other libraries
    - Add domain-specific visualizations
    - Enhance existing visualizations
    
    Example:
        >>> class NetworkGraphPlugin(VisualizationPlugin):
        ...     def create_visualization(self, data, config):
        ...         # Create a network graph visualization
        ...         return frontend_config
    """
    
    @abstractmethod
    def create_visualization(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a visualization with the given data and configuration.
        
        Args:
            data: The data to visualize
            config: Configuration for the visualization
            
        Returns:
            Frontend-compatible configuration dictionary
        """
        pass
    
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get the configuration schema for this visualization.
        
        Return a JSON schema describing the configuration options.
        This can be used to generate UIs or validate configurations.
        """
        return {}
    
    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate that data is compatible with this visualization.
        
        Override this to provide specific validation for your visualization type.
        """
        return len(data) > 0


class ProcessingPlugin(BasePlugin):
    """
    🔧 Base class for data processing plugins.
    
    Need to transform, clean, or analyze data before visualization?
    Processing plugins are perfect for:
    - Data cleaning and normalization
    - Statistical analysis
    - Machine learning integration
    - Custom aggregations
    
    Example:
        >>> class MLInsightsPlugin(ProcessingPlugin):
        ...     def process_data(self, data):
        ...         # Run ML analysis and add insights
        ...         return enhanced_data
    """
    
    @abstractmethod
    def process_data(self, data: List[Dict[str, Any]], **config) -> List[Dict[str, Any]]:
        """
        Process the input data and return the transformed result.
        
        Args:
            data: Input data to process
            **config: Processing configuration
            
        Returns:
            Processed data
        """
        pass
    
    def get_processing_info(self) -> Dict[str, Any]:
        """
        Get information about what this processor does.
        
        Useful for documentation and helping users understand
        what transformations are being applied.
        """
        return {
            "name": self.name,
            "description": self.get_metadata().description,
            "input_requirements": "Any tabular data",
            "output_format": "Enhanced tabular data"
        }


class PluginManager:
    """
    🎪 The plugin manager - orchestrating the plugin ecosystem.
    
    This class handles plugin discovery, loading, validation, and lifecycle
    management. It's like a stage manager for all your plugins!
    """
    
    def __init__(self):
        self.logger = logging.getLogger("vizora.plugins")
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_directories: List[Path] = []
        
        # Default plugin search paths
        self.add_plugin_directory(Path(__file__).parent)  # Built-in plugins
        self.add_plugin_directory(Path.cwd() / "plugins")  # User plugins
        
        self.logger.info("🎪 PluginManager initialized")
    
    def add_plugin_directory(self, directory: Path) -> None:
        """
        Add a directory to search for plugins.
        
        This allows users to organize plugins in different locations
        and makes it easy to distribute plugin collections.
        """
        if directory.exists() and directory.is_dir():
            self.plugin_directories.append(directory)
            self.logger.info(f"📁 Added plugin directory: {directory}")
    
    def discover_plugins(self) -> List[str]:
        """
        Discover all available plugins in the search directories.
        
        Returns a list of plugin names that can be loaded.
        This scans Python files and looks for plugin classes.
        """
        discovered = []
        
        for directory in self.plugin_directories:
            for py_file in directory.glob("*.py"):
                if py_file.name.startswith("_"):
                    continue  # Skip private files
                
                try:
                    plugin_name = py_file.stem
                    
                    # Try to import and find plugin classes
                    spec = importlib.util.spec_from_file_location(plugin_name, py_file)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Look for plugin classes
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and 
                                issubclass(attr, BasePlugin) and 
                                attr != BasePlugin):
                                discovered.append(f"{plugin_name}.{attr_name}")
                                
                except Exception as e:
                    self.logger.warning(f"⚠️ Error scanning {py_file}: {e}")
        
        self.logger.info(f"🔍 Discovered {len(discovered)} plugins")
        return discovered
    
    def load_plugin(self, plugin_path: str) -> BasePlugin:
        """
        Load a specific plugin by path.
        
        Args:
            plugin_path: Path in format "module.ClassName"
            
        Returns:
            The loaded plugin instance
            
        Raises:
            ImportError: If the plugin can't be loaded
            ValueError: If the plugin is invalid
        """
        try:
            module_name, class_name = plugin_path.rsplit(".", 1)
            
            # Import the module
            for directory in self.plugin_directories:
                module_file = directory / f"{module_name}.py"
                if module_file.exists():
                    spec = importlib.util.spec_from_file_location(module_name, module_file)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        break
            else:
                raise ImportError(f"Plugin module not found: {module_name}")
            
            # Get the plugin class
            plugin_class = getattr(module, class_name)
            if not issubclass(plugin_class, BasePlugin):
                raise ValueError(f"{class_name} is not a valid plugin class")
            
            # Create instance
            plugin = plugin_class()
            
            # Validate metadata
            metadata = plugin.get_metadata()
            if not isinstance(metadata, PluginMetadata):
                raise ValueError("Plugin must return valid PluginMetadata")
            
            # Store plugin
            self.plugins[metadata.name] = plugin
            
            self.logger.info(f"🔌 Loaded plugin: {metadata.name} v{metadata.version}")
            return plugin
            
        except Exception as e:
            self.logger.error(f"❌ Error loading plugin {plugin_path}: {e}")
            raise
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a loaded plugin by name."""
        return self.plugins.get(name)
    
    def list_plugins(self) -> Dict[str, PluginMetadata]:
        """Get metadata for all loaded plugins."""
        return {name: plugin.get_metadata() for name, plugin in self.plugins.items()}
    
    def unload_plugin(self, name: str) -> bool:
        """
        Unload a plugin and clean up its resources.
        
        Args:
            name: Name of the plugin to unload
            
        Returns:
            True if plugin was unloaded, False if not found
        """
        plugin = self.plugins.get(name)
        if not plugin:
            return False
        
        # Clean up the plugin
        try:
            plugin.cleanup()
        except Exception as e:
            self.logger.warning(f"⚠️ Error during plugin cleanup: {e}")
        
        # Remove from registry
        del self.plugins[name]
        self.logger.info(f"🗑️ Unloaded plugin: {name}")
        return True
    
    def initialize_all_plugins(self, dashboard) -> None:
        """
        Initialize all loaded plugins with the dashboard instance.
        
        This should be called after the dashboard is created but before
        it starts serving requests.
        """
        for plugin in self.plugins.values():
            try:
                plugin.initialize(dashboard)
            except Exception as e:
                self.logger.error(f"❌ Error initializing plugin {plugin.name}: {e}")
    
    def cleanup_all_plugins(self) -> None:
        """Clean up all plugins during shutdown."""
        for plugin in self.plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                self.logger.warning(f"⚠️ Error cleaning up plugin {plugin.name}: {e}")


# 🚀 Built-in Plugin Examples

class ExampleVisualizationPlugin(VisualizationPlugin):
    """
    🎨 Example visualization plugin to show how it's done.
    
    This creates a simple custom chart type as a demonstration.
    Real plugins would be much more sophisticated!
    """
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="example-viz",
            version="1.0.0",
            author="Vizora Team",
            description="Example visualization plugin for demonstration",
            category="visualization",
            tags=["example", "demo", "chart"]
        )
    
    def create_visualization(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a simple example visualization."""
        return {
            "type": "example_chart",
            "data": data,
            "config": config,
            "message": "This is an example visualization from a plugin!"
        }


class CSVDataSourcePlugin(DataSourcePlugin):
    """
    📊 Enhanced CSV data source plugin.
    
    This extends the basic CSV support with advanced features like
    custom parsing, data validation, and schema detection.
    """
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="enhanced-csv",
            version="1.0.0",
            author="Vizora Team", 
            description="Enhanced CSV data source with advanced parsing",
            category="data_source",
            tags=["csv", "file", "parser"]
        )
    
    def load_data(self, **config) -> List[Dict[str, Any]]:
        """Load CSV data with enhanced parsing."""
        file_path = config.get("file_path")
        if not file_path:
            raise ValueError("file_path is required")
        
        # This would implement enhanced CSV parsing
        # For now, just return a placeholder
        return [{"message": "Enhanced CSV data would be loaded here"}]

# TODO: Add plugin dependency management
# TODO: Add plugin versioning and updates
# TODO: Add plugin marketplace integration
# TODO: Add plugin sandboxing for security
# TODO: Add plugin performance monitoring