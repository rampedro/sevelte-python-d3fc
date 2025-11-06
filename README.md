# 🚀 Vizora - Interactive Data Visualization Platform

**Create stunning, interactive dashboards with Python + Svelte + DeckGL in minutes, not hours!**

Vizora is a fully open-source powerful, extensible platform that transforms raw data into beautiful, interactive visualizations. Whether you're a data scientist, analyst, or developer, Vizora makes it incredibly easy to create professional-grade dashboards that tell compelling data stories.

## ✨ Why Vizora?

- **🎯 Zero-Config Setup**: Get a stunning dashboard running in 3 commands
- **🌐 3D WebGL Visualizations**: Create breathtaking geospatial animations with DeckGL
- **🔧 Infinitely Extensible**: Plugin architecture for custom data sources and visualizations
- **🚀 Production Ready**: Professional Python package with CLI tools and proper deployment
- **📊 Smart Data Handling**: Automatically handles CSV, JSON, Excel, Parquet, and more
- **🎨 Beautiful by Default**: Modern UI with professional themes and responsive design

## 🎬 Quick Demo

```bash
# Install Vizora
pip install vizora

# Create a new project
vizora init my-dashboard --with-sample-data

# Launch your dashboard
cd my-dashboard
vizora run
```

**That's it!** Your interactive dashboard opens automatically in your browser with sample visualizations.

## 🌟 Key Features

### 🎯 **Effortless Data Visualization**
- **Smart Data Loading**: Automatically handles multiple file formats with intelligent type detection
- **One-Command Launch**: Unified startup script with automatic port detection
- **Real-time Updates**: Hot reload for both backend and frontend during development

### 🌐 **Advanced 3D Visualizations**
- **DeckGL Integration**: Hardware-accelerated 3D geospatial visualizations
- **WebGL Performance**: Smooth animations with 60fps rendering
- **Interactive Maps**: MapLibre GL with custom styling and layers

### 🔧 **Developer-Friendly Architecture**
- **Plugin System**: Extend functionality with custom data sources and visualizations
- **Type Safety**: Full TypeScript support with comprehensive type hints
- **Professional CLI**: Intuitive command-line tools for project management

### 📊 **Comprehensive Chart Library**
- **D3-Powered Charts**: Beautiful, interactive charts with smooth animations
- **Geospatial Analysis**: Advanced mapping with population data and custom markers
- **Financial Visualizations**: Specialized charts for trading and financial analysis

## Project Structure

```
sevelte-python-d3fc/
├── start.sh                 # One-command startup script
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── data/               # CSV data files
│       ├── cities.csv      # World cities with coordinates
│       ├── sales.csv       # Monthly sales data
│       ├── stock_prices.csv # Stock market data
│       └── population.csv  # Country demographics
└── frontend/
    ├── src/
    │   ├── routes/
    │   │   └── +page.svelte # Main application page
    │   └── lib/components/  # Svelte components
    │       ├── MapExample.svelte      # MapLibre GL world map
    │       ├── SalesChart.svelte      # D3 sales charts
    │       ├── StockChart.svelte      # DeckGL 3D overlay (Tokyo animation)
    │       └── PopulationChart.svelte # D3 population charts
    ├── package.json         # Node.js dependencies
    └── vite.config.ts      # Vite configuration
```

## 🚀 Installation & Quick Start

### Option 1: Install from PyPI (Recommended)

```bash
# Install Vizora
pip install vizora

# Create a new project with sample data
vizora init sales-dashboard --template finance --with-sample-data

# Launch your dashboard
cd sales-dashboard
vizora run
```

### Option 2: Development Installation

```bash
# Clone the repository
git clone https://github.com/rampedro/vizora.git
cd vizora

# Install in development mode
pip install -e ".[dev,all]"

# Run the example project
vizora run
```

### Your First Dashboard in 30 Seconds

```python
# Create main.py
from vizora import VizoraDashboard

# Initialize dashboard
dashboard = VizoraDashboard("My Analytics")

# Add your data
dashboard.add_data_source("sales.csv")

# Create visualizations
dashboard.add_visualization("bar", 
    data_source="sales", 
    x_column="month", 
    y_column="revenue",
    title="Monthly Revenue")

dashboard.add_visualization("deckgl_overlay",
    center_lat=35.6812,
    center_lng=139.7672, 
    title="3D Tokyo Animation")

# Launch!
dashboard.run()
```

## 📋 Requirements

- **Python**: 3.8+ (fully compatible with 3.13)
- **Node.js**: 18+ (for frontend development)
- **Memory**: 512MB minimum, 2GB recommended
- **Storage**: 100MB for installation, additional space for data

**Optional but recommended:**
- Git (for project management)
- Modern web browser with WebGL support

## API Endpoints

The Python backend provides the following REST endpoints:

- `GET /` - API health check
- `GET /api/cities` - World cities data with coordinates and population
- `GET /api/sales` - Monthly sales data by product category
- `GET /api/stock-prices` - Historical stock prices for major companies
- `GET /api/population` - Country population and GDP data

## Data Visualization Examples

### 1. MapLibre GL World Map
- Interactive map showing major world cities
- Population-based circle sizing and coloring
- Hover effects and detailed popups
- Custom legend and styling
- OpenStreetMap tile integration

### 2. DeckGL 3D Overlay (Tokyo Animation)
- **🌏 Advanced 3D WebGL visualization over Tokyo**
- Animated arc layers radiating from city center
- 3D building extrusions with realistic heights
- Smooth color transitions and real-time animations
- 60° pitch perspective for enhanced 3D viewing
- Based on deck.gl overlay technology

### 3. D3 Sales Charts
- Monthly sales performance by product category
- Grouped bar charts with responsive design
- Product-specific color coding
- Interactive hover effects

### 4. D3 Population Analysis
- Population trend lines by country
- GDP per capita comparison bars
- Multi-year data visualization
- Country-specific color schemes

## Technologies Used

### Backend
- **FastAPI**: Modern Python web framework
- **CSV Module**: Python 3.13 compatible data handling (replaced pandas)
- **Uvicorn**: ASGI server for FastAPI
- **CORS Middleware**: Cross-origin request handling

### Frontend
- **Svelte 5**: Latest reactive JavaScript framework
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and dev server
- **MapLibre GL**: Open-source mapping library
- **DeckGL**: Advanced 3D WebGL visualization framework
- **@svelte-maplibre-gl/deckgl**: Svelte bindings for DeckGL overlays
- **D3**: Data visualization utilities (selection, scale, array, format, axis, shape)

### 3D Visualization Stack
- **WebGL**: Hardware-accelerated 3D graphics
- **ArcLayer**: Animated arc visualizations
- **FillExtrusionLayer**: 3D building rendering
- **Real-time Animation**: requestAnimationFrame-based updates

## Development Tips

1. **Unified Startup**: Use `./start.sh` for automatic port detection and concurrent server startup
2. **Dynamic Port Assignment**: The startup script automatically finds available ports to avoid conflicts
3. **CORS**: The backend is configured to accept requests from any origin during development
4. **Hot Reload**: Both frontend and backend support hot reloading during development
5. **Data Format**: All CSV data is automatically converted to JSON by the backend
6. **Responsive Design**: All visualizations are designed to work on different screen sizes
7. **WebGL Performance**: DeckGL overlay uses hardware acceleration for smooth 3D animations
8. **Python 3.13 Compatibility**: Uses built-in CSV module instead of pandas for better compatibility

## Extending the Project

### Adding New Data Sources
1. Add new CSV files to `backend/data/`
2. Create new API endpoints in `backend/main.py`
3. Create corresponding Svelte components in `frontend/src/lib/components/`

### Customizing Visualizations
- Modify color schemes in component files
- Adjust chart dimensions and styling
- Add new D3 chart types
- Enhance MapLibre GL map features
- Create new DeckGL layer types (ScatterplotLayer, HexagonLayer, etc.)
- Implement custom WebGL shaders for advanced effects

### DeckGL Extensions
- Add more layer types from @deck.gl/layers
- Implement custom animations and transitions
- Create interactive 3D data visualizations
- Integrate with real-time data sources

## Troubleshooting

### Quick Fixes
- **Port conflicts**: Use `./start.sh` - it automatically finds available ports
- **Permission issues**: Run `chmod +x start.sh` to make the startup script executable
- **Both servers**: The startup script handles both backend and frontend simultaneously

### Backend Issues
- Ensure Python virtual environment is activated
- Check that all dependencies are installed: `pip list`
- Verify CSV files exist in the `data/` directory
- Python 3.13 compatibility: Uses csv module instead of pandas

### Frontend Issues
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check browser console for JavaScript errors
- Ensure backend is running and API_BASE_URL is correct

### DeckGL/WebGL Issues
- Check browser WebGL support: visit `chrome://gpu/`
- Ensure hardware acceleration is enabled
- Update graphics drivers if 3D animations are slow
- Check browser console for WebGL context errors

### CORS Issues
- The startup script automatically configures CORS for detected ports
- Check browser network tab for failed requests
- Verify both servers are running on expected ports

## License

This project is open source and available under the MIT License.