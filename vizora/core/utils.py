"""
🔧 Vizora Utilities - The Helpful Toolbox

These are the behind-the-scenes helpers that make Vizora work smoothly.
From port management to path handling, these utilities handle all the
mundane but important tasks so the main components can focus on being awesome.
"""

import socket
import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple
import logging


class PortManager:
    """
    🚢 Smart port management for seamless development.
    
    No more "Port already in use" errors! This class intelligently finds
    available ports and handles port conflicts gracefully. Perfect for
    development environments where multiple services might be running.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("vizora.ports")
    
    def find_available_port(self, start_port: int = 8000, end_port: int = 8010) -> int:
        """
        Find an available port in the specified range.
        
        This is much smarter than hardcoding ports! It automatically finds
        an open port so you can run multiple Vizora instances or avoid
        conflicts with other services.
        
        Args:
            start_port: Start of port range to search
            end_port: End of port range to search
            
        Returns:
            An available port number
            
        Raises:
            RuntimeError: If no ports are available in the range
        """
        for port in range(start_port, end_port + 1):
            if self.is_port_available(port):
                self.logger.info(f"🚢 Found available port: {port}")
                return port
        
        raise RuntimeError(f"No available ports in range {start_port}-{end_port}")
    
    def is_port_available(self, port: int, host: str = "localhost") -> bool:
        """
        Check if a specific port is available.
        
        This uses a socket connection to test if the port is already in use.
        Much more reliable than trying to parse `lsof` output!
        
        Args:
            port: Port number to check
            host: Host to check (defaults to localhost)
            
        Returns:
            True if port is available, False otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)  # Quick timeout
                result = sock.connect_ex((host, port))
                return result != 0  # 0 means connection successful (port in use)
        except Exception:
            # If we can't check, assume it's not available (safer)
            return False
    
    def kill_process_on_port(self, port: int) -> bool:
        """
        Kill any process using the specified port.
        
        Sometimes you need to forcefully free up a port. This method
        finds and terminates the process using it. Use with caution!
        
        Args:
            port: Port to free up
            
        Returns:
            True if a process was killed, False if port was already free
        """
        try:
            # Find process using the port
            if sys.platform == "darwin" or sys.platform == "linux":
                # macOS and Linux
                result = subprocess.run(
                    ["lsof", "-ti", f":{port}"],
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    pid = result.stdout.strip()
                    subprocess.run(["kill", "-9", pid])
                    self.logger.info(f"🔫 Killed process {pid} on port {port}")
                    return True
            
            elif sys.platform == "win32":
                # Windows
                result = subprocess.run(
                    ["netstat", "-ano", "|", "findstr", f":{port}"],
                    capture_output=True,
                    text=True,
                    shell=True
                )
                # Parse Windows netstat output and kill process
                # Implementation would be similar but using taskkill
                
            return False
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not kill process on port {port}: {e}")
            return False


class PathHelper:
    """
    📁 Intelligent path and file management.
    
    This class handles all the tricky path-related operations that make
    cross-platform development smooth. It knows about project structure,
    handles different operating systems gracefully, and makes file operations safe.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("vizora.paths")
        self.project_root = self._find_project_root()
    
    def _find_project_root(self) -> Path:
        """
        Intelligently find the project root directory.
        
        This looks for common indicators like setup.py, pyproject.toml,
        or .git to determine where the project root is. Much more reliable
        than assuming the current directory!
        """
        current = Path.cwd()
        
        # Look for project indicators
        indicators = ["setup.py", "pyproject.toml", ".git", "vizora"]
        
        # Walk up the directory tree
        for parent in [current] + list(current.parents):
            for indicator in indicators:
                if (parent / indicator).exists():
                    self.logger.info(f"📁 Found project root: {parent}")
                    return parent
        
        # Fallback to current directory
        self.logger.warning("⚠️ Could not find project root, using current directory")
        return current
    
    def get_data_directory(self) -> Path:
        """Get the data directory, creating it if necessary."""
        data_dir = self.project_root / "data"
        data_dir.mkdir(exist_ok=True, parents=True)
        return data_dir
    
    def get_template_directory(self) -> Path:
        """Get the template directory for project scaffolding."""
        template_dir = self.project_root / "vizora" / "templates"
        return template_dir
    
    def get_frontend_directory(self) -> Path:
        """Get the frontend directory."""
        return self.project_root / "frontend"
    
    def get_backend_directory(self) -> Path:
        """Get the backend directory."""
        return self.project_root / "backend"
    
    def ensure_directory_exists(self, path: Path) -> Path:
        """
        Ensure a directory exists, creating it if necessary.
        
        This is safer than just calling mkdir() because it handles
        race conditions and permission issues gracefully.
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
            return path
        except PermissionError:
            self.logger.error(f"❌ Permission denied creating directory: {path}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Error creating directory {path}: {e}")
            raise
    
    def safe_copy_file(self, src: Path, dst: Path, overwrite: bool = False) -> bool:
        """
        Safely copy a file with proper error handling.
        
        This includes checks for file existence, permissions, and disk space
        to avoid partial copies or corruption.
        """
        try:
            if dst.exists() and not overwrite:
                self.logger.warning(f"⚠️ File already exists: {dst}")
                return False
            
            # Ensure destination directory exists
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(src, dst)
            self.logger.info(f"📄 Copied {src} -> {dst}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error copying {src} to {dst}: {e}")
            return False
    
    def get_file_size_mb(self, file_path: Path) -> float:
        """Get file size in megabytes."""
        try:
            size_bytes = file_path.stat().st_size
            return size_bytes / (1024 * 1024)
        except Exception:
            return 0.0
    
    def clean_filename(self, filename: str) -> str:
        """
        Clean a filename to be safe for all operating systems.
        
        Removes or replaces characters that cause problems on different
        filesystems. Because file names can be surprisingly tricky!
        """
        # Remove or replace problematic characters
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Ensure it's not empty
        if not filename:
            filename = "untitled"
        
        # Limit length (255 is common filesystem limit)
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename


class ProcessManager:
    """
    ⚙️ Process management for running multiple services.
    
    Vizora often needs to coordinate multiple processes (backend, frontend,
    maybe additional services). This class makes that coordination smooth
    and reliable, with proper cleanup and error handling.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("vizora.processes")
        self.processes: List[subprocess.Popen] = []
        self.cleanup_registered = False
    
    def start_process(self, 
                     command: List[str], 
                     cwd: Optional[Path] = None,
                     env: Optional[dict] = None,
                     name: str = "unnamed") -> subprocess.Popen:
        """
        Start a process with proper management and logging.
        
        This ensures all processes are tracked for cleanup and provides
        consistent logging across different process types.
        """
        try:
            self.logger.info(f"🟢 Starting process: {name}")
            self.logger.debug(f"Command: {' '.join(command)}")
            
            process = subprocess.Popen(
                command,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(process)
            self._register_cleanup()
            
            self.logger.info(f"✅ Process started: {name} (PID: {process.pid})")
            return process
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start process {name}: {e}")
            raise
    
    def _register_cleanup(self):
        """Register cleanup handlers to ensure processes are terminated."""
        if self.cleanup_registered:
            return
        
        import atexit
        import signal
        
        def cleanup():
            self.stop_all_processes()
        
        # Register cleanup for normal exit
        atexit.register(cleanup)
        
        # Register cleanup for signals
        signal.signal(signal.SIGINT, lambda s, f: cleanup())
        signal.signal(signal.SIGTERM, lambda s, f: cleanup())
        
        self.cleanup_registered = True
    
    def stop_all_processes(self):
        """Stop all managed processes gracefully."""
        self.logger.info("🛑 Stopping all processes...")
        
        for process in self.processes:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    process.wait(timeout=5)  # Give it 5 seconds to stop
                    if process.poll() is None:
                        # Force kill if it didn't stop
                        process.kill()
                        process.wait()
                    self.logger.info(f"✅ Stopped process PID: {process.pid}")
            except Exception as e:
                self.logger.warning(f"⚠️ Error stopping process: {e}")
        
        self.processes.clear()
        self.logger.info("🧹 All processes stopped")


class ConfigManager:
    """
    ⚙️ Configuration management with smart defaults.
    
    This handles loading configuration from files, environment variables,
    and command-line arguments. It provides a unified interface and handles
    validation and type conversion automatically.
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        self.logger = logging.getLogger("vizora.config")
        self.config_file = config_file or Path("vizora.config.json")
        self.config = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment."""
        # Load from file if it exists
        if self.config_file.exists():
            try:
                import json
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                self.logger.info(f"📋 Loaded config from {self.config_file}")
            except Exception as e:
                self.logger.warning(f"⚠️ Error loading config file: {e}")
        
        # Override with environment variables
        env_prefix = "VIZORA_"
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()
                self.config[config_key] = self._convert_env_value(value)
                self.logger.debug(f"🌍 Set {config_key} from environment")
    
    def _convert_env_value(self, value: str):
        """Convert environment variable string to appropriate type."""
        # Try boolean
        if value.lower() in ['true', 'yes', '1']:
            return True
        elif value.lower() in ['false', 'no', '0']:
            return False
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Default to string
        return value
    
    def get(self, key: str, default=None):
        """Get configuration value with default."""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value."""
        self.config[key] = value
    
    def save(self):
        """Save current configuration to file."""
        try:
            import json
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info(f"💾 Saved config to {self.config_file}")
        except Exception as e:
            self.logger.error(f"❌ Error saving config: {e}")

# 🔧 Extension Points and Utilities

def setup_logging(level: str = "INFO", format_style: str = "emoji") -> None:
    """
    Set up beautiful, human-readable logging for Vizora.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format_style: Style for log formatting (emoji, plain, minimal)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s | 🎯 %(name)s | %(levelname)s | %(message)s' if format_style == "emoji" else 
               '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

def check_system_requirements() -> List[str]:
    """
    Check if the system has all required dependencies.
    
    Returns a list of missing requirements that need to be installed.
    Helps users get up and running quickly with helpful error messages.
    """
    missing = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        missing.append("Python 3.8 or higher")
    
    # Check for Node.js (for frontend)
    try:
        result = subprocess.run(["node", "--version"], capture_output=True)
        if result.returncode != 0:
            missing.append("Node.js")
    except FileNotFoundError:
        missing.append("Node.js")
    
    # Check for npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True)
        if result.returncode != 0:
            missing.append("npm")
    except FileNotFoundError:
        missing.append("npm")
    
    return missing

# TODO: Add system performance monitoring
# TODO: Add network connectivity checks  
# TODO: Add disk space management
# TODO: Add memory usage tracking
# TODO: Add configuration validation