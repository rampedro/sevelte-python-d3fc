"""
🎨 Vizora Visualization Engine - Where Data Becomes Art

The VisualizationEngine is the creative heart of Vizora. It takes your raw 
data and transforms it into stunning, interactive visualizations that tell 
compelling stories.

We've designed this to be incredibly flexible - you can create everything
from simple bar charts to complex 3D geospatial animations with just a 
few lines of code!
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum
import json
import logging
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


class VisualizationType(Enum):
    """
    📊 All the amazing visualization types Vizora supports.
    
    This enum makes it easy to discover what's possible and ensures
    type safety when creating visualizations.
    """
    # 📊 Basic Charts
    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    PIE = "pie"
    HISTOGRAM = "histogram"
    
    # 🗺️ Geospatial Visualizations
    MAP = "map"
    CHOROPLETH = "choropleth"
    HEATMAP = "heatmap"
    
    # 🌐 Advanced 3D Visualizations
    DECKGL_OVERLAY = "deckgl_overlay"
    ARC_LAYER = "arc_layer"
    SCATTERPLOT_LAYER = "scatterplot_layer"
    HEXAGON_LAYER = "hexagon_layer"
    
    # 📈 Financial Charts
    CANDLESTICK = "candlestick"
    VOLUME = "volume"
    OHLC = "ohlc"
    
    # 🎯 Custom (for plugins)
    CUSTOM = "custom"


@dataclass
class VisualizationConfig:
    """
    ⚙️ Configuration for a visualization.
    
    This is like a recipe that tells the engine exactly how to create
    your visualization. Every parameter is optional with sensible defaults!
    """
    # Core settings
    viz_type: VisualizationType
    data_source: str
    title: str = "Untitled Visualization"
    description: str = ""
    
    # Data mapping
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    color_column: Optional[str] = None
    size_column: Optional[str] = None
    
    # Styling
    width: int = 800
    height: int = 400
    color_scheme: str = "viridis"
    theme: str = "modern"
    
    # Interactivity
    interactive: bool = True
    zoom_enabled: bool = True
    pan_enabled: bool = True
    
    # Advanced options
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    # 🗺️ Geospatial specific
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None
    zoom_level: int = 10
    
    # 🎯 3D specific
    pitch: float = 0
    bearing: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.viz_type.value,
            "data_source": self.data_source,
            "title": self.title,
            "description": self.description,
            "x_column": self.x_column,
            "y_column": self.y_column,
            "color_column": self.color_column,
            "size_column": self.size_column,
            "width": self.width,
            "height": self.height,
            "color_scheme": self.color_scheme,
            "theme": self.theme,
            "interactive": self.interactive,
            "zoom_enabled": self.zoom_enabled,
            "pan_enabled": self.pan_enabled,
            "center_lat": self.center_lat,
            "center_lng": self.center_lng,
            "zoom_level": self.zoom_level,
            "pitch": self.pitch,
            "bearing": self.bearing,
            "custom_config": self.custom_config
        }


class BaseVisualization(ABC):
    """
    🎨 Base class for all visualizations.
    
    This defines the interface that all visualization types must implement.
    It's designed to be super flexible while maintaining consistency.
    """
    
    def __init__(self, config: VisualizationConfig):
        self.config = config
        self.logger = logging.getLogger(f"vizora.viz.{config.viz_type.value}")
    
    @abstractmethod
    def generate_frontend_config(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate the configuration that the frontend needs to render this visualization.
        
        This is where the magic happens - we take the high-level config and
        transform it into the specific parameters that the frontend library needs.
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate that the provided data is compatible with this visualization type.
        
        Better to catch issues early with helpful error messages than to have
        silent failures in the browser!
        """
        pass
    
    def get_required_columns(self) -> List[str]:
        """
        Return the columns required for this visualization.
        
        Helps with validation and user guidance.
        """
        required = []
        if self.config.x_column:
            required.append(self.config.x_column)
        if self.config.y_column:
            required.append(self.config.y_column)
        return required


class BarChartVisualization(BaseVisualization):
    """
    📊 Bar chart visualization - the classic data storyteller.
    
    Perfect for comparing categories, showing rankings, or displaying
    distributions. Simple but incredibly effective!
    """
    
    def generate_frontend_config(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate D3-compatible bar chart configuration."""
        return {
            "type": "bar",
            "data": data,
            "encoding": {
                "x": {"field": self.config.x_column, "type": "ordinal"},
                "y": {"field": self.config.y_column, "type": "quantitative"},
                "color": {"field": self.config.color_column} if self.config.color_column else None
            },
            "title": self.config.title,
            "width": self.config.width,
            "height": self.config.height,
            "theme": self.config.theme,
            "interactive": self.config.interactive
        }
    
    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """Validate data for bar chart."""
        if not data:
            raise ValueError("Data cannot be empty for bar chart")
        
        required_columns = self.get_required_columns()
        first_row = data[0]
        
        for col in required_columns:
            if col not in first_row:
                raise ValueError(f"Required column '{col}' not found in data")
        
        return True


class MapVisualization(BaseVisualization):
    """
    🗺️ Interactive map visualization - geography meets data.
    
    Perfect for location-based data, regional comparisons, or any time
    you need to show "where" along with "what" and "how much".
    """
    
    def generate_frontend_config(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate MapLibre GL compatible configuration."""
        return {
            "type": "map",
            "data": data,
            "center": [
                self.config.center_lng or 0,
                self.config.center_lat or 0
            ],
            "zoom": self.config.zoom_level,
            "pitch": self.config.pitch,
            "bearing": self.config.bearing,
            "title": self.config.title,
            "interactive": self.config.interactive,
            "layers": [
                {
                    "type": "circle",
                    "data": data,
                    "paint": {
                        "circle-radius": 8,
                        "circle-color": "#667eea",
                        "circle-stroke-color": "#ffffff",
                        "circle-stroke-width": 2
                    }
                }
            ]
        }
    
    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """Validate data for map visualization."""
        if not data:
            raise ValueError("Data cannot be empty for map")
        
        # Check for latitude/longitude columns
        first_row = data[0]
        lat_cols = ['lat', 'latitude', 'y']
        lng_cols = ['lng', 'longitude', 'lon', 'x']
        
        has_lat = any(col in first_row for col in lat_cols)
        has_lng = any(col in first_row for col in lng_cols)
        
        if not (has_lat and has_lng):
            raise ValueError("Map visualization requires latitude and longitude columns")
        
        return True


class DeckGLVisualization(BaseVisualization):
    """
    🌐 Advanced 3D DeckGL visualization - where data meets artistry.
    
    This is where Vizora really shines! Create stunning 3D visualizations
    with WebGL acceleration. Perfect for geospatial data, animations, and
    when you need to wow your audience.
    """
    
    def generate_frontend_config(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate DeckGL-compatible configuration."""
        
        # Default to Tokyo if no center specified
        center = [
            self.config.center_lng or 139.7672,
            self.config.center_lat or 35.6812
        ]
        
        config = {
            "type": "deckgl_overlay",
            "data": data,
            "mapStyle": "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
            "initialViewState": {
                "longitude": center[0],
                "latitude": center[1],
                "zoom": self.config.zoom_level,
                "pitch": self.config.pitch or 60,
                "bearing": self.config.bearing or -45
            },
            "title": self.config.title,
            "layers": []
        }
        
        # Add layers based on visualization type
        if self.config.viz_type == VisualizationType.ARC_LAYER:
            config["layers"].append({
                "type": "ArcLayer",
                "id": "arc-layer",
                "data": data,
                "getSourcePosition": "source",
                "getTargetPosition": "target",
                "getSourceColor": [0, 255, 100],
                "getTargetColor": [0, 190, 255],
                "getWidth": 5
            })
        
        elif self.config.viz_type == VisualizationType.SCATTERPLOT_LAYER:
            config["layers"].append({
                "type": "ScatterplotLayer",
                "id": "scatter-layer",
                "data": data,
                "getPosition": "position",
                "getRadius": 100,
                "getFillColor": [255, 140, 0]
            })
        
        # Add custom config overrides
        if self.config.custom_config:
            config.update(self.config.custom_config)
        
        return config
    
    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """Validate data for DeckGL visualization."""
        if not data:
            raise ValueError("Data cannot be empty for DeckGL visualization")
        
        # Validation depends on layer type
        first_row = data[0]
        
        if self.config.viz_type == VisualizationType.ARC_LAYER:
            required = ['source', 'target']
            for field in required:
                if field not in first_row:
                    raise ValueError(f"ArcLayer requires '{field}' field")
        
        return True


class VisualizationEngine:
    """
    🎨 The main visualization engine that orchestrates everything.
    
    This is like a master artist's studio - it has all the tools and 
    knowledge to create any kind of visualization you can imagine.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("vizora.engine")
        self.visualization_registry: Dict[VisualizationType, type] = {
            VisualizationType.BAR: BarChartVisualization,
            VisualizationType.MAP: MapVisualization,
            VisualizationType.DECKGL_OVERLAY: DeckGLVisualization,
            VisualizationType.ARC_LAYER: DeckGLVisualization,
            VisualizationType.SCATTERPLOT_LAYER: DeckGLVisualization,
        }
        
        self.logger.info("🎨 VisualizationEngine initialized with {} visualization types".format(
            len(self.visualization_registry)
        ))
    
    def create_visualization(self, config: VisualizationConfig, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a visualization with the specified configuration and data.
        
        This is the main entry point for creating visualizations. It handles
        validation, type checking, and generates the frontend configuration.
        
        Args:
            config: Visualization configuration
            data: The data to visualize
            
        Returns:
            Frontend-compatible configuration dictionary
        """
        self.logger.info(f"🎯 Creating {config.viz_type.value} visualization: {config.title}")
        
        # Get the appropriate visualization class
        viz_class = self.visualization_registry.get(config.viz_type)
        if not viz_class:
            raise ValueError(f"Unsupported visualization type: {config.viz_type}")
        
        # Create and validate
        visualization = viz_class(config)
        visualization.validate_data(data)
        
        # Generate frontend configuration
        frontend_config = visualization.generate_frontend_config(data)
        
        self.logger.info(f"✅ Generated configuration for {len(data)} data points")
        return frontend_config
    
    def register_visualization_type(self, viz_type: VisualizationType, viz_class: type) -> None:
        """
        Register a custom visualization type.
        
        This is how plugins can extend Vizora with completely new visualization
        types. Perfect for domain-specific charts or experimental visualizations!
        
        Args:
            viz_type: The visualization type enum value
            viz_class: Class that implements BaseVisualization
        """
        if not issubclass(viz_class, BaseVisualization):
            raise ValueError("Visualization class must inherit from BaseVisualization")
        
        self.visualization_registry[viz_type] = viz_class
        self.logger.info(f"🔌 Registered custom visualization type: {viz_type.value}")
    
    def get_supported_types(self) -> List[str]:
        """
        Get a list of all supported visualization types.
        
        Useful for building UIs or helping users discover what's possible.
        """
        return [viz_type.value for viz_type in self.visualization_registry.keys()]
    
    def get_type_info(self, viz_type: VisualizationType) -> Dict[str, Any]:
        """
        Get detailed information about a visualization type.
        
        This includes required data format, configuration options, and
        usage examples. Perfect for auto-generating documentation!
        """
        viz_class = self.visualization_registry.get(viz_type)
        if not viz_class:
            return {"error": f"Unknown visualization type: {viz_type}"}
        
        # Create a dummy instance to get info
        dummy_config = VisualizationConfig(viz_type=viz_type, data_source="dummy")
        dummy_viz = viz_class(dummy_config)
        
        return {
            "type": viz_type.value,
            "class": viz_class.__name__,
            "description": viz_class.__doc__ or "No description available",
            "required_columns": dummy_viz.get_required_columns(),
            "supports_3d": viz_type in [VisualizationType.DECKGL_OVERLAY, VisualizationType.ARC_LAYER],
            "category": self._get_category(viz_type)
        }
    
    def _get_category(self, viz_type: VisualizationType) -> str:
        """Categorize visualization types for better organization."""
        if viz_type in [VisualizationType.BAR, VisualizationType.LINE, VisualizationType.SCATTER, VisualizationType.PIE]:
            return "Basic Charts"
        elif viz_type in [VisualizationType.MAP, VisualizationType.CHOROPLETH, VisualizationType.HEATMAP]:
            return "Geospatial"
        elif viz_type in [VisualizationType.DECKGL_OVERLAY, VisualizationType.ARC_LAYER, VisualizationType.SCATTERPLOT_LAYER]:
            return "3D Visualizations"
        elif viz_type in [VisualizationType.CANDLESTICK, VisualizationType.VOLUME]:
            return "Financial"
        else:
            return "Other"

# 🔧 Extension Points for Advanced Users

class VisualizationPlugin(ABC):
    """
    🧩 Base class for visualization plugins.
    
    Want to create completely custom visualization types? This is your
    starting point! Perfect for:
    - Domain-specific charts (scientific, medical, etc.)
    - Integration with specialized libraries
    - Experimental visualization techniques
    - Custom interactive elements
    """
    
    @abstractmethod
    def get_visualization_type(self) -> VisualizationType:
        """Return the visualization type this plugin handles."""
        pass
    
    @abstractmethod
    def get_visualization_class(self) -> type:
        """Return the visualization class that implements the rendering."""
        pass
    
    def register_with_engine(self, engine: VisualizationEngine) -> None:
        """Register this plugin with the visualization engine."""
        engine.register_visualization_type(
            self.get_visualization_type(),
            self.get_visualization_class()
        )

# TODO: Add support for animated visualizations
# TODO: Add support for real-time data updates
# TODO: Add support for custom color palettes
# TODO: Add support for accessibility features (screen readers, high contrast)
# TODO: Add support for exporting visualizations (PNG, SVG, PDF)