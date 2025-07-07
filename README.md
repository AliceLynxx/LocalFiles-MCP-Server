# LocalFiles MCP Server

A simple Model Context Protocol (MCP) server that provides secure access to local files from specified directories.

## Features

- 🔒 **Secure Access**: Only allows access to explicitly configured directories
- 📁 **Directory Listing**: List all files in allowed directories with metadata
- 📖 **File Reading**: Read file contents with automatic text/binary detection
- ⚙️ **Configurable**: Easy configuration via environment variables or .env file
- 🛡️ **Safety Features**: File size limits and extension filtering

## Installation

1. Clone this repository:
```bash
git clone https://github.com/AliceLynxx/LocalFiles-MCP-Server.git
cd LocalFiles-MCP-Server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create configuration file:
```bash
cp .env.example .env
```

4. Edit `.env` file to configure your allowed directories:
```env
ALLOWED_DIRECTORIES=/home/user/documents,/home/user/projects
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=.txt,.md,.py,.js,.json,.yaml,.yml,.csv,.xml,.html,.css
```

## Usage

### Running the Server

```bash
python app.py
```

### Available Tools

The MCP server provides three tools:

#### 1. `list_files`
Lists all files in allowed directories or a specific directory.

**Parameters:**
- `directory_path` (optional): Specific directory to list

**Example:**
```python
# List all files in all allowed directories
result = list_files()

# List files in specific directory
result = list_files("/path/to/specific/directory")
```

#### 2. `read_file`
Reads the contents of a specific file.

**Parameters:**
- `file_path`: Path to the file to read

**Example:**
```python
result = read_file("/path/to/your/file.txt")
```

#### 3. `get_config`
Returns current server configuration.

**Example:**
```python
config = get_config()
```

## Configuration

### Environment Variables

- `ALLOWED_DIRECTORIES`: Comma-separated list of directories the server can access
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 10MB)
- `ALLOWED_EXTENSIONS`: Comma-separated list of allowed file extensions

### Security Features

- **Directory Restriction**: Only files within explicitly allowed directories can be accessed
- **File Size Limits**: Prevents reading of excessively large files
- **Extension Filtering**: Optionally restrict access to specific file types
- **Path Traversal Protection**: Prevents access outside allowed directories

## Example Response Formats

### list_files Response
```json
{
  "allowed_directories": ["/home/user/documents"],
  "directories": [
    {
      "directory": "/home/user/documents",
      "files": [
        {
          "name": "example.txt",
          "path": "/home/user/documents/example.txt",
          "relative_path": "example.txt",
          "size": 1024,
          "modified": 1704067200.0,
          "extension": ".txt"
        }
      ],
      "total_files": 1
    }
  ],
  "total_directories": 1
}
```

### read_file Response
```json
{
  "file_path": "/home/user/documents/example.txt",
  "name": "example.txt",
  "size": 1024,
  "modified": 1704067200.0,
  "extension": ".txt",
  "content_type": "text",
  "content": "File contents here..."
}
```

## License

MIT License - see LICENSE file for details.