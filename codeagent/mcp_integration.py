# =============================================================================
# MCP Integration for Gent (CodeAgent) - FIXED VERSION
# =============================================================================
# This module provides Model Context Protocol (MCP) server integration,
# allowing Gent to connect to external tools and data sources through MCP.
# =============================================================================

import asyncio
import os
import warnings
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Suppress specific MCP warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*cancel scope.*")

try:
    from mcp import ClientSession, StdioServerParameters, types
    from mcp.client.stdio import stdio_client
    from mcp.client.sse import sse_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP SDK not installed. Run: pip install mcp")


# =============================================================================
# CONFIGURATION
# =============================================================================

class TransportType(Enum):
    """MCP server transport types."""
    STDIO = "stdio"  # Local subprocess communication
    SSE = "sse"      # Server-Sent Events (HTTP-based)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    name: str
    transport: TransportType
    
    # For stdio transport
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    
    # For SSE transport
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    
    # Optional settings
    auto_approve_tools: bool = False
    timeout: int = 60


# =============================================================================
# PRELOADED SERVER CONFIGURATIONS - SIMPLIFIED
# =============================================================================

PRELOADED_SERVERS = {
    "context7": MCPServerConfig(
        name="context7",
        transport=TransportType.SSE,
        url="https://mcp.context7.com/sse",
        auto_approve_tools=True,
    ),
    
    "filesystem": MCPServerConfig(
        name="filesystem",
        transport=TransportType.STDIO,
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "."],
        auto_approve_tools=True,
    ),
    
    "playwright": MCPServerConfig(
        name="playwright",
        transport=TransportType.STDIO,
        command="npx",
        args=["-y", "@playwright/mcp@latest"],
        auto_approve_tools=False,  # Requires approval for browser actions
    ),
    
    "playwright-ea": MCPServerConfig(
        name="playwright-ea",
        transport=TransportType.STDIO,
        command="npx",
        args=["-y", "@executeautomation/playwright-mcp-server"],
        auto_approve_tools=False,  # Alternative Playwright server
    ),
    
    "markitdown": MCPServerConfig(
        name="markitdown",
        transport=TransportType.STDIO,
        command="npx",
        args=["-y", "markitdown-mcp-npx"],  # NPX wrapper, no Python setup needed
        auto_approve_tools=True,
    ),
    
    "github": MCPServerConfig(
        name="github",
        transport=TransportType.STDIO,
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")},
        auto_approve_tools=False,
    ),
    
    "brave-search": MCPServerConfig(
        name="brave-search",
        transport=TransportType.STDIO,
        command="npx",
        args=["-y", "@modelcontextprotocol/server-brave-search"],
        env={"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", "")},
        auto_approve_tools=True,
    ),
}


# =============================================================================
# MCP CLIENT WRAPPER - SIMPLIFIED
# =============================================================================

class MCPClient:
    """Wrapper for an MCP server client session."""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.session: Optional[ClientSession] = None
        self.available_tools: List[Dict[str, Any]] = []
        self.available_resources: List[Dict[str, Any]] = []
        self._context_manager = None
        
    async def connect(self):
        """Connect to the MCP server."""
        if not MCP_AVAILABLE:
            raise RuntimeError("MCP SDK not installed")
        
        try:
            if self.config.transport == TransportType.STDIO:
                await self._connect_stdio()
            elif self.config.transport == TransportType.SSE:
                await self._connect_sse()
            else:
                raise ValueError(f"Unsupported transport: {self.config.transport}")
            
            # Initialize session and discover capabilities
            await self.session.initialize()
            await self._discover_capabilities()
            
            print(f"✓ Connected to MCP server: {self.config.name}")
            print(f"  Tools: {len(self.available_tools)}")
            
        except Exception as e:
            print(f"✗ Failed to connect to {self.config.name}: {e}")
            raise
    
    async def _connect_stdio(self):
        """Connect via stdio transport."""
        server_params = StdioServerParameters(
            command=self.config.command,
            args=self.config.args or [],
            env=self.config.env,
        )
        
        # Store the context manager
        self._context_manager = stdio_client(server_params)
        read_stream, write_stream = await self._context_manager.__aenter__()
        
        self.session = ClientSession(read_stream, write_stream)
        await self.session.__aenter__()
    
    async def _connect_sse(self):
        """Connect via SSE transport."""
        # Store the context manager
        self._context_manager = sse_client(
            self.config.url,
            headers=self.config.headers or {}
        )
        read_stream, write_stream = await self._context_manager.__aenter__()
        
        self.session = ClientSession(read_stream, write_stream)
        await self.session.__aenter__()
    
    async def _discover_capabilities(self):
        """Discover available tools from the server."""
        # List tools
        try:
            tools_response = await self.session.list_tools()
            self.available_tools = [
                {
                    "name": tool.name,
                    "description": tool.description or f"Tool: {tool.name}",
                    "input_schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {},
                    "server": self.config.name,
                }
                for tool in tools_response.tools
            ]
        except Exception as e:
            print(f"Warning: Could not list tools from {self.config.name}: {e}")
            self.available_tools = []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server."""
        try:
            result = await self.session.call_tool(tool_name, arguments)
            
            # Extract content from result
            if result.content:
                if len(result.content) == 1:
                    content_item = result.content[0]
                    if hasattr(content_item, 'text'):
                        return content_item.text
                    elif hasattr(content_item, 'data'):
                        return {"type": "image", "data": content_item.data}
                
                # Multiple content items
                return [
                    item.text if hasattr(item, 'text') else str(item)
                    for item in result.content
                ]
            
            return None
            
        except Exception as e:
            return f"Error calling tool {tool_name}: {str(e)}"
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        # Suppress cleanup errors - they don't affect functionality
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
        except (RuntimeError, GeneratorExit, Exception):
            pass  # Ignore cleanup errors
        
        try:
            if self._context_manager:
                await self._context_manager.__aexit__(None, None, None)
        except (RuntimeError, GeneratorExit, Exception):
            pass  # Ignore cleanup errors


# =============================================================================
# MCP MANAGER - SIMPLIFIED
# =============================================================================

class MCPManager:
    """Manages multiple MCP server connections."""
    
    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
    
    async def initialize(self, server_names: Optional[List[str]] = None):
        """Initialize MCP servers."""
        if not MCP_AVAILABLE:
            print("MCP SDK not available. Skipping MCP initialization.")
            return
        
        if server_names is None:
            server_names = ["context7"]
        
        print(f"\n🔌 Initializing {len(server_names)} MCP server(s)...")
        
        for server_name in server_names:
            if server_name not in PRELOADED_SERVERS:
                print(f"⚠️  Unknown server: {server_name}")
                continue
            
            config = PRELOADED_SERVERS[server_name]
            client = MCPClient(config)
            
            try:
                await client.connect()
                self.clients[server_name] = client
            except Exception as e:
                print(f"Failed to initialize {server_name}: {e}")
                # Continue with other servers
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools from all connected servers."""
        all_tools = []
        for client in self.clients.values():
            all_tools.extend(client.available_tools)
        return all_tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the appropriate MCP server."""
        for client in self.clients.values():
            for tool in client.available_tools:
                if tool["name"] == tool_name:
                    return await client.call_tool(tool_name, arguments)
        
        return f"Tool {tool_name} not found in any connected MCP server"
    
    async def shutdown(self):
        """Disconnect from all MCP servers."""
        print("\n🔌 Disconnecting from MCP servers...")
        for client in self.clients.values():
            await client.disconnect()
        self.clients.clear()


# =============================================================================
# GEMINI FUNCTION CONVERSION - SIMPLIFIED
# =============================================================================

class MCPToGeminiConverter:
    """Converts MCP tools to Gemini function declarations."""
    
    @staticmethod
    def convert_tools_to_gemini(mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert MCP tool definitions to Gemini function declarations."""
        gemini_functions = []
        
        for tool in mcp_tools:
            # Create a safe name by prefixing with mcp_
            safe_name = f"mcp_{tool['server']}_{tool['name'].replace('-', '_')}"
            
            gemini_function = {
                "name": safe_name,
                "description": tool.get("description", f"Tool from {tool['server']} server"),
                "parameters": tool.get("input_schema", {
                    "type": "object",
                    "properties": {},
                }),
                "_mcp_original_name": tool["name"],
                "_mcp_server": tool["server"],
            }
            
            gemini_functions.append(gemini_function)
        
        return gemini_functions
    
    @staticmethod
    def extract_mcp_call(gemini_function_call: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Extract the original MCP tool name and arguments."""
        function_name = gemini_function_call.get("name", "")
        arguments = gemini_function_call.get("args", {})
        
        # Extract original tool name
        if function_name.startswith("mcp_"):
            # Remove mcp_ prefix and server name
            parts = function_name[4:].split("_", 1)
            if len(parts) == 2:
                # Convert back to original format (underscores to hyphens)
                original_name = parts[1].replace("_", "-")
                return original_name, arguments
        
        return function_name, arguments


# =============================================================================
# INTEGRATION WITH GENT AGENT - SIMPLIFIED
# =============================================================================

class GentMCPIntegration:
    """Main integration class for adding MCP capabilities to Gent."""
    
    def __init__(self):
        self.manager = MCPManager()
        self.converter = MCPToGeminiConverter()
    
    async def initialize(self, server_names: Optional[List[str]] = None):
        """Initialize MCP servers."""
        await self.manager.initialize(server_names)
    
    def get_gemini_functions(self) -> List[Dict[str, Any]]:
        """Get all MCP tools as Gemini function declarations."""
        mcp_tools = self.manager.get_all_tools()
        return self.converter.convert_tools_to_gemini(mcp_tools)
    
    async def handle_function_call(self, function_call: Dict[str, Any]) -> Any:
        """Handle a function call from Gemini that might be an MCP tool."""
        function_name = function_call.get("name", "")
        
        if function_name.startswith("mcp_"):
            tool_name, arguments = self.converter.extract_mcp_call(function_call)
            return await self.manager.call_tool(tool_name, arguments)
        
        return None
    
    async def shutdown(self):
        """Shutdown all MCP connections."""
        await self.manager.shutdown()
    
    def get_connected_servers(self) -> List[str]:
        """Get list of currently connected servers."""
        return list(self.manager.clients.keys())
    
    def get_server_info(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific server."""
        if server_name in self.manager.clients:
            client = self.manager.clients[server_name]
            return {
                "name": server_name,
                "transport": client.config.transport.value,
                "tools": len(client.available_tools),
                "tool_list": [t["name"] for t in client.available_tools],
            }
        return None


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

async def test_mcp():
    """Simple test of MCP integration."""
    if not MCP_AVAILABLE:
        print("MCP SDK not installed. Please run: pip install mcp")
        return
    
    mcp = GentMCPIntegration()
    
    try:
        # Initialize with context7 only (most reliable)
        await mcp.initialize(["context7"])
        
        # Get available functions
        functions = mcp.get_gemini_functions()
        print(f"\nAvailable MCP functions: {len(functions)}")
        for func in functions:
            print(f"  - {func['name']}: {func['description']}")
        
        # Test a function call
        if functions:
            print("\nTesting function call...")
            result = await mcp.handle_function_call({
                "name": functions[0]["name"],
                "args": {"libraryName": "Next.js"}
            })
            print(f"Result: {result}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await mcp.shutdown()


if __name__ == "__main__":
    asyncio.run(test_mcp())