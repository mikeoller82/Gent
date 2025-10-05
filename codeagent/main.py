import os
import sys
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
║            AI-Powered Coding Agent                           ║
║            Working Directory: {cwd:<31} ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""



load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

# Map function names to actual functions
FUNCTION_MAP = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

# Create available functions tool
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

system_prompt = """
You are a PERSISTENT autonomous AI coding agent. You NEVER give up until the task is COMPLETE and VERIFIED.

AVAILABLE FUNCTIONS:
- get_files_info(directory): List files and directories
- get_file_content(file_path): Read file contents  
- run_python_file(file_path, args): Execute Python files
- write_file(file_path, content): Write or overwrite files

MANDATORY WORKFLOW:
1. EXPLORE: Use get_files_info and get_file_content to understand the codebase
2. ANALYZE: Identify what needs to be done
3. IMPLEMENT: Make the necessary changes with write_file
4. VERIFY: Run tests or execute code to verify changes work
5. FIX: If verification fails, analyze errors and fix them
6. REPEAT steps 4-5 until verification passes
7. REPORT: Only when task is complete and verified

CRITICAL RULES:
✓ NEVER stop until the task is complete AND verified to work
✓ ALWAYS test your changes (run code, check output)
✓ If tests fail, analyze the error, fix it, and test again
✓ Keep iterating through fix-test cycles until it works
✓ Make actual code changes - don't just suggest them
✓ Be thorough in your exploration
✓ Fix ALL errors you encounter

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

def call_function(function_call_part, working_directory, verbose=False):
    """Execute a function call from the LLM."""
    function_name = function_call_part.name
    function_args = dict(function_call_part.args)
    
    # Print function call
    if verbose:
        console.print(f"[cyan]→ Calling: {function_name}({function_args})[/cyan]")
    else:
        console.print(f"[dim cyan]→ {function_name}[/dim cyan]")
    
    # Check if function exists
    if function_name not in FUNCTION_MAP:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
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
    
    # Return the result as a Content object
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
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
                    
                    # Print function call
                    if verbose:
                        console.print(f"[cyan]→ Calling: {func_name}({func_args})[/cyan]")
                    else:
                        console.print(f"[dim cyan]→ {func_name}[/dim cyan]")
                    
                    # Check if function exists
                    if func_name not in FUNCTION_MAP:
                        function_response_parts.append(
                            types.Part.from_function_response(
                                name=func_name,
                                response={"error": f"Unknown function: {func_name}"},
                            )
                        )
                        continue
                    
                    # Handle write_file with diff display
                    if func_name == "write_file":
                        file_path = func_args.get("file_path", "")
                        new_content = func_args.get("content", "")
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
                    func_args["working_directory"] = working_directory
                    
                    # Call the actual function
                    function = FUNCTION_MAP[func_name]
                    function_result = function(**func_args)
                    
                    # Show success/failure for write operations
                    if func_name == "write_file":
                        if "Successfully wrote" in function_result:
                            console.print(f"[green]✓ {function_result}[/green]")
                        else:
                            console.print(f"[red]✗ {function_result}[/red]")
                    
                    # Show verbose result for other functions
                    if verbose and func_name != "write_file":
                        result_str = str(function_result)
                        if len(result_str) > 200:
                            console.print(f"[dim]  Result: {result_str[:200]}...[/dim]")
                        else:
                            console.print(f"[dim]  Result: {result_str}[/dim]")
                    
                    # Create function response part (NOT a full Content object)
                    function_response_parts.append(
                        types.Part.from_function_response(
                            name=func_name,
                            response={"result": function_result},
                        )
                    )
                
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
    
    console.print("[dim]Type your requests in natural language.[/dim]")
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


def main():
    """Main entry point for the CLI."""
    # Get current working directory
    working_directory = os.getcwd()
    
    # Use the already initialized client from module level
    # (client is initialized at the top of the file with the API key)
    
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


if __name__ == "__main__":
    main()