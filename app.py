#!/usr/bin/env python3
"""
LocalFiles MCP Server

A simple Model Context Protocol server that provides access to local files
from directories specified in the environment configuration.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("LocalFiles-MCP-Server")

def load_config() -> Dict[str, Any]:
    """Load configuration from .env file or environment variables."""
    config = {
        'allowed_directories': [],
        'max_file_size': 10 * 1024 * 1024,  # 10MB default
        'allowed_extensions': ['.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml', '.csv', '.xml', '.html', '.css']
    }
    
    # Try to load from .env file
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        
                        if key == 'ALLOWED_DIRECTORIES':
                            # Support comma-separated directories
                            config['allowed_directories'] = [d.strip() for d in value.split(',') if d.strip()]
                        elif key == 'MAX_FILE_SIZE':
                            config['max_file_size'] = int(value)
                        elif key == 'ALLOWED_EXTENSIONS':
                            config['allowed_extensions'] = [ext.strip() for ext in value.split(',') if ext.strip()]
    
    # Override with environment variables if present
    if os.getenv('ALLOWED_DIRECTORIES'):
        config['allowed_directories'] = [d.strip() for d in os.getenv('ALLOWED_DIRECTORIES').split(',') if d.strip()]
    
    if os.getenv('MAX_FILE_SIZE'):
        config['max_file_size'] = int(os.getenv('MAX_FILE_SIZE'))
    
    if os.getenv('ALLOWED_EXTENSIONS'):
        config['allowed_extensions'] = [ext.strip() for ext in os.getenv('ALLOWED_EXTENSIONS').split(',') if ext.strip()]
    
    return config

def is_file_allowed(file_path: Path, config: Dict[str, Any]) -> bool:
    """Check if a file is allowed to be accessed."""
    # Check file size
    try:
        if file_path.stat().st_size > config['max_file_size']:
            return False
    except OSError:
        return False
    
    # Check file extension
    if config['allowed_extensions'] and file_path.suffix.lower() not in config['allowed_extensions']:
        return False
    
    return True

def is_path_allowed(file_path: str, config: Dict[str, Any]) -> bool:
    """Check if a path is within allowed directories."""
    file_path = Path(file_path).resolve()
    
    for allowed_dir in config['allowed_directories']:
        allowed_path = Path(allowed_dir).resolve()
        try:
            file_path.relative_to(allowed_path)
            return True
        except ValueError:
            continue
    
    return False

@mcp.tool()
def lf_list_files(directory_path: str = "") -> Dict[str, Any]:
    """List all files in the specified directory or all allowed directories.
    
    Args:
        directory_path: Optional specific directory to list. If empty, lists all allowed directories.
    
    Returns:
        Dictionary containing the list of files with their metadata.
    """
    config = load_config()
    
    if not config['allowed_directories']:
        return {"error": "No allowed directories configured. Please set ALLOWED_DIRECTORIES in .env file."}
    
    files_info = []
    
    if directory_path:
        # List specific directory
        if not is_path_allowed(directory_path, config):
            return {"error": f"Directory '{directory_path}' is not in allowed directories."}
        
        directories_to_scan = [directory_path]
    else:
        # List all allowed directories
        directories_to_scan = config['allowed_directories']
    
    for dir_path in directories_to_scan:
        try:
            path = Path(dir_path)
            if not path.exists():
                files_info.append({"directory": dir_path, "error": "Directory does not exist"})
                continue
            
            if not path.is_dir():
                files_info.append({"directory": dir_path, "error": "Path is not a directory"})
                continue
            
            dir_files = []
            for file_path in path.rglob('*'):
                if file_path.is_file() and is_file_allowed(file_path, config):
                    try:
                        stat = file_path.stat()
                        dir_files.append({
                            "name": file_path.name,
                            "path": str(file_path),
                            "relative_path": str(file_path.relative_to(path)),
                            "size": stat.st_size,
                            "modified": stat.st_mtime,
                            "extension": file_path.suffix
                        })
                    except OSError as e:
                        continue
            
            files_info.append({
                "directory": dir_path,
                "files": dir_files,
                "total_files": len(dir_files)
            })
            
        except Exception as e:
            files_info.append({"directory": dir_path, "error": str(e)})
    
    return {
        "allowed_directories": config['allowed_directories'],
        "directories": files_info,
        "total_directories": len(files_info)
    }

@mcp.tool()
def lf_read_file(file_path: str) -> Dict[str, Any]:
    """Read the contents of a specific file.
    
    Args:
        file_path: Path to the file to read.
    
    Returns:
        Dictionary containing the file contents and metadata.
    """
    config = load_config()
    
    if not config['allowed_directories']:
        return {"error": "No allowed directories configured. Please set ALLOWED_DIRECTORIES in .env file."}
    
    if not is_path_allowed(file_path, config):
        return {"error": f"File '{file_path}' is not in allowed directories."}
    
    try:
        path = Path(file_path)
        
        if not path.exists():
            return {"error": "File does not exist."}
        
        if not path.is_file():
            return {"error": "Path is not a file."}
        
        if not is_file_allowed(path, config):
            return {"error": "File is not allowed (size or extension restrictions)."}
        
        # Try to read as text first
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            content_type = "text"
        except UnicodeDecodeError:
            # If text reading fails, read as binary and encode as base64
            import base64
            with open(path, 'rb') as f:
                content = base64.b64encode(f.read()).decode('ascii')
            content_type = "binary_base64"
        
        stat = path.stat()
        
        return {
            "file_path": str(path),
            "name": path.name,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "extension": path.suffix,
            "content_type": content_type,
            "content": content
        }
        
    except Exception as e:
        return {"error": f"Error reading file: {str(e)}"}

@mcp.tool()
def lf_get_config() -> Dict[str, Any]:
    """Get current server configuration.
    
    Returns:
        Dictionary containing current configuration settings.
    """
    config = load_config()
    return {
        "allowed_directories": config['allowed_directories'],
        "max_file_size": config['max_file_size'],
        "allowed_extensions": config['allowed_extensions'],
        "status": "configured" if config['allowed_directories'] else "not_configured"
    }

if __name__ == "__main__":
    print("Starting LocalFiles MCP Server...")
    config = load_config()
    
    if not config['allowed_directories']:
        print("WARNING: No allowed directories configured!")
        print("Please create a .env file with ALLOWED_DIRECTORIES setting.")
        print("Example: ALLOWED_DIRECTORIES=/path/to/dir1,/path/to/dir2")
    else:
        print(f"Allowed directories: {config['allowed_directories']}")
    
    mcp.run()