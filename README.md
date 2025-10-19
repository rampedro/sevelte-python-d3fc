# Svelte + Python + D3FC + MapLibre GL Dashboard

A modern data visualization dashboard that combines a Python FastAPI backend with a Svelte frontend, featuring interactive maps using MapLibre GL and charts using D3FC.

## Features

- **Python Backend**: FastAPI server serving CSV data through REST endpoints
- **Svelte Frontend**: Modern reactive UI with TypeScript support
- **MapLibre GL**: Interactive world cities map with population-based visualization
- **D3FC Charts**: Advanced data visualization including:
  - Sales performance bar charts
  - Stock price line charts with volume analysis
  - Population trends and GDP comparison charts

## Project Structure

```
sevelte-python-d3fc/
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
    │       ├── SalesChart.svelte      # D3FC sales charts
    │       ├── StockChart.svelte      # D3FC stock analysis
    │       └── PopulationChart.svelte # D3FC population charts
    ├── package.json         # Node.js dependencies
    └── vite.config.ts      # Vite configuration
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI server:
   ```bash
   python main.py
   ```

   The backend will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at http://localhost:5173

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

### 2. D3FC Sales Charts
- Monthly sales performance by product category
- Grouped bar charts with responsive design
- Product-specific color coding

### 3. D3FC Stock Analysis
- Time series line charts for stock prices
- Trading volume bar charts
- Multi-symbol comparison with legends
- Interactive tooltips and styling

### 4. D3FC Population Analysis
- Population trend lines by country
- GDP per capita comparison bars
- Multi-year data visualization
- Country-specific color schemes

## Technologies Used

### Backend
- **FastAPI**: Modern Python web framework
- **Pandas**: Data manipulation and analysis
- **Uvicorn**: ASGI server for FastAPI

### Frontend
- **Svelte**: Reactive JavaScript framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **MapLibre GL**: Open-source mapping library
- **D3FC**: Financial charting library built on D3
- **D3**: Data visualization utilities

## Development Tips

1. **CORS**: The backend is configured to accept requests from any origin during development
2. **Hot Reload**: Both frontend and backend support hot reloading during development
3. **Data Format**: All CSV data is automatically converted to JSON by the backend
4. **Responsive Design**: All visualizations are designed to work on different screen sizes

## Extending the Project

### Adding New Data Sources
1. Add new CSV files to `backend/data/`
2. Create new API endpoints in `backend/main.py`
3. Create corresponding Svelte components in `frontend/src/lib/components/`

### Customizing Visualizations
- Modify color schemes in component files
- Adjust chart dimensions and styling
- Add new D3FC chart types
- Enhance MapLibre GL map features

## Troubleshooting

### Backend Issues
- Ensure Python virtual environment is activated
- Check that all dependencies are installed: `pip list`
- Verify CSV files exist in the `data/` directory

### Frontend Issues
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check browser console for JavaScript errors
- Ensure backend is running on port 8000

### CORS Issues
- Verify backend CORS configuration allows frontend origin
- Check browser network tab for failed requests
- Ensure both servers are running on expected ports

## License

This project is open source and available under the MIT License.