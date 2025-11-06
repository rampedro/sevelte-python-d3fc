"""
🖥️ Vizora CLI - Your Command-Line Companion

The Vizora CLI makes it incredibly easy to get started with new projects,
manage existing ones, and discover what's possible. It's designed to be
intuitive and helpful - like having a data visualization expert right
in your terminal!
"""

import click
import sys
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
import subprocess
import time

from ..core.utils import PortManager, PathHelper, check_system_requirements
from ..core.dashboard import VizoraDashboard, DashboardConfig
from ..plugins.base_plugin import PluginManager
from .. import show_banner, get_version


@click.group()
@click.version_option(version=get_version(), prog_name="Vizora")
def cli():
    """
    🚀 Vizora - Interactive Data Visualization Platform
    
    Create stunning, interactive dashboards with just a few commands!
    Perfect for data scientists, analysts, and anyone who wants to
    turn data into beautiful, meaningful visualizations.
    """
    pass


@cli.command()
@click.argument('project_name')
@click.option('--template', '-t', default='basic', 
              help='Project template to use (basic, advanced, geo, finance)')
@click.option('--directory', '-d', default=None,
              help='Directory to create project in (defaults to current directory)')
@click.option('--with-sample-data', is_flag=True,
              help='Include sample datasets for quick experimentation')
def init(project_name: str, template: str, directory: Optional[str], with_sample_data: bool):
    """
    🏗️ Initialize a new Vizora project with intelligent scaffolding.
    
    This creates a complete project structure with everything you need
    to start creating amazing visualizations immediately!
    
    Examples:
        vizora init my-dashboard
        vizora init sales-analytics --template finance --with-sample-data
        vizora init geo-viz --template geo -d ./projects/
    """
    show_banner()
    click.echo(f"🏗️ Creating new Vizora project: {project_name}")
    
    # Determine project directory
    if directory:
        project_dir = Path(directory) / project_name
    else:
        project_dir = Path.cwd() / project_name
    
    if project_dir.exists():
        if not click.confirm(f"Directory {project_dir} already exists. Continue?"):
            click.echo("❌ Project creation cancelled")
            return
    
    try:
        # Create project structure
        _create_project_structure(project_dir, template)
        
        # Add sample data if requested
        if with_sample_data:
            _add_sample_data(project_dir, template)
        
        # Create configuration file
        _create_project_config(project_dir, project_name, template)
        
        # Initialize git repository
        _init_git_repo(project_dir)
        
        click.echo("✅ Project created successfully!")
        click.echo(f"📁 Location: {project_dir}")
        click.echo("\n🚀 Quick start:")
        click.echo(f"   cd {project_name}")
        click.echo("   vizora run")
        click.echo("\n📚 Learn more: https://vizora.dev/docs")
        
    except Exception as e:
        click.echo(f"❌ Error creating project: {e}")
        sys.exit(1)


@cli.command()
@click.option('--port', '-p', type=int, help='Port to run on (auto-detected if not specified)')
@click.option('--host', '-h', default='localhost', help='Host to bind to')
@click.option('--no-browser', is_flag=True, help='Don\'t automatically open browser')
@click.option('--debug', is_flag=True, help='Enable debug mode with verbose logging')
def run(port: Optional[int], host: str, no_browser: bool, debug: bool):
    """
    🚀 Run your Vizora dashboard with one command.
    
    This starts both the backend API and frontend development server,
    automatically finds available ports, and opens your dashboard
    in the browser. It's like magic!
    
    Examples:
        vizora run                    # Start with auto-detected ports
        vizora run --port 8080        # Start on specific port
        vizora run --debug            # Enable verbose logging
        vizora run --no-browser       # Start without opening browser
    """
    show_banner()
    
    # Check if we're in a Vizora project
    if not _is_vizora_project():
        click.echo("❌ This doesn't appear to be a Vizora project.")
        click.echo("💡 Use 'vizora init <project-name>' to create a new project")
        return
    
    # Check system requirements
    missing_deps = check_system_requirements()
    if missing_deps:
        click.echo("❌ Missing required dependencies:")
        for dep in missing_deps:
            click.echo(f"   - {dep}")
        click.echo("\n📖 See installation guide: https://vizora.dev/docs/installation")
        return
    
    # Load project configuration
    config = _load_project_config()
    
    try:
        # Create and configure dashboard
        dashboard_config = DashboardConfig(
            name=config.get('name', 'Vizora Dashboard'),
            debug=debug,
            backend_port=port,
            host=host
        )
        
        dashboard = VizoraDashboard(config=dashboard_config)
        
        # Load data sources from config
        for data_source in config.get('data_sources', []):
            dashboard.add_data_source(data_source['file'], data_source.get('name'))
        
        # Load visualizations from config
        for viz in config.get('visualizations', []):
            dashboard.add_visualization(viz['type'], **viz.get('config', {}))
        
        # Run the dashboard
        click.echo("🚀 Starting Vizora dashboard...")
        dashboard.run(
            backend_port=port,
            open_browser=not no_browser
        )
        
    except KeyboardInterrupt:
        click.echo("\n🛑 Shutting down gracefully...")
    except Exception as e:
        click.echo(f"❌ Error running dashboard: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('data_file')
@click.option('--name', '-n', help='Name for the dataset (defaults to filename)')
@click.option('--preview', '-p', is_flag=True, help='Preview the data after adding')
def add_data(data_file: str, name: Optional[str], preview: bool):
    """
    📊 Add a data source to your project.
    
    This command adds a new data source to your project configuration
    and validates that it can be loaded correctly.
    
    Examples:
        vizora add-data sales.csv
        vizora add-data financial_data.json --name finance
        vizora add-data population.xlsx --preview
    """
    if not _is_vizora_project():
        click.echo("❌ This doesn't appear to be a Vizora project.")
        return
    
    data_path = Path(data_file)
    if not data_path.exists():
        # Try looking in data directory
        data_path = Path('data') / data_file
        if not data_path.exists():
            click.echo(f"❌ Data file not found: {data_file}")
            return
    
    dataset_name = name or data_path.stem
    
    try:
        # Test loading the data
        from ..core.data_manager import DataManager
        dm = DataManager()
        dm.load_dataset(data_path, dataset_name)
        
        # Update project configuration
        config = _load_project_config()
        if 'data_sources' not in config:
            config['data_sources'] = []
        
        # Check if already exists
        existing = next((ds for ds in config['data_sources'] if ds['name'] == dataset_name), None)
        if existing:
            if not click.confirm(f"Dataset '{dataset_name}' already exists. Update?"):
                return
            existing['file'] = str(data_path)
        else:
            config['data_sources'].append({
                'name': dataset_name,
                'file': str(data_path)
            })
        
        _save_project_config(config)
        
        click.echo(f"✅ Added data source: {dataset_name}")
        click.echo(f"📁 File: {data_path}")
        
        if preview:
            # Show data preview
            data = dm.get_dataset(dataset_name)
            info = dm.get_dataset_info(dataset_name)
            
            click.echo(f"\n📊 Dataset Preview:")
            click.echo(f"   Rows: {info.row_count:,}")
            click.echo(f"   Columns: {info.column_count}")
            click.echo(f"   Size: {info.size_bytes / 1024:.1f} KB")
            
            if data:
                click.echo(f"\n🔍 First few rows:")
                for i, row in enumerate(data[:3]):
                    click.echo(f"   {i+1}: {dict(list(row.items())[:3])}...")
        
    except Exception as e:
        click.echo(f"❌ Error adding data source: {e}")


@cli.command()
@click.argument('viz_type')
@click.option('--data-source', '-d', required=True, help='Data source to visualize')
@click.option('--title', '-t', help='Title for the visualization')
@click.option('--config', '-c', help='JSON configuration string')
def add_viz(viz_type: str, data_source: str, title: Optional[str], config: Optional[str]):
    """
    🎨 Add a visualization to your project.
    
    This creates a new visualization and adds it to your project
    configuration. The visualization will appear in your dashboard
    the next time you run it.
    
    Examples:
        vizora add-viz bar --data-source sales --title "Monthly Sales"
        vizora add-viz map --data-source cities --config '{"center_lat": 40, "center_lng": -74}'
        vizora add-viz deckgl_overlay --data-source locations --title "3D City View"
    """
    if not _is_vizora_project():
        click.echo("❌ This doesn't appear to be a Vizora project.")
        return
    
    # Parse config if provided
    viz_config = {}
    if config:
        try:
            viz_config = json.loads(config)
        except json.JSONDecodeError:
            click.echo("❌ Invalid JSON configuration")
            return
    
    # Add title if provided
    if title:
        viz_config['title'] = title
    
    viz_config['data_source'] = data_source
    
    try:
        # Update project configuration
        project_config = _load_project_config()
        if 'visualizations' not in project_config:
            project_config['visualizations'] = []
        
        project_config['visualizations'].append({
            'type': viz_type,
            'config': viz_config
        })
        
        _save_project_config(project_config)
        
        click.echo(f"✅ Added {viz_type} visualization")
        click.echo(f"📊 Data source: {data_source}")
        if title:
            click.echo(f"📝 Title: {title}")
        
    except Exception as e:
        click.echo(f"❌ Error adding visualization: {e}")


@cli.command()
def status():
    """
    📋 Show status of your Vizora project.
    
    This displays information about your project configuration,
    data sources, visualizations, and system requirements.
    Perfect for debugging or getting an overview.
    """
    if not _is_vizora_project():
        click.echo("❌ This doesn't appear to be a Vizora project.")
        click.echo("💡 Use 'vizora init <project-name>' to create a new project")
        return
    
    show_banner()
    
    # Load project configuration
    config = _load_project_config()
    
    click.echo(f"📊 Project: {config.get('name', 'Unnamed')}")
    click.echo(f"📁 Directory: {Path.cwd()}")
    click.echo(f"🎨 Template: {config.get('template', 'unknown')}")
    
    # Data sources
    data_sources = config.get('data_sources', [])
    click.echo(f"\n📈 Data Sources ({len(data_sources)}):")
    if data_sources:
        for ds in data_sources:
            file_path = Path(ds['file'])
            status = "✅" if file_path.exists() else "❌"
            click.echo(f"   {status} {ds['name']} ({ds['file']})")
    else:
        click.echo("   None configured")
    
    # Visualizations
    visualizations = config.get('visualizations', [])
    click.echo(f"\n🎨 Visualizations ({len(visualizations)}):")
    if visualizations:
        for viz in visualizations:
            title = viz.get('config', {}).get('title', 'Untitled')
            click.echo(f"   📊 {viz['type']}: {title}")
    else:
        click.echo("   None configured")
    
    # System requirements
    missing_deps = check_system_requirements()
    click.echo(f"\n🔧 System Requirements:")
    if missing_deps:
        click.echo("   ❌ Missing dependencies:")
        for dep in missing_deps:
            click.echo(f"      - {dep}")
    else:
        click.echo("   ✅ All requirements satisfied")
    
    # Port availability
    port_manager = PortManager()
    backend_port = port_manager.find_available_port(8000, 8010)
    frontend_port = port_manager.find_available_port(5174, 5184)
    click.echo(f"\n🚢 Available Ports:")
    click.echo(f"   Backend: {backend_port}")
    click.echo(f"   Frontend: {frontend_port}")


@cli.command()
def plugins():
    """
    🧩 Manage Vizora plugins.
    
    List available plugins, show plugin information, and manage
    your plugin ecosystem.
    """
    click.echo("🧩 Vizora Plugin Manager")
    
    plugin_manager = PluginManager()
    discovered = plugin_manager.discover_plugins()
    loaded = plugin_manager.list_plugins()
    
    click.echo(f"\n📦 Discovered Plugins ({len(discovered)}):")
    for plugin_path in discovered:
        click.echo(f"   📄 {plugin_path}")
    
    click.echo(f"\n🔌 Loaded Plugins ({len(loaded)}):")
    for name, metadata in loaded.items():
        click.echo(f"   ✅ {name} v{metadata.version} - {metadata.description}")


# Helper functions

def _create_project_structure(project_dir: Path, template: str) -> None:
    """Create the basic project structure."""
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create directories
    (project_dir / "data").mkdir(exist_ok=True)
    (project_dir / "plugins").mkdir(exist_ok=True)
    (project_dir / "templates").mkdir(exist_ok=True)
    
    # Copy template files based on template type
    template_source = Path(__file__).parent.parent / "templates" / template
    if template_source.exists():
        for item in template_source.iterdir():
            if item.is_file():
                shutil.copy2(item, project_dir / item.name)
            elif item.is_dir():
                shutil.copytree(item, project_dir / item.name, dirs_exist_ok=True)
    
    # Create basic files if template doesn't exist
    else:
        _create_basic_files(project_dir)


def _create_basic_files(project_dir: Path) -> None:
    """Create basic project files."""
    # README
    readme_content = f"""# {project_dir.name}

A Vizora data visualization project.

## Quick Start

```bash
# Install dependencies
pip install vizora

# Run the dashboard
vizora run
```

## Adding Data

```bash
vizora add-data your_data.csv
vizora add-viz bar --data-source your_data --title "Your Chart"
```

## Learn More

- [Vizora Documentation](https://vizora.dev/docs)
- [Examples](https://vizora.dev/examples)
- [Community](https://vizora.dev/community)
"""
    (project_dir / "README.md").write_text(readme_content)
    
    # .gitignore
    gitignore_content = """# Vizora
.vizora/
*.log

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Node.js
node_modules/
npm-debug.log*

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    (project_dir / ".gitignore").write_text(gitignore_content)


def _add_sample_data(project_dir: Path, template: str) -> None:
    """Add sample data based on template type."""
    data_dir = project_dir / "data"
    
    # Sample data based on template
    if template == "finance":
        # Create sample financial data
        sample_data = [
            {"date": "2024-01-01", "price": 100.0, "volume": 1000},
            {"date": "2024-01-02", "price": 102.5, "volume": 1200},
            {"date": "2024-01-03", "price": 98.7, "volume": 800},
        ]
    elif template == "geo":
        # Create sample geographic data
        sample_data = [
            {"city": "New York", "lat": 40.7128, "lng": -74.0060, "population": 8000000},
            {"city": "London", "lat": 51.5074, "lng": -0.1278, "population": 9000000},
            {"city": "Tokyo", "lat": 35.6762, "lng": 139.6503, "population": 14000000},
        ]
    else:
        # Basic sample data
        sample_data = [
            {"category": "A", "value": 25, "date": "2024-01-01"},
            {"category": "B", "value": 30, "date": "2024-01-01"},
            {"category": "C", "value": 20, "date": "2024-01-01"},
        ]
    
    # Write sample data as CSV
    import csv
    sample_file = data_dir / "sample_data.csv"
    with open(sample_file, 'w', newline='') as f:
        if sample_data:
            writer = csv.DictWriter(f, fieldnames=sample_data[0].keys())
            writer.writeheader()
            writer.writerows(sample_data)


def _create_project_config(project_dir: Path, project_name: str, template: str) -> None:
    """Create the project configuration file."""
    config = {
        "name": project_name,
        "version": "1.0.0",
        "template": template,
        "data_sources": [],
        "visualizations": [],
        "plugins": [],
        "settings": {
            "theme": "modern",
            "debug": True
        }
    }
    
    config_file = project_dir / "vizora.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)


def _init_git_repo(project_dir: Path) -> None:
    """Initialize a git repository."""
    try:
        subprocess.run(["git", "init"], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial Vizora project"], 
                      cwd=project_dir, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        # Git not available or failed - not critical
        pass


def _is_vizora_project() -> bool:
    """Check if current directory is a Vizora project."""
    return (Path.cwd() / "vizora.json").exists()


def _load_project_config() -> Dict[str, Any]:
    """Load project configuration."""
    config_file = Path.cwd() / "vizora.json"
    if not config_file.exists():
        return {}
    
    with open(config_file, 'r') as f:
        return json.load(f)


def _save_project_config(config: Dict[str, Any]) -> None:
    """Save project configuration."""
    config_file = Path.cwd() / "vizora.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)


if __name__ == "__main__":
    cli()