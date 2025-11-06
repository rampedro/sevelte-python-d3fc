# 🔧 Vizora Development Guide

This guide helps you set up a complete development environment for contributing to Vizora.

## 🏗️ Architecture Overview

Vizora follows a modular architecture with clear separation of concerns:

```
vizora/
├── core/                   # Core platform components
│   ├── dashboard.py       # Main dashboard orchestrator
│   ├── data_manager.py    # Data loading and management
│   ├── visualization_engine.py  # Visualization processing
│   └── utils.py          # Utility functions
├── plugins/               # Plugin system
│   ├── base_plugin.py    # Plugin base classes
│   ├── data_sources/     # Data source plugins
│   └── visualizations/   # Visualization plugins
├── cli/                   # Command-line interface
│   └── main.py           # CLI commands
├── frontend/              # Svelte frontend (when generated)
└── templates/             # Project templates
```

## 🌟 Key Components

### VizoraDashboard
The main orchestrator that brings everything together:
- Manages FastAPI server lifecycle
- Coordinates data sources and visualizations
- Handles plugin registration and lifecycle
- Provides WebSocket real-time updates

### DataManager
Intelligent data handling with smart format detection:
- Supports CSV, JSON, Excel, Parquet formats
- Automatic type inference and validation
- Caching for performance
- Extensible through plugins

### VisualizationEngine
Processes and renders visualizations:
- Plugin-based architecture
- Multiple rendering backends (D3.js, DeckGL, Plotly)
- Real-time data streaming
- Configuration management

## 🔌 Plugin System

Vizora's plugin system allows easy extension through two main plugin types:

### Data Source Plugins
```python
from vizora.plugins import DataSourcePlugin, PluginMetadata

class DatabasePlugin(DataSourcePlugin):
    def get_metadata(self):
        return PluginMetadata(
            name="postgres-source",
            version="1.0.0",
            author="Your Name",
            description="PostgreSQL data source"
        )
    
    def load_data(self, config):
        # Database connection and query logic
        return dataframe
    
    def get_schema(self):
        # Return available tables/columns
        return schema_info
```

### Visualization Plugins
```python
from vizora.plugins import VisualizationPlugin, PluginMetadata

class CustomChartPlugin(VisualizationPlugin):
    def get_metadata(self):
        return PluginMetadata(
            name="custom-chart",
            version="1.0.0",
            author="Your Name",
            description="Custom chart visualization"
        )
    
    def render(self, data, config):
        # Generate visualization spec
        return {
            "type": "custom_chart",
            "spec": chart_specification,
            "data": processed_data
        }
```

## 🧪 Testing Strategy

We use a comprehensive testing approach:

### Unit Tests
```python
# tests/test_data_manager.py
import pytest
from vizora.core.data_manager import DataManager

def test_csv_loading():
    manager = DataManager()
    data = manager.load_data("sample.csv")
    assert len(data) > 0
    assert "column1" in data.columns

def test_invalid_file():
    manager = DataManager()
    with pytest.raises(FileNotFoundError):
        manager.load_data("nonexistent.csv")
```

### Integration Tests
```python
# tests/test_dashboard_integration.py
import pytest
from vizora.core.dashboard import VizoraDashboard

@pytest.mark.asyncio
async def test_dashboard_startup():
    config = DashboardConfig(port=8001, debug=True)
    dashboard = VizoraDashboard(config)
    
    await dashboard.start()
    assert dashboard.is_running()
    
    await dashboard.stop()
    assert not dashboard.is_running()
```

### End-to-End Tests
```python
# tests/test_e2e.py
import requests
from vizora.cli.main import cli

def test_full_workflow():
    # Start dashboard
    result = runner.invoke(cli, ['run', '--port', '8002'])
    
    # Upload data
    response = requests.post(
        "http://localhost:8002/api/data",
        files={"file": open("sample.csv", "rb")}
    )
    assert response.status_code == 200
    
    # Create visualization
    viz_response = requests.post(
        "http://localhost:8002/api/visualizations",
        json={"type": "bar_chart", "data_id": "sample.csv"}
    )
    assert viz_response.status_code == 200
```

## 🎨 Frontend Development

The frontend is built with Svelte and modern web technologies:

### Project Structure
```
frontend/
├── src/
│   ├── components/        # Reusable components
│   │   ├── charts/       # Chart components
│   │   ├── ui/           # UI components
│   │   └── layout/       # Layout components
│   ├── stores/           # Svelte stores for state
│   ├── utils/            # Utility functions
│   └── App.svelte        # Main application
├── public/               # Static assets
└── package.json          # Dependencies
```

### Key Technologies
- **Svelte**: Reactive UI framework
- **D3.js**: Data visualization
- **DeckGL**: 3D/GIS visualizations
- **Tailwind CSS**: Utility-first styling
- **Vite**: Build tool and dev server

### Development Commands
```bash
# Frontend development
cd frontend/
npm install
npm run dev        # Start dev server
npm run build      # Production build
npm run preview    # Preview production build
```

## 🔄 Data Flow

Understanding how data flows through Vizora:

1. **Data Ingestion**: DataManager loads and validates data
2. **Processing**: VisualizationEngine processes data for rendering
3. **Plugin System**: Plugins extend functionality at each step
4. **Frontend**: Svelte components render visualizations
5. **Real-time Updates**: WebSocket connections for live data

## 🚀 Performance Optimization

### Backend Optimization
- **Async/Await**: All I/O operations are asynchronous
- **Caching**: Smart caching of processed data
- **Lazy Loading**: Load plugins and data on demand
- **Connection Pooling**: Efficient database connections

### Frontend Optimization
- **Code Splitting**: Dynamic imports for large visualizations
- **Virtual Scrolling**: Handle large datasets efficiently
- **Web Workers**: Offload heavy computations
- **Progressive Loading**: Show results as they become available

## 🔧 Debugging

### Common Issues and Solutions

#### Plugin Not Loading
```python
# Check plugin registration
from vizora.plugins import get_registered_plugins
print(get_registered_plugins())

# Verify plugin metadata
plugin = MyPlugin()
print(plugin.get_metadata())
```

#### Data Loading Issues
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check data manager state
manager = DataManager()
print(manager.get_supported_formats())
```

#### Frontend Connection Issues
```javascript
// Check WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('Connected');
ws.onerror = (error) => console.error('WebSocket error:', error);
```

## 📊 Monitoring and Metrics

Vizora includes built-in monitoring capabilities:

### Performance Metrics
- Request/response times
- Memory usage
- Plugin load times
- Data processing times

### Health Checks
```python
# Built-in health check endpoint
GET /health

# Response:
{
    "status": "healthy",
    "version": "1.0.0",
    "uptime": 3600,
    "plugins": {
        "loaded": 5,
        "failed": 0
    }
}
```

## 🔐 Security Considerations

- **Input Validation**: All user inputs are validated
- **File Upload Limits**: Configurable size and type restrictions
- **Plugin Sandboxing**: Plugins run in isolated environments
- **CORS Configuration**: Proper cross-origin settings
- **Rate Limiting**: Prevent abuse of API endpoints

## 📚 Additional Resources

- **API Documentation**: `/docs` endpoint when running
- **Plugin Examples**: `examples/plugins/` directory
- **Frontend Storybook**: Component library documentation
- **Architecture Decision Records**: `docs/adr/` directory

---

Happy coding! 🎉 If you have questions, don't hesitate to ask in our GitHub Discussions or Discord community.