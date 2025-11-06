"""
🎯 Vizora Dashboard - The Heart of Your Data Story

This is where the magic happens! The VizoraDashboard class orchestrates 
everything from data loading to visualization rendering. Think of it as 
the conductor of your data visualization symphony.

We've designed this to be incredibly intuitive - you can have a stunning 
dashboard running in just 3 lines of code, but it's also powerful enough 
to handle complex, multi-layered visualizations.
"""

import os
import sys
import subprocess
import signal
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from .data_manager import DataManager
from .visualization_engine import VisualizationEngine
from .utils import PortManager, PathHelper
from ..plugins.base_plugin import BasePlugin


@dataclass
class DashboardConfig:
    """
    📋 Configuration settings for your Vizora dashboard.
    
    This is like the control panel for your entire dashboard. You can 
    customize everything from the app name to advanced server settings.
    Most of the time, the defaults work perfectly!
    """
    name: str = "Vizora Dashboard"
    description: str = "Interactive Data Visualization Platform"
    host: str = "0.0.0.0"
    backend_port: Optional[int] = None  # Auto-detect if None
    frontend_port: Optional[int] = None  # Auto-detect if None
    debug: bool = True
    auto_reload: bool = True
    data_directory: str = "data"
    template_directory: str = "templates"
    plugins: List[str] = field(default_factory=list)
    
    # 🎨 UI Customization
    theme: str = "modern"  # modern, classic, minimal
    primary_color: str = "#667eea"
    accent_color: str = "#764ba2"
    
    # 🔧 Advanced Settings
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    max_data_size_mb: int = 100
    cache_enabled: bool = True


class VizoraDashboard:
    """
    🚀 The main Vizora Dashboard class.
    
    This is your one-stop shop for creating amazing data visualizations.
    It handles everything behind the scenes so you can focus on telling 
    your data story.
    
    Example:
        >>> dashboard = VizoraDashboard("Sales Analytics")
        >>> dashboard.add_data("sales.csv")
        >>> dashboard.add_chart("bar", x="month", y="revenue")
        >>> dashboard.run()  # 🎉 Your dashboard is live!
    """
    
    def __init__(self, name: str = "Vizora Dashboard", config: Optional[DashboardConfig] = None):
        """
        Initialize your dashboard with love and attention to detail.
        
        Args:
            name: A friendly name for your dashboard
            config: Advanced configuration (optional - we've got sensible defaults!)
        """
        self.config = config or DashboardConfig(name=name)
        self.logger = self._setup_logging()
        
        # 🏗️ Core components - these are the building blocks of awesomeness
        self.data_manager = DataManager(
            data_dir=self.config.data_directory,
            max_size_mb=self.config.max_data_size_mb
        )
        self.viz_engine = VisualizationEngine()
        self.plugins: Dict[str, BasePlugin] = {}
        
        # 🌐 FastAPI application - this serves your data
        self.app = self._create_fastapi_app()
        
        # 🔧 Utilities
        self.port_manager = PortManager()
        self.path_helper = PathHelper()
        
        # 📊 Dashboard state
        self.visualizations: List[Dict[str, Any]] = []
        self.is_running = False
        
        self.logger.info(f"🎯 {self.config.name} initialized successfully!")
    
    def _setup_logging(self) -> logging.Logger:
        """
        Set up beautiful, human-readable logging.
        
        We use emojis and colors to make logs actually enjoyable to read!
        """
        logger = logging.getLogger("vizora")
        logger.setLevel(logging.INFO if self.config.debug else logging.WARNING)
        
        # Create a handler that doesn't suck
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s | 🎯 %(name)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _create_fastapi_app(self) -> FastAPI:
        """
        Create our FastAPI application with all the bells and whistles.
        
        This includes CORS middleware, error handling, and all the API 
        endpoints your frontend needs to create beautiful visualizations.
        """
        app = FastAPI(
            title=self.config.name,
            description=self.config.description,
            version="1.0.0",
            docs_url="/api/docs",  # Because good APIs deserve good docs!
            redoc_url="/api/redoc"
        )
        
        # 🌍 Enable CORS - because browsers can be picky
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 📡 Register API routes
        self._register_routes(app)
        
        return app
    
    def _register_routes(self, app: FastAPI) -> None:
        """
        Register all the API endpoints that make the magic happen.
        
        These endpoints serve your data to the frontend in exactly the 
        format it needs. No more wrestling with data formats!
        """
        
        @app.get("/")
        async def health_check():
            """A friendly hello from your dashboard! 👋"""
            return {
                "message": f"🎯 {self.config.name} is running smoothly!",
                "version": "1.0.0",
                "status": "healthy",
                "endpoints": {
                    "data": "/api/data/{dataset_name}",
                    "visualizations": "/api/visualizations",
                    "config": "/api/config"
                }
            }
        
        @app.get("/api/data/{dataset_name}")
        async def get_data(dataset_name: str):
            """
            Serve your data in the perfect format for visualizations.
            
            This endpoint automatically handles CSV, JSON, and other formats,
            and returns clean, structured data that's ready to visualize.
            """
            try:
                data = self.data_manager.get_dataset(dataset_name)
                return {
                    "data": data,
                    "count": len(data),
                    "dataset": dataset_name,
                    "timestamp": self.data_manager.get_last_modified(dataset_name)
                }
            except FileNotFoundError:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Dataset '{dataset_name}' not found. Available datasets: {self.data_manager.list_datasets()}"
                )
            except Exception as e:
                self.logger.error(f"Error loading dataset {dataset_name}: {e}")
                raise HTTPException(status_code=500, detail=f"Error loading dataset: {str(e)}")
        
        @app.get("/api/visualizations")
        async def get_visualizations():
            """Return the configuration for all registered visualizations."""
            return {
                "visualizations": self.visualizations,
                "count": len(self.visualizations),
                "plugins": list(self.plugins.keys())
            }
        
        @app.get("/api/config")
        async def get_config():
            """Return the dashboard configuration (sanitized for security)."""
            return {
                "name": self.config.name,
                "description": self.config.description,
                "theme": self.config.theme,
                "primary_color": self.config.primary_color,
                "accent_color": self.config.accent_color,
                "debug": self.config.debug
            }
    
    def add_data_source(self, file_path: str, name: Optional[str] = None) -> 'VizoraDashboard':
        """
        Add a data source to your dashboard.
        
        This is where you feed your dashboard the data it needs to create 
        amazing visualizations. We support CSV, JSON, Excel, and more!
        
        Args:
            file_path: Path to your data file
            name: Optional name for the dataset (defaults to filename)
            
        Returns:
            Self for method chaining (because fluent APIs are nice!)
        """
        try:
            dataset_name = name or Path(file_path).stem
            self.data_manager.load_dataset(file_path, dataset_name)
            self.logger.info(f"📊 Added data source: {dataset_name}")
            return self
        except Exception as e:
            self.logger.error(f"❌ Failed to add data source {file_path}: {e}")
            raise
    
    def add_visualization(self, viz_type: str, **kwargs) -> 'VizoraDashboard':
        """
        Add a visualization to your dashboard.
        
        This is where you define what kind of chart or map you want to show.
        We've made it super flexible - you can create anything from simple
        bar charts to complex 3D geospatial visualizations!
        
        Args:
            viz_type: Type of visualization (bar, line, map, deckgl_overlay, etc.)
            **kwargs: Configuration specific to the visualization type
            
        Returns:
            Self for method chaining
        """
        viz_config = {
            "type": viz_type,
            "id": f"viz_{len(self.visualizations)}",
            "config": kwargs
        }
        
        self.visualizations.append(viz_config)
        self.logger.info(f"🎨 Added {viz_type} visualization")
        return self
    
    def add_plugin(self, plugin: BasePlugin) -> 'VizoraDashboard':
        """
        Add a custom plugin to extend your dashboard's capabilities.
        
        Plugins are where Vizora really shines! You can create custom 
        visualizations, data processors, or completely new features.
        
        Args:
            plugin: An instance of a BasePlugin subclass
            
        Returns:
            Self for method chaining
        """
        self.plugins[plugin.name] = plugin
        plugin.register(self)
        self.logger.info(f"🔌 Added plugin: {plugin.name}")
        return self
    
    def run(self, 
           backend_port: Optional[int] = None, 
           frontend_port: Optional[int] = None,
           open_browser: bool = True) -> None:
        """
        🚀 Launch your dashboard and watch the magic happen!
        
        This starts both the backend API server and the frontend development 
        server. It handles all the boring stuff like port management and 
        process coordination, so you can focus on the exciting stuff.
        
        Args:
            backend_port: Port for the API server (auto-detected if None)
            frontend_port: Port for the frontend (auto-detected if None)  
            open_browser: Whether to automatically open the dashboard in your browser
        """
        try:
            # 🔍 Find available ports
            self.config.backend_port = backend_port or self.port_manager.find_available_port(8000, 8010)
            self.config.frontend_port = frontend_port or self.port_manager.find_available_port(5174, 5184)
            
            self.logger.info(f"🎯 Starting {self.config.name}...")
            self.logger.info(f"🔍 Backend will run on port {self.config.backend_port}")
            self.logger.info(f"⚡ Frontend will run on port {self.config.frontend_port}")
            
            # 🐍 Start the backend server
            self._start_backend()
            
            # ⚡ Start the frontend server (if frontend exists)
            if self._has_frontend():
                self._start_frontend()
            
            # 🌐 Open browser if requested
            if open_browser:
                self._open_dashboard()
            
            self.is_running = True
            self.logger.info("🎉 Dashboard is running! Press Ctrl+C to stop.")
            
            # Keep the main process alive
            self._wait_for_shutdown()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start dashboard: {e}")
            raise
    
    def _start_backend(self) -> None:
        """Start the FastAPI backend server."""
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.backend_port,
            reload=self.config.auto_reload,
            log_level="info" if self.config.debug else "warning"
        )
    
    def _start_frontend(self) -> None:
        """Start the Svelte frontend development server."""
        # This would typically run npm run dev in the frontend directory
        # Implementation depends on the specific frontend setup
        pass
    
    def _has_frontend(self) -> bool:
        """Check if a frontend directory exists."""
        frontend_path = Path("frontend")
        return frontend_path.exists() and (frontend_path / "package.json").exists()
    
    def _open_dashboard(self) -> None:
        """Open the dashboard in the default web browser."""
        import webbrowser
        url = f"http://localhost:{self.config.frontend_port}"
        webbrowser.open(url)
        self.logger.info(f"🌐 Opening dashboard at {url}")
    
    def _wait_for_shutdown(self) -> None:
        """Wait for shutdown signal and clean up gracefully."""
        try:
            # Handle Ctrl+C gracefully
            signal.signal(signal.SIGINT, self._shutdown_handler)
            signal.pause()
        except KeyboardInterrupt:
            self._shutdown()
    
    def _shutdown_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info("🛑 Received shutdown signal...")
        self._shutdown()
    
    def _shutdown(self) -> None:
        """Clean up and shut down all services."""
        self.logger.info("🧹 Cleaning up...")
        self.is_running = False
        # Additional cleanup would go here
        self.logger.info("✅ Shutdown complete")
        sys.exit(0)

# 🎯 Extension Points - These are hooks for advanced users to customize behavior

class DashboardExtensions:
    """
    🔧 Extension points for advanced customization.
    
    These are like plugin hooks that let you modify dashboard behavior 
    at key points. Perfect for when you need something really specific!
    """
    
    # TODO: Add hooks for data processing pipeline
    # TODO: Add hooks for custom authentication
    # TODO: Add hooks for custom visualization types
    # TODO: Add hooks for custom API endpoints
    
    pass