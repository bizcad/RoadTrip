## Step-by-Step Guide: Building an MCP Discovery Client

An MCP discovery client connects to MCP servers, discovers available tools/resources/prompts, and integrates them with LLM agents. Here's a comprehensive guide covering both basic and production-ready implementations. [github](https://github.com/modelcontextprotocol)

## Prerequisites

Before building your MCP client, ensure you have: [github](https://github.com/modelcontextprotocol)
- Python 3.10+ or Node.js 18+ installed
- An LLM API key (Anthropic Claude, OpenAI, or Google Gemini)
- Basic understanding of async programming
- MCP SDK for your language of choice

## Phase 1: Environment Setup

### Python Setup

Create your project directory and install dependencies: [github](https://github.com/modelcontextprotocol)

```bash
# Create project directory
mkdir mcp-discovery-client
cd mcp-discovery-client

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate  # Windows

# Install required packages
pip install mcp anthropic python-dotenv
# For LangChain integration:
pip install langchain langchain_mcp_adapters langgraph
```

### TypeScript Setup

For TypeScript/JavaScript clients: [youtube](https://www.youtube.com/watch?v=5tl6D-h2_Qc)

```bash
# Initialize project
npm init -y

# Install dependencies
npm install @modelcontextprotocol/sdk @anthropic-ai/sdk dotenv
npm install -D typescript @types/node

# Initialize TypeScript
npx tsc --init
```

### Configure API Keys

Create a `.env` file: [github](https://github.com/modelcontextprotocol)

```bash
# For Anthropic Claude
ANTHROPIC_API_KEY=your-key-here

# For Google Gemini
GOOGLE_API_KEY=your-key-here

# For OpenAI
OPENAI_API_KEY=your-key-here
```

Add `.env` to `.gitignore`:

```bash
echo ".env" >> .gitignore
```

## Phase 2: Core Client Structure

### Python Implementation

Create `client.py` with the basic structure: [github](https://github.com/modelcontextprotocol/servers)

```python
import asyncio
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class MCPDiscoveryClient:
    def __init__(self):
        """Initialize the MCP client"""
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.available_servers = []
        
    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server and discover its capabilities"""
        # Determine server type
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        
        if not (is_python or is_js):
            raise ValueError("Server script must be .py or .js file")
        
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        # Establish connection
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        
        # Initialize and discover capabilities
        await self.session.initialize()
        await self.discover_capabilities()
```

### Discovery Methods

Add capability discovery functions: [github](https://github.com/modelcontextprotocol)

```python
    async def discover_capabilities(self):
        """Discover all server capabilities"""
        print("\n=== Discovering Server Capabilities ===")
        
        # Discover tools
        tools_response = await self.session.list_tools()
        self.tools = tools_response.tools
        print(f"\nTools ({len(self.tools)}):")
        for tool in self.tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Discover resources
        try:
            resources_response = await self.session.list_resources()
            self.resources = resources_response.resources
            print(f"\nResources ({len(self.resources)}):")
            for resource in self.resources:
                print(f"  - {resource.name}: {resource.description}")
        except Exception:
            self.resources = []
            print("\nResources: Not supported")
        
        # Discover prompts
        try:
            prompts_response = await self.session.list_prompts()
            self.prompts = prompts_response.prompts
            print(f"\nPrompts ({len(self.prompts)}):")
            for prompt in self.prompts:
                print(f"  - {prompt.name}: {prompt.description}")
        except Exception:
            self.prompts = []
            print("\nPrompts: Not supported")
```

## Phase 3: Query Processing with Tool Discovery

Implement query processing that utilizes discovered tools: [github](https://github.com/modelcontextprotocol/servers)

```python
    async def process_query(self, query: str) -> str:
        """Process a user query with dynamic tool discovery"""
        messages = [{"role": "user", "content": query}]
        
        # Format tools for Claude
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in self.tools]
        
        # Initial LLM call
        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )
        
        # Process tool calls
        final_text = []
        assistant_content = []
        
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_content.append(content)
                
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                
                # Execute tool call
                print(f"\n[Executing tool: {tool_name}]")
                result = await self.session.call_tool(tool_name, tool_args)
                
                assistant_content.append(content)
                messages.append({
                    "role": "assistant",
                    "content": assistant_content
                })
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": result.content
                    }]
                })
                
                # Get final response
                response = self.anthropic.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools
                )
                
                final_text.append(response.content[0].text)
        
        return "\n".join(final_text)
```

## Phase 4: Multi-Server Discovery

Add support for discovering and managing multiple servers: [github](https://github.com/modelcontextprotocol/servers)

```python
    async def discover_multiple_servers(self, server_configs: list):
        """Connect to and discover capabilities from multiple servers"""
        self.server_registry = {}
        
        for config in server_configs:
            try:
                print(f"\nConnecting to {config['name']}...")
                await self.connect_to_server(config['path'])
                
                self.server_registry[config['name']] = {
                    'tools': self.tools.copy(),
                    'resources': self.resources.copy(),
                    'prompts': self.prompts.copy(),
                    'session': self.session
                }
                
                print(f"✓ {config['name']} connected successfully")
            except Exception as e:
                print(f"✗ Failed to connect to {config['name']}: {e}")
    
    def list_all_capabilities(self):
        """List all discovered capabilities across servers"""
        print("\n=== All Discovered Capabilities ===")
        
        for server_name, capabilities in self.server_registry.items():
            print(f"\n{server_name}:")
            print(f"  Tools: {len(capabilities['tools'])}")
            print(f"  Resources: {len(capabilities['resources'])}")
            print(f"  Prompts: {len(capabilities['prompts'])}")
```

## Phase 5: SSE/HTTP Transport Support

For remote server discovery, add SSE support: [github](https://github.com/invariantlabs-ai/mcp-streamable-http)

```python
from mcp.client.sse import sse_client

class MCPDiscoveryClient:
    async def connect_to_remote_server(self, server_url: str):
        """Connect to remote MCP server via SSE"""
        async with sse_client(url=server_url) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                self.session = session
                await self.discover_capabilities()
```

## Phase 6: Interactive Interface

Add an interactive CLI for exploration: [github](https://github.com/modelcontextprotocol)

```python
    async def interactive_discovery(self):
        """Run interactive discovery and query loop"""
        print("\n=== MCP Discovery Client Started ===")
        print("Commands:")
        print("  query <text> - Send query to LLM")
        print("  list - List all capabilities")
        print("  servers - Show connected servers")
        print("  quit - Exit")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'list':
                    self.list_all_capabilities()
                elif user_input.lower() == 'servers':
                    print(list(self.server_registry.keys()))
                elif user_input.startswith('query '):
                    query = user_input[6:]
                    response = await self.process_query(query)
                    print(f"\n{response}")
                else:
                    print("Unknown command")
                    
            except Exception as e:
                print(f"Error: {e}")
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
```

## Phase 7: Main Entry Point

Create the main execution logic: [github](https://github.com/modelcontextprotocol)

```python
async def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python client.py <server1.py> [server2.py ...]")
        sys.exit(1)
    
    client = MCPDiscoveryClient()
    
    try:
        # Discover servers
        server_configs = [
            {'name': f'server_{i}', 'path': path}
            for i, path in enumerate(sys.argv[1:], 1)
        ]
        
        await client.discover_multiple_servers(server_configs)
        client.list_all_capabilities()
        
        # Start interactive session
        await client.interactive_discovery()
        
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## Phase 8: Advanced Features

### Registry Integration

Connect to the Official MCP Registry: [modelcontextprotocol](https://modelcontextprotocol.io/registry/about)

```python
import httpx

class MCPDiscoveryClient:
    async def search_registry(self, query: str):
        """Search the official MCP registry"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://registry.modelcontextprotocol.io/search?q={query}"
            )
            servers = response.json()
            
            print(f"\nFound {len(servers)} servers:")
            for server in servers:
                print(f"  - {server['name']}: {server['description']}")
                print(f"    Install: {server['install_command']}")
```

### Capability Filtering

Add filtering for specific tool types: [dailydoseofds](https://www.dailydoseofds.com/model-context-protocol-crash-course-part-3/)

```python
    def find_tools_by_category(self, category: str):
        """Filter tools by category across all servers"""
        matching_tools = []
        
        for server_name, capabilities in self.server_registry.items():
            for tool in capabilities['tools']:
                if category.lower() in tool.description.lower():
                    matching_tools.append({
                        'server': server_name,
                        'tool': tool.name,
                        'description': tool.description
                    })
        
        return matching_tools
```

## Running the Discovery Client

### Basic Usage

```bash
# Single server
python client.py path/to/server.py

# Multiple servers
python client.py server1.py server2.py server3.js

# With remote server
python client.py https://example.com/mcp-server
```

### Example Output

```
=== Discovering Server Capabilities ===

Tools (5):
  - calculate: Perform mathematical calculations
  - search_web: Search the internet
  - read_file: Read file contents
  - write_file: Write to files
  - execute_command: Run terminal commands

Resources (2):
  - config: Configuration settings
  - database: Database connection

Prompts (1):
  - analyze_code: Code analysis prompt

=== MCP Discovery Client Started ===
Commands:
  query <text> - Send query to LLM
  list - List all capabilities
  servers - Show connected servers
  quit - Exit

> query What tools are available?
```

## Best Practices

### Error Handling

Implement robust error handling: [github](https://github.com/modelcontextprotocol)

```python
try:
    result = await self.session.call_tool(tool_name, tool_args)
except Exception as e:
    print(f"Tool execution failed: {e}")
    result = {"error": str(e)}
```

### Resource Management

Always use context managers: [github](https://github.com/modelcontextprotocol)

```python
async with AsyncExitStack() as stack:
    # All resources automatically cleaned up
    pass
```

### Security

- Validate server sources before connecting [github](https://github.com/modelcontextprotocol)
- Store API keys in environment variables [github](https://github.com/modelcontextprotocol)
- Sanitize tool inputs and outputs [modelcontextprotocol](https://modelcontextprotocol.info/docs/best-practices/)
- Implement authentication for remote servers [modelcontextprotocol](https://modelcontextprotocol.info/docs/best-practices/)

### Performance

- Cache discovered capabilities [modelcontextprotocol](https://modelcontextprotocol.info/docs/best-practices/)
- Use connection pooling for multiple servers [modelcontextprotocol](https://modelcontextprotocol.info/docs/best-practices/)
- Implement timeouts for slow servers [github](https://github.com/modelcontextprotocol)

## Troubleshooting

Common issues and solutions: [github](https://github.com/modelcontextprotocol)

| Issue | Solution |
|-------|----------|
| Connection timeout | Increase timeout settings, check server path |
| Tool execution fails | Verify tool parameters match schema |
| First response slow (30s) | Normal behavior during initialization |
| FileNotFoundError | Use absolute path to server script |

## Video Tutorials

For visual learners, these tutorials provide step-by-step demonstrations:

1. **MCP Tutorial: Build Your First MCP Server and Client** - KodeKloud (35:52) [youtube](https://www.youtube.com/watch?v=RhTiAOGwbYE)
2. **Create MCP Clients in JavaScript** - Alejandro AO (36:01) [youtube](https://www.youtube.com/watch?v=5tl6D-h2_Qc)
3. **Create an MCP Client in Python - FastAPI Tutorial** (1:13:17) [youtube](https://www.youtube.com/watch?v=mhdGVbJBswA)
4. **Build AI-Powered Apps with MCP Clients in Spring AI** - Dan Vega [youtube](https://www.youtube.com/watch?v=TSFkdlreRMQ)

## Additional Resources

- Official Build Guide: https://modelcontextprotocol.io/docs/develop/build-client [github](https://github.com/modelcontextprotocol)
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk [github](https://github.com/mcp-auth/mcp-typescript-sdk)
- Python Examples: https://realpython.com/python-mcp-client/ [realpython](https://realpython.com/python-mcp-client/)
- Composio Integration: https://composio.dev/blog/mcp-client-step-by-step-guide-to-building-from-scratch [github](https://github.com/modelcontextprotocol/servers)

This guide provides a foundation for building production-ready MCP discovery clients that can connect to local and remote servers, discover their capabilities dynamically, and integrate them with AI agents for enhanced functionality.