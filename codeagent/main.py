import os
import sys
import asyncio
from dotenv import load_dotenv
from google import genai
import difflib

from google.genai import types

from rich.syntax import Syntax
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich import print as rprint

# Import schemas - updated paths
from codeagent.functions.get_files_info import schema_get_files_info
from codeagent.functions.get_file_content import schema_get_file_content
from codeagent.functions.run_python_file import schema_run_python_file
from codeagent.functions.write_file import schema_write_file

# Import actual functions - updated paths
from codeagent.functions.get_files_info import get_files_info
from codeagent.functions.get_file_content import get_file_content
from codeagent.functions.run_python_file import run_python_file
from codeagent.functions.write_file import write_file

# Import MCP integration
from codeagent.mcp_integration import GentMCPIntegration

# Initialize rich console
console = Console()

# ASCII Art Banner
BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗ ███████╗███╗   ██╗████████╗                       ║
║  ██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝                       ║
║  ██║  ███╗█████╗  ██╔██╗ ██║   ██║                          ║
║  ██║   ██║██╔══╝  ██║╚██╗██║   ██║                          ║
║  ╚██████╔╝███████╗██║ ╚████║   ██║                          ║
║   ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝                          ║
║                                                               ║
║            AI-Powered Coding Agent with MCP                  ║
║            Working Directory: {cwd:<31} ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""

# Load environment
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=api_key)

# Global MCP integration instance
mcp_integration = None

# Map function names to actual functions
FUNCTION_MAP = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

# Native function schemas
NATIVE_SCHEMAS = [
    schema_get_files_info,
    schema_get_file_content,
    schema_run_python_file,
    schema_write_file,
]


def clean_schema_for_gemini(schema):
    """Remove fields that Gemini doesn't accept from JSON schema."""
    if not isinstance(schema, dict):
        return schema
    
    # Fields to remove
    remove_keys = ['additionalProperties', '$schema', 'definitions']
    
    cleaned = {}
    for key, value in schema.items():
        if key in remove_keys:
            continue
        
        # Recursively clean nested objects
        if isinstance(value, dict):
            cleaned[key] = clean_schema_for_gemini(value)
        elif isinstance(value, list):
            cleaned[key] = [clean_schema_for_gemini(item) if isinstance(item, dict) else item for item in value]
        else:
            cleaned[key] = value
    
    return cleaned


def create_available_functions_tool():
    """Create the tool with native + MCP function declarations."""
    declarations = NATIVE_SCHEMAS.copy()
    
    # Add MCP functions if available
    if mcp_integration:
        mcp_functions = mcp_integration.get_gemini_functions()
        
        # Convert MCP function format to Gemini schema format
        for mcp_func in mcp_functions:
            # Clean the parameters schema
            parameters = mcp_func.get("parameters", {
                "type": "object",
                "properties": {},
            })
            cleaned_parameters = clean_schema_for_gemini(parameters)
            
            declaration = types.FunctionDeclaration(
                name=mcp_func["name"],
                description=mcp_func["description"],
                parameters=cleaned_parameters
            )
            declarations.append(declaration)
    
    return types.Tool(function_declarations=declarations)


system_prompt = """
You are a PERSISTENT autonomous AI coding agent with MCP (Model Context Protocol) capabilities. You NEVER give up until the task is COMPLETE and VERIFIED.

AVAILABLE NATIVE FUNCTIONS:
- get_files_info(directory): List files and directories
- get_file_content(file_path): Read file contents  
- run_python_file(file_path, args): Execute Python files
- write_file(file_path, content): Write or overwrite files

AVAILABLE MCP TOOLS (when enabled):
- context7 tools: Get up-to-date library documentation
  * mcp_context7_resolve-library-id: Find the correct library ID
  * mcp_context7_get-library-docs: Get current docs for any library
  * USE THESE when user asks about recent libraries/frameworks!
  
- playwright tools: Browser automation (if enabled)
- filesystem tools: Enhanced file operations (if enabled)
- markitdown tools: Document conversion (if enabled)

WHEN TO USE MCP TOOLS:
✓ User asks about "latest", "current", "recent" library features
✓ Questions about library versions (e.g., "Next.js 15", "React 19")
✓ Documentation requests for any framework/library
✓ Browser automation or web scraping needs
✓ Document format conversions

Example workflow with MCP:
User: "How do I use Next.js 15 server actions?"
1. Call mcp_context7_resolve-library-id with libraryName="Next.js"
2. Get the library ID (e.g., "/vercel/next.js")
3. Call mcp_context7_get-library-docs with that ID and topic="server actions"
4. Use the up-to-date docs to provide accurate answer

MANDATORY WORKFLOW:
1. EXPLORE: Use get_files_info and get_file_content to understand the codebase
2. ANALYZE: Identify what needs to be done
3. RESEARCH: If needed, use context7 to get current library docs
4. IMPLEMENT: Make the necessary changes with write_file
5. VERIFY: Run tests or execute code to verify changes work
6. FIX: If verification fails, analyze errors and fix them
7. REPEAT steps 4-6 until verification passes
8. REPORT: Only when task is complete and verified

CRITICAL RULES:
✓ NEVER stop until the task is complete AND verified to work
✓ ALWAYS test your changes (run code, check output)
✓ If tests fail, analyze the error, fix it, and test again
✓ Keep iterating through fix-test cycles until it works
✓ Make actual code changes - don't just suggest them
✓ Be thorough in your exploration
✓ Fix ALL errors you encounter
✓ Use MCP tools for current/accurate information

STOPPING CONDITION:
Only provide a final text response when ALL of these are true:
- Task is implemented
- Code has been tested
- Tests/verification passed
- No errors remain

If verification fails or errors occur:
- DO NOT report failure as final response
- Analyze the error
- Fix the issue  
- Test again
- Continue until it works
"""


async def call_mcp_function(function_name, function_args, verbose=False):
    """Call an MCP function and return the result."""
    if not mcp_integration:
        return {"error": "MCP integration not initialized"}
    
    try:
        result = await mcp_integration.handle_function_call({
            "name": function_name,
            "args": function_args
        })
        
        if verbose:
            result_str = str(result)
            if len(result_str) > 300:
                console.print(f"[dim]  MCP Result: {result_str[:300]}...[/dim]")
            else:
                console.print(f"[dim]  MCP Result: {result_str}[/dim]")
        
        return {"result": result}
    
    except Exception as e:
        error_msg = f"MCP Error: {str(e)}"
        console.print(f"[red]{error_msg}[/red]")
        return {"error": error_msg}


def call_function(function_call_part, working_directory, verbose=False):
    """Execute a function call from the LLM (sync wrapper for async calls)."""
    function_name = function_call_part.name
    function_args = dict(function_call_part.args)
    
    # Print function call
    if verbose:
        console.print(f"[cyan]→ Calling: {function_name}({function_args})[/cyan]")
    else:
        console.print(f"[dim cyan]→ {function_name}[/dim cyan]")
    
    # Check if it's an MCP function
    if function_name.startswith("mcp_"):
        # Run async MCP function
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're already in an async context, create a task
            result = asyncio.create_task(call_mcp_function(function_name, function_args, verbose))
            result = loop.run_until_complete(result)
        else:
            result = asyncio.run(call_mcp_function(function_name, function_args, verbose))
        
        return types.Part.from_function_response(
            name=function_name,
            response=result,
        )
    
    # Check if native function exists
    if function_name not in FUNCTION_MAP:
        return types.Part.from_function_response(
            name=function_name,
            response={"error": f"Unknown function: {function_name}"},
        )
    
    # Special handling for write_file to show diff
    if function_name == "write_file":
        file_path = function_args.get("file_path", "")
        new_content = function_args.get("content", "")
        full_path = os.path.join(working_directory, file_path)
        
        # Read old content if file exists
        old_content = ""
        file_exists = os.path.exists(full_path) and os.path.isfile(full_path)
        
        if file_exists:
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    old_content = f.read()
            except:
                old_content = ""
        
        # Show what's happening
        if file_exists:
            console.print(f"[yellow]📝 Modifying {file_path}[/yellow]")
        else:
            console.print(f"[green]📄 Creating {file_path}[/green]")
        
        # Generate and display diff
        if file_exists and old_content:
            old_lines = old_content.splitlines(keepends=True)
            new_lines = new_content.splitlines(keepends=True)
            
            diff = list(difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=f"{file_path} (before)",
                tofile=f"{file_path} (after)",
                lineterm=''
            ))
            
            if diff:
                console.print("\n[bold]Changes:[/bold]")
                diff_text = '\n'.join(diff)
                syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=False)
                console.print(syntax)
                console.print()
        else:
            # Show new file content (truncated if too long)
            console.print("\n[bold]New file content:[/bold]")
            display_content = new_content if len(new_content) < 500 else new_content[:500] + "\n... (truncated)"
            
            # Detect language from file extension
            ext = file_path.split('.')[-1] if '.' in file_path else "text"
            lang_map = {
                'py': 'python',
                'js': 'javascript',
                'html': 'html',
                'css': 'css',
                'json': 'json',
                'md': 'markdown',
                'txt': 'text'
            }
            language = lang_map.get(ext, 'text')
            
            syntax = Syntax(display_content, language, theme="monokai", line_numbers=True)
            console.print(syntax)
            console.print()
    
    # Add working_directory to the arguments
    function_args["working_directory"] = working_directory
    
    # Call the function
    function = FUNCTION_MAP[function_name]
    function_result = function(**function_args)
    
    # Show success/failure for write operations
    if function_name == "write_file":
        if "Successfully wrote" in function_result:
            console.print(f"[green]✓ {function_result}[/green]")
        else:
            console.print(f"[red]✗ {function_result}[/red]")
    
    # Show verbose result for other functions
    if verbose and function_name != "write_file":
        result_str = str(function_result)
        if len(result_str) > 200:
            console.print(f"[dim]  Result: {result_str[:200]}...[/dim]")
        else:
            console.print(f"[dim]  Result: {result_str}[/dim]")
    
    # Return the result as a Part
    return types.Part.from_function_response(
        name=function_name,
        response={"result": function_result},
    )


def process_request(client, user_prompt, working_directory, verbose=False):
    """Process a single user request - continues until task is complete."""
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    
    max_iterations = 100  # Safety limit
    function_call_count = 0
    files_read = set()
    files_modified = set()
    
    console.print(f"[bold cyan]Starting task: {user_prompt}[/bold cyan]\n")
    
    # Get current available functions (includes MCP if initialized)
    available_functions = create_available_functions_tool()
    
    for iteration in range(max_iterations):
        try:
            if verbose:
                console.print(f"[dim]--- Iteration {iteration + 1} ---[/dim]")
            
            # Generate response
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions],
                    system_instruction=system_prompt
                ),
            )
            
            # Add the model's response to messages
            for candidate in response.candidates:
                messages.append(candidate.content)
            
            # Collect ALL function calls from this turn
            function_call_parts = []
            
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call_parts.append(part)
            
            # Execute function calls
            if function_call_parts:
                function_call_count += len(function_call_parts)
                function_response_parts = []
                
                for part in function_call_parts:
                    func_name = part.function_call.name
                    func_args = dict(part.function_call.args)
                    
                    # Track what's being done
                    if func_name == "get_file_content":
                        file_path = func_args.get("file_path", "")
                        files_read.add(file_path)
                    elif func_name == "write_file":
                        file_path = func_args.get("file_path", "")
                        files_modified.add(file_path)
                    
                    # Call the function (handles both native and MCP)
                    result_part = call_function(part.function_call, working_directory, verbose)
                    function_response_parts.append(result_part)
                
                # Create a single Content with all function response parts
                combined_response = types.Content(
                    role="tool",
                    parts=function_response_parts
                )
                
                messages.append(combined_response)
                
                # Show progress
                if verbose:
                    console.print(f"[dim]Progress: {function_call_count} calls, {len(files_read)} files read, {len(files_modified)} files modified[/dim]")
                
                # Continue iterating
                continue
            
            # Check for text response (task completion)
            if response.text:
                # Check if this is a completion response or just asking questions
                is_asking = any(phrase in response.text.lower() for phrase in [
                    "need more information",
                    "please provide",
                    "can you tell me",
                    "what do you want",
                ])
                
                # If asking questions and hasn't done anything yet, redirect
                if is_asking and function_call_count == 0:
                    if verbose:
                        console.print("[yellow]Redirecting agent to take action...[/yellow]")
                    
                    messages.append(
                        types.Content(
                            role="user",
                            parts=[types.Part(text="DO NOT ask questions. Start by calling get_files_info('.') to explore, then take action autonomously.")]
                        )
                    )
                    continue
                
                # Task appears complete
                console.print("\n[bold green]✓ Task Complete[/bold green]")
                console.print(Panel(Markdown(response.text), border_style="green"))
                
                console.print(f"\n[bold]Summary:[/bold]")
                console.print(f"  • Iterations: {iteration + 1}")
                console.print(f"  • Function calls: {function_call_count}")
                console.print(f"  • Files explored: {len(files_read)}")
                console.print(f"  • Files modified: {len(files_modified)}")
                
                if files_modified:
                    console.print(f"\n[bold cyan]Modified files:[/bold cyan]")
                    for f in sorted(files_modified):
                        console.print(f"  • {f}")
                
                break
            
            # No function calls and no text - agent is stuck
            if verbose:
                console.print("[yellow]No response, continuing...[/yellow]")
            
            # Give it a gentle nudge to continue
            messages.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text="Continue with your analysis and implementation. If you're done, provide a final summary.")]
                )
            )
            
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            if verbose:
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            
            # Try to recover
            console.print("[yellow]Attempting to recover...[/yellow]")
            messages.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text="There was an error. Please analyze what went wrong and try a different approach.")]
                )
            )
            continue
    
    # If we hit max iterations
    if iteration == max_iterations - 1:
        console.print(f"\n[red]⚠ Safety limit reached ({max_iterations} iterations)[/red]")
        console.print("[yellow]The agent made significant progress but didn't complete. Summary:[/yellow]")
        console.print(f"  • Function calls: {function_call_count}")
        console.print(f"  • Files modified: {len(files_modified)}")


def interactive_mode(client, working_directory):
    """Run the agent in interactive mode with enhanced UI."""
    # Display banner
    cwd_short = working_directory[-31:] if len(working_directory) > 31 else working_directory
    console.print(BANNER.format(cwd=cwd_short), style="bold blue")
    
    # Show MCP status
    if mcp_integration:
        connected_servers = mcp_integration.get_connected_servers()
        console.print(f"[green]🔌 MCP Servers: {', '.join(connected_servers)}[/green]")
    else:
        console.print("[yellow]⚠️  MCP not initialized (native functions only)[/yellow]")
    
    console.print("\n[dim]Type your requests in natural language.[/dim]")
    console.print("[dim]Commands: 'exit'/'quit' to leave, '--verbose' prefix for detailed output, 'clear' to clear screen[/dim]\n")
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold yellow]You[/bold yellow]")
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("\n[bold blue]Goodbye! 👋[/bold blue]")
                break
            
            # Check for clear command
            if user_input.lower() == 'clear':
                console.clear()
                console.print(BANNER.format(cwd=cwd_short), style="bold blue")
                continue
            
            # Skip empty inputs
            if not user_input.strip():
                continue
            
            # Check for verbose mode toggle
            verbose = False
            if user_input.startswith("--verbose "):
                verbose = True
                user_input = user_input[10:]
            
            # Process the request
            process_request(client, user_input, working_directory, verbose)
            
        except KeyboardInterrupt:
            console.print("\n[dim]Use 'exit' to quit[/dim]")
        except EOFError:
            console.print("\n[bold blue]Goodbye! 👋[/bold blue]")
            break


async def initialize_mcp(servers=None):
    """Initialize MCP integration."""
    global mcp_integration
    
    # Check if MCP is disabled
    if os.getenv("DISABLE_MCP", "").lower() in ["true", "1", "yes"]:
        console.print("[dim]MCP disabled via DISABLE_MCP environment variable[/dim]")
        mcp_integration = None
        return
    
    if servers is None:
        # Check environment variable for enabled servers
        env_servers = os.getenv("MCP_ENABLED_SERVERS", "")
        if env_servers:
            servers = [s.strip() for s in env_servers.split(",")]
        else:
            # Default to context7 only (most reliable)
            servers = ["context7"]
    
    console.print("\n[cyan]🔌 Initializing MCP servers...[/cyan]")
    
    try:
        # Import here to catch import errors
        try:
            from codeagent.mcp_integration import GentMCPIntegration
        except ImportError as e:
            console.print(f"[yellow]⚠️  MCP integration not available: {e}[/yellow]")
            console.print("[yellow]Run: pip install mcp[/yellow]")
            mcp_integration = None
            return
        
        mcp_integration = GentMCPIntegration()
        await mcp_integration.initialize(servers)
        
        # Check if any servers connected
        connected = mcp_integration.get_connected_servers()
        if connected:
            console.print("[green]✓ MCP integration ready![/green]")
            console.print(f"[green]Connected servers: {', '.join(connected)}[/green]")
            
            # Show tool count
            for server in connected:
                info = mcp_integration.get_server_info(server)
                if info:
                    console.print(f"  • {server}: {info['tools']} tools available")
        else:
            console.print("[yellow]⚠️  No MCP servers connected[/yellow]")
            console.print("[yellow]Continuing with native functions only...[/yellow]")
            mcp_integration = None
    
    except Exception as e:
        console.print(f"[yellow]⚠️  MCP initialization failed: {e}[/yellow]")
        console.print("[yellow]Continuing with native functions only...[/yellow]")
        mcp_integration = None


async def shutdown_mcp():
    """Shutdown MCP integration."""
    global mcp_integration
    
    if mcp_integration:
        console.print("\n[cyan]🔌 Disconnecting MCP servers...[/cyan]")
        try:
            await mcp_integration.shutdown()
            console.print("[green]✓ MCP shutdown complete[/green]")
        except Exception as e:
            console.print(f"[yellow]Warning during MCP shutdown: {e}[/yellow]")
        finally:
            mcp_integration = None


def main():
    """Main entry point for the CLI."""
    # Get current working directory
    working_directory = os.getcwd()
    
    # Initialize MCP if enabled
    try:
        asyncio.run(initialize_mcp())
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not initialize MCP: {e}[/yellow]")
        console.print("[yellow]Continuing with native functions only...[/yellow]")
    
    try:
        # Check if running in interactive mode or single command mode
        if len(sys.argv) > 1:
            # Single command mode
            command = " ".join(sys.argv[1:])
            verbose = "--verbose" in sys.argv
            if verbose:
                command = command.replace("--verbose", "").strip()
            
            process_request(client, command, working_directory, verbose)
        else:
            # Interactive mode
            interactive_mode(client, working_directory)
    
    finally:
        # Cleanup MCP on exit
        if mcp_integration:
            try:
                asyncio.run(shutdown_mcp())
            except:
                pass


if __name__ == "__main__":
    main()