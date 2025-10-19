from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import csv
import json
from pathlib import Path

app = FastAPI(title="Svelte Python D3FC API", version="1.0.0")

# Enable CORS for all origins (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"

def read_csv_to_dict(file_path):
    """Helper function to read CSV file and return as list of dictionaries"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

@app.get("/")
async def root():
    return {"message": "Svelte Python D3FC API"}

@app.get("/api/cities")
async def get_cities():
    """Get cities data with population information"""
    try:
        data = read_csv_to_dict(DATA_DIR / "cities.csv")
        # Convert population to float for proper JSON serialization
        for row in data:
            if 'population' in row:
                row['population'] = float(row['population'])
            if 'latitude' in row:
                row['latitude'] = float(row['latitude'])
            if 'longitude' in row:
                row['longitude'] = float(row['longitude'])
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Cities data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading cities data: {str(e)}")

@app.get("/api/sales")
async def get_sales():
    """Get monthly sales data"""
    try:
        data = read_csv_to_dict(DATA_DIR / "sales.csv")
        # Convert sales to float for proper JSON serialization
        for row in data:
            if 'sales' in row:
                row['sales'] = float(row['sales'])
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Sales data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading sales data: {str(e)}")

@app.get("/api/stock-prices")
async def get_stock_prices():
    """Get stock prices data"""
    try:
        data = read_csv_to_dict(DATA_DIR / "stock_prices.csv")
        # Convert numeric fields to proper types
        for row in data:
            if 'close' in row:
                row['close'] = float(row['close'])
            if 'volume' in row:
                row['volume'] = int(row['volume'])
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Stock prices data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading stock prices data: {str(e)}")

@app.get("/api/population")
async def get_population():
    """Get population by age group data"""
    try:
        data = read_csv_to_dict(DATA_DIR / "population.csv")
        # Convert population to int for proper JSON serialization
        for row in data:
            if 'population' in row:
                row['population'] = int(row['population'])
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Population data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading population data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)