# Call Graph Explorer

A powerful web-based UI and CLI tool for visualizing and analyzing function call graphs. Explore relationships between functions in your codebase with an intuitive interface.

## ✨ Features

- 🔍 **Function Search** - Search functions by name with instant results
- 📊 **Call Relationships** - View caller-callee relationships in clean tables
- 📈 **Depth Analysis** - Analyze call graph depth and function distribution
- 🎯 **Interactive Web UI** - Streamlit-based interface for easy exploration
- 💻 **CLI Tools** - Command-line interface for data loading and queries
- 💾 **LadyBugDB** - Custom database for efficient storage

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd callgraph-ui
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate on Windows
   .venv\Scripts\activate

   # Activate on Linux/Mac
   source .venv/bin/activate
   ```

3. **Install the package**
   ```bash
   pip install -e .
   ```

### Running the Application

1. **Initialize database**
   ```bash
   callgraph init-db --db-path test_callgraph.db
   ```

2. **Load sample data**
   ```bash
   callgraph load-json data/sample_callgraph.json --db-path test_callgraph.db --root main
   ```

3. **Launch web interface**
   ```bash
   streamlit run callgraph/ui/app.py --server.port 8506
   ```

4. **Open browser** → http://localhost:8506

## 📖 Usage Guide

### Web Interface

The web UI provides three main sections:

1. **Search Functions**
   - Type a function name in the search box
   - Click 🔍 to search
   - View results in the Call Relationships Table

2. **Configuration Table**
   - Shows call depth statistics
   - Select depth level to analyze
   - Configure number of functions to display

3. **Results Table**
   - Displays caller-callee relationships at selected depth
   - Shows file locations for each function

### CLI Commands

#### Initialize Database
```bash
callgraph init-db --db-path <path>
```

#### Validate JSON
```bash
callgraph validate-json <json-file>
```

#### Load Data
```bash
callgraph load-json <json-file> --db-path <db-path> --root <root-function>
```

Example:
```bash
callgraph load-json data/sample_callgraph.json --db-path test_callgraph.db --root main
```

#### Query Commands

**List all functions:**
```bash
callgraph query functions --db-path test_callgraph.db
```

**Get function callees:**
```bash
callgraph query callees --function main --db-path test_callgraph.db
```

**Get function callers:**
```bash
callgraph query callers --function bar --db-path test_callgraph.db
```

**View function details:**
```bash
callgraph query detail --function main --db-path test_callgraph.db
```

**Show depth summary:**
```bash
callgraph query depth-summary --root main --db-path test_callgraph.db
```

**Show edges at depth:**
```bash
callgraph query edges-at-depth --root main --depth 1 --db-path test_callgraph.db
```

## 📁 Project Structure

```
callgraph-ui/
├── callgraph/
│   ├── cli.py                 # CLI commands
│   ├── config/                # Configuration
│   ├── loader/                # Database operations
│   │   ├── db.py             # Database manager
│   │   └── writer.py         # Data writer
│   ├── model/                 # Data models
│   ├── queries/               # Query functions
│   ├── schema/                # Database schema
│   ├── ui/                    # Web interface
│   │   ├── app.py            # Main app
│   │   └── components/       # UI components
│   └── validate/              # Validation
├── data/                      # Sample data
├── ladybugdb.py              # Database implementation
└── pyproject.toml            # Project config
```

## 📝 JSON Format

The tool expects JSON with this structure:

```json
{
  "functions": [
    {
      "id": "1",
      "name": "main",
      "file": "main.c",
      "signature": "int main()"
    }
  ],
  "callsites": [
    {
      "id": "1",
      "caller_function_id": "1",
      "callee_function_id": "2",
      "file": "main.c",
      "line": 10
    }
  ],
  "edges": [
    {
      "id": "1",
      "caller_function_id": "1",
      "callee_function_id": "2",
      "callsite_id": "1"
    }
  ]
}
```

## ⚙️ Configuration

Configure database path via:
- `--db-path` command option
- `CALLGRAPH_DB_PATH` environment variable
- Default: `test_callgraph.db`

## 🔧 Development

### Install development dependencies
```bash
pip install -e ".[dev]"
```

### Run tests
```bash
pytest tests/
```

## 🐛 Troubleshooting

**"Database file not found"**
- Run `callgraph init-db` first
- Check database path in sidebar

**"No functions found"**
- Load data using `callgraph load-json`
- Validate JSON with `callgraph validate-json`

**Search returns no results**
- Search by function **name** (e.g., `main`, `foo`)
- Search is case-insensitive
- Supports partial matches

## 📄 License

See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please submit a Pull Request.
