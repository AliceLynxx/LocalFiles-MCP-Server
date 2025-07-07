# LocalFiles MCP Server

A Model Context Protocol (MCP) server that provides secure access to local files from specified directories.

## Features

- List files in configured directories
- Read file contents (text and binary)
- File size and extension filtering
- Secure path validation
- Configuration via .env file or environment variables

## Configuration

### Method 1: .env file (Recommended)

Create a `.env` file in the same directory as `app.py`:

```env
# Comma-separated list of allowed directories
ALLOWED_DIRECTORIES=/home/user/documents,/home/user/projects,/path/to/your/files

# Maximum file size in bytes (default: 10MB)
MAX_FILE_SIZE=10485760

# Allowed file extensions (comma-separated)
ALLOWED_EXTENSIONS=.txt,.md,.py,.js,.json,.yaml,.yml,.csv,.xml,.html,.css
```

### Method 2: Environment Variables

Set environment variables directly:

```bash
export ALLOWED_DIRECTORIES="/home/user/documents,/home/user/projects"
export MAX_FILE_SIZE=10485760
export ALLOWED_EXTENSIONS=".txt,.md,.py,.js,.json,.yaml,.yml,.csv,.xml,.html,.css"
```

## Usage

### Start the server

```bash
python app.py
```

### Available Tools

1. **lf_list_files** - List files in allowed directories
2. **lf_read_file** - Read contents of a specific file
3. **lf_get_config** - Get current server configuration

## Security

- Only files within configured `ALLOWED_DIRECTORIES` can be accessed
- File size limits prevent reading overly large files
- File extension filtering restricts access to specified file types
- All paths are resolved and validated to prevent directory traversal attacks

## Troubleshooting

### "No allowed directories configured" error

This error occurs when:

1. **No .env file exists** - Create a `.env` file with `ALLOWED_DIRECTORIES` setting
2. **Empty ALLOWED_DIRECTORIES** - Ensure the value is not empty
3. **Wrong working directory** - The server looks for `.env` in the script directory first, then current directory
4. **Environment variables not set** - If not using .env, ensure environment variables are properly set

### Debug configuration

Use the `lf_get_config` tool to check what configuration the server is actually using:

```python
# This will show the current configuration
lf_get_config()
```

## Example .env file

```env
# Example configuration for a development environment
ALLOWED_DIRECTORIES=/home/alice/projects,/home/alice/documents,/tmp/safe-files
MAX_FILE_SIZE=52428800
ALLOWED_EXTENSIONS=.txt,.md,.py,.js,.json,.yaml,.yml,.csv,.xml,.html,.css,.log
```

## Requirements

- Python 3.7+
- fastmcp library
- pathlib (built-in)

## Installation

```bash
pip install fastmcp
```