"""
📊 Vizora Data Manager - Your Data's Best Friend

The DataManager is like a personal assistant for your data. It handles all 
the boring stuff like loading different file formats, caching for performance,
and serving data in exactly the format your visualizations need.

We've designed it to be incredibly smart about data types and formats, so 
you can focus on insights instead of data wrangling!
"""

import csv
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class DatasetInfo:
    """
    📋 Metadata about a dataset.
    
    This keeps track of useful information about your data files,
    like when they were last modified and how big they are.
    """
    name: str
    file_path: str
    size_bytes: int
    last_modified: datetime
    row_count: int
    column_count: int
    columns: List[str]
    data_types: Dict[str, str]


class DataManager:
    """
    🗃️ The data management powerhouse of Vizora.
    
    This class handles all your data needs with grace and efficiency:
    - Loads data from multiple formats (CSV, JSON, Excel, Parquet)
    - Intelligent type detection and conversion
    - Smart caching for blazing-fast performance
    - Memory-efficient handling of large datasets
    
    Example:
        >>> dm = DataManager("./data")
        >>> dm.load_dataset("sales.csv", "sales_data")
        >>> data = dm.get_dataset("sales_data")  # Lightning fast!
    """
    
    def __init__(self, data_dir: str = "data", max_size_mb: int = 100):
        """
        Initialize the DataManager with intelligence and care.
        
        Args:
            data_dir: Directory where your data files live
            max_size_mb: Maximum file size to load (safety first!)
        """
        self.data_dir = Path(data_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024  # Convert to bytes
        self.datasets: Dict[str, Any] = {}
        self.dataset_info: Dict[str, DatasetInfo] = {}
        self.logger = logging.getLogger("vizora.data")
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True, parents=True)
        
        self.logger.info(f"📊 DataManager initialized (max size: {max_size_mb}MB)")
    
    def load_dataset(self, file_path: Union[str, Path], name: Optional[str] = None) -> str:
        """
        Load a dataset with intelligence and style.
        
        This method is like a Swiss Army knife for data loading. It automatically
        detects file formats, handles encoding issues, and converts data types
        intelligently. Just point it at your data and watch it work!
        
        Args:
            file_path: Path to your data file
            name: Optional name for the dataset (defaults to filename)
            
        Returns:
            The name of the loaded dataset
            
        Raises:
            FileNotFoundError: When the file doesn't exist
            ValueError: When the file is too large or unsupported format
        """
        file_path = Path(file_path)
        dataset_name = name or file_path.stem
        
        # 🔍 Check if file exists and is reasonable size
        if not file_path.exists():
            # Try looking in the data directory
            file_path = self.data_dir / file_path.name
            if not file_path.exists():
                raise FileNotFoundError(f"Data file not found: {file_path}")
        
        file_size = file_path.stat().st_size
        if file_size > self.max_size_bytes:
            raise ValueError(f"File too large: {file_size / 1024**2:.1f}MB (max: {self.max_size_bytes / 1024**2}MB)")
        
        # 🎯 Load data based on file extension
        self.logger.info(f"📥 Loading dataset: {dataset_name} ({file_size / 1024:.1f}KB)")
        
        try:
            if file_path.suffix.lower() == '.csv':
                data = self._load_csv(file_path)
            elif file_path.suffix.lower() == '.json':
                data = self._load_json(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                data = self._load_excel(file_path)
            elif file_path.suffix.lower() == '.parquet':
                data = self._load_parquet(file_path)
            else:
                # Default to CSV with different delimiters
                data = self._load_csv_flexible(file_path)
            
            # 📊 Store dataset and metadata
            self.datasets[dataset_name] = data
            self.dataset_info[dataset_name] = self._create_dataset_info(dataset_name, file_path, data)
            
            self.logger.info(f"✅ Loaded {len(data)} rows, {len(data[0]) if data else 0} columns")
            return dataset_name
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load {file_path}: {e}")
            raise
    
    def _load_csv(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Load CSV with intelligent parsing and type detection.
        
        This isn't your grandmother's CSV loader! We automatically detect
        delimiters, handle encoding issues, and convert data types intelligently.
        """
        data = []
        
        # Try different encodings (because the world is messy)
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, newline='') as file:
                    # Auto-detect delimiter (CSV files can be surprisingly creative)
                    sample = file.read(1024)
                    file.seek(0)
                    
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                    
                    reader = csv.DictReader(file, delimiter=delimiter)
                    data = [self._convert_row_types(row) for row in reader]
                    break
                    
            except UnicodeDecodeError:
                continue  # Try next encoding
            except Exception as e:
                if encoding == encodings[-1]:  # Last encoding attempt
                    raise e
                continue
        
        if not data:
            raise ValueError("Could not load CSV file with any supported encoding")
        
        return data
    
    def _load_csv_flexible(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Flexible CSV loader that tries different delimiters.
        
        Sometimes files claim to be CSV but use semicolons, tabs, or other
        creative separators. This method tries them all!
        """
        delimiters = [',', ';', '\t', '|']
        
        for delimiter in delimiters:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file, delimiter=delimiter)
                    data = [self._convert_row_types(row) for row in reader]
                    
                    # Check if we got reasonable data (more than one column)
                    if data and len(data[0]) > 1:
                        return data
                        
            except Exception:
                continue
        
        # Fallback: treat as single-column data
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            return [{'value': line.strip()} for line in lines if line.strip()]
    
    def _load_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Load JSON with intelligent structure detection.
        
        JSON can come in many shapes - arrays of objects, nested structures,
        or single objects. We handle them all gracefully!
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_data = json.load(file)
        
        # Handle different JSON structures
        if isinstance(raw_data, list):
            # Array of objects - perfect!
            return [self._convert_row_types(row) if isinstance(row, dict) else {'value': row} 
                   for row in raw_data]
        elif isinstance(raw_data, dict):
            # Single object - convert to single-row dataset
            return [self._convert_row_types(raw_data)]
        else:
            # Primitive value - wrap it
            return [{'value': raw_data}]
    
    def _load_excel(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Load Excel files (because sometimes data comes from spreadsheets).
        
        We use the first sheet by default, but this could be extended to
        handle multiple sheets or let users specify which sheet to use.
        """
        try:
            import pandas as pd
            df = pd.read_excel(file_path, engine='openpyxl')
            return df.to_dict('records')
        except ImportError:
            raise ImportError("Excel support requires pandas and openpyxl: pip install pandas openpyxl")
    
    def _load_parquet(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Load Parquet files (for when you're dealing with big data).
        
        Parquet is great for large datasets because it's compressed and 
        columnar. Perfect for analytics workloads!
        """
        try:
            import pandas as pd
            df = pd.read_parquet(file_path)
            return df.to_dict('records')
        except ImportError:
            raise ImportError("Parquet support requires pandas and pyarrow: pip install pandas pyarrow")
    
    def _convert_row_types(self, row: Dict[str, str]) -> Dict[str, Any]:
        """
        Intelligently convert string values to appropriate Python types.
        
        This is where the magic happens! We look at each value and try to
        figure out if it's really a number, date, boolean, etc. Much smarter
        than leaving everything as strings.
        """
        converted = {}
        
        for key, value in row.items():
            if value is None or value == '':
                converted[key] = None
            elif isinstance(value, str):
                converted[key] = self._smart_convert(value.strip())
            else:
                converted[key] = value
        
        return converted
    
    def _smart_convert(self, value: str) -> Any:
        """
        Smart type conversion that handles the messy real world.
        
        Real-world data is messy. This function tries really hard to figure
        out what type each value should be, handling things like:
        - Numbers with commas (1,234.56)
        - Percentages (45.6%)
        - Booleans (yes/no, true/false, 1/0)
        - Dates in various formats
        """
        if not value:
            return None
        
        # Try boolean first (common in surveys)
        bool_lower = value.lower()
        if bool_lower in ['true', 'yes', 'y', '1', 'on']:
            return True
        elif bool_lower in ['false', 'no', 'n', '0', 'off']:
            return False
        
        # Try percentage
        if value.endswith('%'):
            try:
                return float(value[:-1]) / 100
            except ValueError:
                pass
        
        # Try number (with or without commas)
        try:
            # Remove commas and try as integer first
            clean_value = value.replace(',', '')
            if '.' not in clean_value:
                return int(clean_value)
            else:
                return float(clean_value)
        except ValueError:
            pass
        
        # Try date (basic ISO format)
        if len(value) >= 8 and ('-' in value or '/' in value):
            try:
                # This is a simplified date parser - could be much more sophisticated
                from datetime import datetime
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
            except ImportError:
                pass
        
        # Default to string
        return value
    
    def _create_dataset_info(self, name: str, file_path: Path, data: List[Dict[str, Any]]) -> DatasetInfo:
        """
        Create comprehensive metadata about a dataset.
        
        This information is super useful for debugging, monitoring, and
        helping users understand their data better.
        """
        if not data:
            columns = []
            data_types = {}
        else:
            columns = list(data[0].keys())
            # Analyze data types from first few rows
            data_types = {}
            sample_size = min(10, len(data))
            for col in columns:
                types = [type(row.get(col, None)).__name__ for row in data[:sample_size]]
                # Most common type wins
                data_types[col] = max(set(types), key=types.count)
        
        return DatasetInfo(
            name=name,
            file_path=str(file_path),
            size_bytes=file_path.stat().st_size,
            last_modified=datetime.fromtimestamp(file_path.stat().st_mtime),
            row_count=len(data),
            column_count=len(columns),
            columns=columns,
            data_types=data_types
        )
    
    @lru_cache(maxsize=32)
    def get_dataset(self, name: str) -> List[Dict[str, Any]]:
        """
        Get a dataset with lightning-fast caching.
        
        The @lru_cache decorator means repeated requests for the same dataset
        are served from memory instantly. Perfect for dashboards that refresh
        frequently!
        
        Args:
            name: Name of the dataset to retrieve
            
        Returns:
            The dataset as a list of dictionaries
            
        Raises:
            KeyError: If the dataset doesn't exist
        """
        if name not in self.datasets:
            raise KeyError(f"Dataset '{name}' not found. Available: {list(self.datasets.keys())}")
        
        return self.datasets[name]
    
    def get_dataset_info(self, name: str) -> DatasetInfo:
        """
        Get detailed information about a dataset.
        
        This is perfect for debugging or showing users information about
        their data in the dashboard.
        """
        if name not in self.dataset_info:
            raise KeyError(f"Dataset info for '{name}' not found")
        
        return self.dataset_info[name]
    
    def list_datasets(self) -> List[str]:
        """
        Get a list of all loaded datasets.
        
        Handy for debugging or letting users choose which dataset to visualize.
        """
        return list(self.datasets.keys())
    
    def get_last_modified(self, name: str) -> datetime:
        """
        Get the last modified time of a dataset's source file.
        
        Useful for cache invalidation and showing users how fresh their data is.
        """
        info = self.get_dataset_info(name)
        return info.last_modified
    
    def reload_dataset(self, name: str) -> None:
        """
        Reload a dataset from its source file.
        
        Perfect for when you know the underlying data has changed and you
        want to refresh the dashboard.
        """
        if name not in self.dataset_info:
            raise KeyError(f"Cannot reload unknown dataset: {name}")
        
        info = self.dataset_info[name]
        self.load_dataset(info.file_path, name)
        self.logger.info(f"🔄 Reloaded dataset: {name}")
    
    def get_column_stats(self, dataset_name: str, column_name: str) -> Dict[str, Any]:
        """
        Get statistical information about a specific column.
        
        This is incredibly useful for understanding your data and creating
        better visualizations. We calculate different stats based on the
        data type.
        """
        data = self.get_dataset(dataset_name)
        values = [row.get(column_name) for row in data if row.get(column_name) is not None]
        
        if not values:
            return {"error": "No data found for column"}
        
        stats = {
            "count": len(values),
            "null_count": len(data) - len(values),
            "data_type": type(values[0]).__name__
        }
        
        # Numeric statistics
        if all(isinstance(v, (int, float)) for v in values):
            stats.update({
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "unique_count": len(set(values))
            })
        
        # String statistics
        elif all(isinstance(v, str) for v in values):
            stats.update({
                "unique_count": len(set(values)),
                "avg_length": sum(len(v) for v in values) / len(values),
                "most_common": max(set(values), key=values.count)
            })
        
        return stats

# 🔧 Extension Points for Advanced Users

class DataProcessorPlugin:
    """
    🧩 Base class for custom data processors.
    
    Want to add custom data transformations? Inherit from this class!
    Perfect for things like:
    - Custom data cleaning pipelines
    - Integration with external APIs
    - Real-time data streaming
    - Custom aggregations
    """
    
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process data and return the transformed result.
        
        Override this method in your custom processor.
        """
        raise NotImplementedError("Subclasses must implement process()")

# TODO: Add support for real-time data streams
# TODO: Add support for database connections (PostgreSQL, MySQL, etc.)
# TODO: Add support for cloud storage (S3, GCS, Azure Blob)
# TODO: Add data validation and quality checks
# TODO: Add data transformation pipelines