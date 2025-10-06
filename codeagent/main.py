import os
import sys
import asyncio
import concurrent.futures
import warnings
import difflib
from dotenv import load_dotenv
from google import genai
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

warnings.filterwarnings("ignore", category=RuntimeWarning, message="coroutine.*was never awaited")

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

# Function maps
FUNCTION_MAP = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

NATIVE_SCHEMAS = [
    schema_get_files_info,
    schema_get_file_content,
    schema_run_python_file,
    schema_write_file,
]


def clean_schema_for_gemini(schema):
    if not isinstance(schema, dict):
        return schema
    remove_keys = ['additionalProperties', '$schema', 'definitions']
    cleaned = {}
    for key, value in schema.items():
        if key in remove_keys:
            continue
        if isinstance(value, dict):
            cleaned[key] = clean_schema_for_gemini(value)
        elif isinstance(value, list):
            cleaned[key] = [clean_schema_for_gemini(item) if isinstance(item, dict) else item for item in value]
        else:
            cleaned[key] = value
    return cleaned


def create_available_functions_tool():
    declarations = NATIVE_SCHEMAS.copy()
    if mcp_integration:
        mcp_functions = mcp_integration.get_gemini_functions()
        for mcp_func in mcp_functions:
            parameters = mcp_func.get("parameters", {"type": "object", "properties": {}})
            cleaned_parameters = clean_schema_for_gemini(parameters)
            declaration = types.FunctionDeclaration(
                name=mcp_func["name"],
                description=mcp_func["description"],
                parameters=cleaned_parameters
            )
            declarations.append(declaration)
    return types.Tool(function_declarations=declarations)


system_prompt = """
You are a PERSISTENT autonomous AI coding agent with MCP capabilities. 
You NEVER give up until the task is COMPLETE and VERIFIED.
Follow the structured fix-test loop until success.
"""

# ---------- MCP FUNCTION CALLS ----------
async def call_mcp_function(function_name, function_args, verbose=False):
    if not mcp_integration:
        return {"error": "MCP integration not initialized"}
    try:
        result = await mcp_integration.handle_function_call({"name": function_name, "args": function_args})
        if verbose:
            console.print(f"[dim]MCP Result: {str(result)[:250]}[/dim]")
        return {"result": result}
    except Exception as e:
        msg = f"MCP Error: {str(e)}"
        console.print(f"[red]{msg}[/red]")
        return {"error": msg}


# ---------- FUNCTION EXECUTION ----------
def call_function(function_call_part, working_directory, verbose=False):
    function_name = function_call_part.name
    function_args = dict(function_call_part.args)
    if verbose:
        console.print(f"[cyan]→ Calling: {function_name}({function_args})[/cyan]")
    else:
        console.print(f"[dim cyan]→ {function_name}[/dim cyan]")

    if function_name.startswith("mcp_"):
        return asyncio.run(call_mcp_function(function_name, function_args, verbose))

    if function_name not in FUNCTION_MAP:
        return types.Part.from_function_response(name=function_name, response={"error": f"Unknown function: {function_name}"})

    if function_name == "write_file":
        file_path = function_args.get("file_path", "")
        new_content = function_args.get("content", "")
        full_path = os.path.join(working_directory, file_path)
        old_content = ""
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    old_content = f.read()
            except:
                old_content = ""

        if os.path.exists(full_path):
            console.print(f"[yellow]📝 Modifying {file_path}[/yellow]")
        else:
            console.print(f"[green]📄 Creating {file_path}[/green]")

        if old_content:
            diff = list(difflib.unified_diff(
                old_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"{file_path} (before)",
                tofile=f"{file_path} (after)",
                lineterm=''
            ))
            if diff:
                console.print("\n[bold]Changes:[/bold]")
                console.print(Syntax('\n'.join(diff), "diff", theme="monokai"))
        else:
            console.print("\n[bold]New content:[/bold]")
            console.print(Syntax(new_content[:500], "python", theme="monokai"))

    function_args["working_directory"] = working_directory
    fn = FUNCTION_MAP[function_name]
    result = fn(**function_args)
    if verbose:
        console.print(f"[dim]{str(result)[:300]}[/dim]")
    return types.Part.from_function_response(name=function_name, response={"result": result})


# ---------- MAIN PROCESS LOOP ----------
def process_request(client, user_prompt, working_directory, verbose=False):
    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]
    console.print(f"[bold cyan]Starting task: {user_prompt}[/bold cyan]\n")

    available_functions = create_available_functions_tool()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for iteration in range(1, 100):
        try:
            if verbose:
                console.print(f"[dim]--- Iteration {iteration} ---[/dim]")

            # ✅ Run Gemini safely in background
            console.print("[dim]🤖 Generating Gemini response...[/dim]")
            response = loop.run_until_complete(asyncio.to_thread(
                client.models.generate_content,
                model="gemini-2.0-flash",
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions],
                    system_instruction=system_prompt
                ),
            ))
            console.print("[dim green]✓ Gemini response received[/dim green]")

            # Extract function calls if any
            function_call_parts = []
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        function_call_parts.append(part.function_call)

            if function_call_parts:
                for fc in function_call_parts:
                    part = call_function(fc, working_directory, verbose)
                    messages.append(types.Content(role="tool", parts=[part]))
                continue

            if response.text:
                console.print("\n[bold green]✓ Task Complete[/bold green]")
                console.print(Panel(Markdown(response.text), border_style="green"))
                break

            console.print("[yellow]No new action. Continuing...[/yellow]")
            messages.append(types.Content(role="user", parts=[types.Part(text="Continue your process until completion.")]))

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            messages.append(types.Content(role="user", parts=[types.Part(text="Recover and try again.")]))

    loop.close()


# ---------- INTERACTIVE LOOP ----------
def interactive_mode(client, working_directory):
    cwd_short = working_directory[-31:] if len(working_directory) > 31 else working_directory
    console.print(BANNER.format(cwd=cwd_short), style="bold blue")

    if mcp_integration:
        connected = mcp_integration.get_connected_servers()
        console.print(f"[green]🔌 MCP Servers: {', '.join(connected)}[/green]")
    else:
        console.print("[yellow]⚠️ MCP not initialized (native only)[/yellow]")

    console.print("\n[dim]Enter tasks in natural language.[/dim]")
    console.print("[dim]Commands: 'exit', 'clear', '--verbose <cmd>'[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("\n[bold yellow]You[/bold yellow]")
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("\n[bold blue]Goodbye 👋[/bold blue]")
                break
            if user_input.lower() == "clear":
                console.clear()
                console.print(BANNER.format(cwd=cwd_short), style="bold blue")
                continue
            if not user_input.strip():
                continue

            verbose = user_input.startswith("--verbose ")
            if verbose:
                user_input = user_input.replace("--verbose ", "").strip()
            process_request(client, user_input, working_directory, verbose)

        except KeyboardInterrupt:
            console.print("\n[dim]Use 'exit' to quit[/dim]")
        except EOFError:
            console.print("\n[bold blue]Goodbye 👋[/bold blue]")
            break


# ---------- MCP INIT / SHUTDOWN ----------
async def initialize_mcp(servers=None):
    global mcp_integration
    if os.getenv("DISABLE_MCP", "").lower() in ["true", "1", "yes"]:
        console.print("[dim]MCP disabled via env[/dim]")
        return
    try:
        console.print("[cyan]🔌 Initializing MCP...[/cyan]")
        mcp_integration = GentMCPIntegration()
        await mcp_integration.initialize(servers or ["context7"])
        connected = mcp_integration.get_connected_servers()
        if connected:
            console.print(f"[green]✓ MCP ready ({', '.join(connected)})[/green]")
        else:
            console.print("[yellow]No MCP servers connected[/yellow]")
    except Exception as e:
        console.print(f"[yellow]MCP init failed: {e}[/yellow]")
        mcp_integration = None


async def shutdown_mcp():
    global mcp_integration
    if mcp_integration:
        console.print("[cyan]🔌 Shutting down MCP...[/cyan]")
        try:
            await mcp_integration.shutdown()
            console.print("[green]✓ MCP shutdown complete[/green]")
        except Exception as e:
            console.print(f"[yellow]Warning: {e}[/yellow]")
        finally:
            mcp_integration = None


def main():
    working_directory = os.getcwd()
    try:
        asyncio.run(initialize_mcp())
    except Exception as e:
        console.print(f"[yellow]MCP init skipped: {e}[/yellow]")

    try:
        if len(sys.argv) > 1:
            cmd = " ".join(sys.argv[1:])
            verbose = "--verbose" in sys.argv
            cmd = cmd.replace("--verbose", "").strip()
            process_request(client, cmd, working_directory, verbose)
        else:
            interactive_mode(client, working_directory)
    finally:
        if mcp_integration:
            try:
                asyncio.run(shutdown_mcp())
            except:
                pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold blue]Goodbye 👋[/bold blue]")
