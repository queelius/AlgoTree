# AlgoTree Integrations

This directory contains **optional integrations** for AlgoTree with external systems and frameworks.

## Why Separate from Core?

1. **Separation of Concerns** - Core AlgoTree functionality vs external adapters
2. **Independent Dependencies** - Each integration may require different packages
3. **Optional Installation** - Users only install what they need
4. **Clear Boundaries** - Makes it obvious what's core vs what's an integration

## Available Integrations (Placeholders)

### MCP (Model Context Protocol)
- **File**: `mcp.py`
- **Purpose**: Enable AI/LLM systems to interact with AlgoTree
- **Status**: Placeholder - implementation pending
- **Future**: Will provide MCP server/client for tree operations

### LangChain
- **File**: `langchain.py`
- **Purpose**: LangChain tools and chains for tree manipulation
- **Status**: Placeholder - implementation pending
- **Future**: Custom tools, document loaders, memory stores

### Jupyter
- **File**: `jupyter.py`  
- **Purpose**: Interactive widgets and magic commands for notebooks
- **Status**: Placeholder - implementation pending
- **Future**: Rich tree visualization, IPython magics

### Databases
- **File**: `databases.py`
- **Purpose**: Adapters for storing trees in various databases
- **Status**: Placeholder - implementation pending
- **Future**: SQL, Neo4j, MongoDB, Redis adapters

## Installation

These integrations are not part of the core AlgoTree package. In the future, they will be installable separately:

```bash
# Core library only
pip install algotree

# With specific integrations (future)
pip install algotree[mcp]
pip install algotree[langchain]
pip install algotree[jupyter]
pip install algotree[databases]

# Or install integration separately (future)
pip install algotree-mcp
pip install algotree-langchain
```

## Development

Each integration should:
1. Have minimal dependencies on core AlgoTree
2. Include its own tests
3. Document its specific requirements
4. Provide examples of usage

## Contributing

When adding a new integration:
1. Create a new module in this directory
2. Add placeholder implementation with clear TODOs
3. Document the integration's purpose and future plans
4. Keep dependencies separate from core library

## Note

These are currently **placeholder implementations** to establish the structure for future development. Actual implementations will be added based on community needs and contributions.