"""
🚀 Vizora Setup Configuration

This setup.py file defines how Vizora is packaged and distributed.
We've included everything needed for a professional Python package
that can be installed via pip and distributed to PyPI.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for the long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read version from the version file
version_file = Path(__file__).parent / "vizora" / "__version__.py"
version_dict = {}
if version_file.exists():
    exec(version_file.read_text(), version_dict)
    version = version_dict.get("__version__", "1.0.0")
else:
    version = "1.0.0"

# Core dependencies - these are the minimum requirements
install_requires = [
    # Web framework and server
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    
    # Data handling
    "pandas>=2.0.0",  # For advanced data operations
    "numpy>=1.24.0",  # Numerical computations
    
    # CLI and utilities
    "click>=8.0.0",   # Command-line interface
    "rich>=13.0.0",   # Beautiful terminal output
    
    # Configuration and serialization
    "pydantic>=2.0.0", # Data validation and settings
    "PyYAML>=6.0.0",   # YAML configuration files
    
    # File handling
    "openpyxl>=3.1.0", # Excel file support
    "pyarrow>=13.0.0",  # Parquet file support
    
    # Development utilities
    "python-dotenv>=1.0.0", # Environment variable management
]

# Optional dependencies for enhanced features
extras_require = {
    # Development tools
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "mypy>=1.5.0",
        "pre-commit>=3.0.0",
    ],
    
    # Documentation
    "docs": [
        "mkdocs>=1.5.0",
        "mkdocs-material>=9.0.0",
        "mkdocstrings[python]>=0.23.0",
    ],
    
    # Database connectivity
    "databases": [
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",  # PostgreSQL
        "pymysql>=1.1.0",          # MySQL
        "sqlite3",                 # SQLite (built-in)
    ],
    
    # Machine learning integration
    "ml": [
        "scikit-learn>=1.3.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
    ],
    
    # Geospatial analysis
    "geo": [
        "geopandas>=0.14.0",
        "folium>=0.14.0",
        "shapely>=2.0.0",
    ],
    
    # Performance enhancements
    "performance": [
        "polars>=0.19.0",  # Fast DataFrame library
        "duckdb>=0.9.0",   # Fast analytical database
    ],
    
    # All optional dependencies
    "all": [
        # Flatten all extras
        "pytest>=7.0.0", "pytest-cov>=4.0.0", "black>=23.0.0",
        "isort>=5.12.0", "flake8>=6.0.0", "mypy>=1.5.0",
        "mkdocs>=1.5.0", "mkdocs-material>=9.0.0",
        "sqlalchemy>=2.0.0", "psycopg2-binary>=2.9.0",
        "scikit-learn>=1.3.0", "matplotlib>=3.7.0",
        "geopandas>=0.14.0", "folium>=0.14.0",
        "polars>=0.19.0", "duckdb>=0.9.0",
    ]
}

setup(
    # Basic package information
    name="vizora",
    version=version,
    author="Pedro Ramirez", 
    author_email="pedro@vizora.dev",
    description="🚀 Interactive Data Visualization Platform - Create stunning dashboards with Python + Svelte + DeckGL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rampedro/vizora",
    project_urls={
        "Documentation": "https://vizora.dev/docs",
        "Source Code": "https://github.com/rampedro/vizora",
        "Issue Tracker": "https://github.com/rampedro/vizora/issues",
        "Examples": "https://vizora.dev/examples",
        "Community": "https://vizora.dev/community",
    },
    
    # Package discovery and structure
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
    package_data={
        "vizora": [
            "templates/**/*",
            "frontend/**/*",
            "data/**/*",
        ]
    },
    include_package_data=True,
    
    # Dependencies
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    
    # Entry points - this makes the CLI available
    entry_points={
        "console_scripts": [
            "vizora=vizora.cli.main:cli",
        ],
    },
    
    # Package classification
    classifiers=[
        # Development Status
        "Development Status :: 4 - Beta",
        
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Data Scientists", 
        "Intended Audience :: Science/Research",
        "Intended Audience :: Financial and Insurance Industry",
        
        # Topic
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Programming Language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        
        # Operating System
        "Operating System :: OS Independent",
        
        # Framework
        "Framework :: FastAPI",
    ],
    
    # Keywords for discoverability
    keywords=[
        "data-visualization", "dashboard", "analytics", "charts", 
        "maps", "3d-visualization", "deckgl", "d3", "svelte",
        "fastapi", "interactive", "web-app", "business-intelligence",
        "data-science", "geospatial", "webgl", "real-time"
    ],
    
    # Zip safety
    zip_safe=False,
    
    # Additional metadata
    license="MIT",
    platforms=["any"],
)