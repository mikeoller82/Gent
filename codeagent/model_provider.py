"""
OpenRouter Model Provider for CodeAgent
========================================
Dynamically fetches and selects from ALL available OpenRouter models.
"""

import os
import json
import requests
from typing import Any, Dict, List, Optional
from openai import OpenAI
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


# =============================================================================
# MOCK CLASSES FOR COMPATIBILITY
# =============================================================================

class MockFunctionDeclaration:
    """Mock Gemini FunctionDeclaration for compatibility."""
    def __init__(self, name, description, parameters):
        self.name = name
        self.description = description
        self.parameters = parameters


class MockTool:
    """Mock Gemini Tool for compatibility."""
    def __init__(self, function_declarations):
        self.function_declarations = function_declarations


class MockContent:
    """Mock Gemini Content for compatibility."""
    def __init__(self, role="user", parts=None):
        self.role = role
        self.parts = parts or []


class MockPart:
    """Mock Gemini Part for compatibility."""
    def __init__(self, text="", function_call=None, function_response=None):
        self.text = text
        self.function_call = function_call
        self.function_response = function_response
    
    @staticmethod
    def from_function_response(name, response):
        """Create a function response part."""
        class FunctionResponse:
            def __init__(self, name, response):
                self.name = name
                self.response = response
        
        part = MockPart()
        part.function_response = FunctionResponse(name, response)
        return part


class MockFunctionCall:
    """Mock function call."""
    def __init__(self, name, args):
        self.name = name
        self.args = args


# Mock classes for compatibility with existing code
class MockFunctionDeclaration:
    """Mock Gemini FunctionDeclaration for compatibility."""
    def __init__(self, name, description, parameters):
        self.name = name
        self.description = description
        self.parameters = parameters


class MockTool:
    """Mock Gemini Tool for compatibility."""
    def __init__(self, function_declarations):
        self.function_declarations = function_declarations


class MockContent:
    """Mock Gemini Content for compatibility."""
    def __init__(self, role="user", parts=None):
        self.role = role
        self.parts = parts or []


class MockPart:
    """Mock Gemini Part for compatibility."""
    def __init__(self, text="", function_call=None, function_response=None):
        self.text = text
        self.function_call = function_call
        self.function_response = function_response
    
    @staticmethod
    def from_function_response(name, response):
        """Create a function response part."""
        class FunctionResponse:
            def __init__(self, name, response):
                self.name = name
                self.response = response
        
        part = MockPart()
        part.function_response = FunctionResponse(name, response)
        return part


def fetch_openrouter_models(api_key: str) -> List[Dict[str, Any]]:
    """
    Fetch all available models from OpenRouter API.
    
    Returns:
        List of model dictionaries with id, name, pricing, context_length, etc.
    """
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task(description="Fetching available models from OpenRouter...", total=None)
            
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            models = data.get("data", [])
            
            console.print(f"[green]✓ Found {len(models)} available models[/green]\n")
            return models
    
    except requests.exceptions.RequestException as e:
        console.print(f"[red]✗ Error fetching models: {e}[/red]")
        console.print("[yellow]Using offline model list...[/yellow]\n")
        return []


def select_model_interactive(models: List[Dict[str, Any]]) -> str:
    """
    Interactive model selection with filtering and search.
    
    Returns:
        Selected model ID
    """
    if not models:
        console.print("[red]No models available![/red]")
        return "anthropic/claude-3.5-sonnet"
    
    # Filter for models that support function calling
    function_calling_models = [
        m for m in models 
        if "tool" in m.get("supported_parameters", []) or 
           "tools" in m.get("supported_parameters", [])
    ]
    
    if not function_calling_models:
        console.print("[yellow]Warning: No models with verified function calling support found[/yellow]")
        function_calling_models = models
    
    console.print(f"[bold cyan]OpenRouter Models[/bold cyan] ({len(function_calling_models)} models with function calling)\n")
    
    # Ask for filter
    console.print("[dim]Filter options:[/dim]")
    console.print("  1. Show all models")
    console.print("  2. Free models only")
    console.print("  3. Cheap models (< $0.50 per 1M tokens)")
    console.print("  4. Premium models (Claude, GPT-4, etc.)")
    console.print("  5. Search by name\n")
    
    filter_choice = Prompt.ask(
        "[yellow]Select filter[/yellow]",
        choices=["1", "2", "3", "4", "5"],
        default="3"
    )
    
    # Apply filter
    filtered_models = function_calling_models.copy()
    
    if filter_choice == "2":
        # Free models
        filtered_models = [
            m for m in filtered_models
            if m.get("pricing", {}).get("prompt", "0") == "0" and
               m.get("pricing", {}).get("completion", "0") == "0"
        ]
        console.print(f"\n[green]Showing {len(filtered_models)} free models[/green]\n")
    
    elif filter_choice == "3":
        # Cheap models (< $0.50 per 1M tokens)
        filtered_models = [
            m for m in filtered_models
            if float(m.get("pricing", {}).get("prompt", "999")) * 1000000 < 0.50
        ]
        console.print(f"\n[green]Showing {len(filtered_models)} cheap models[/green]\n")
    
    elif filter_choice == "4":
        # Premium models
        premium_keywords = ["claude", "gpt-4", "gemini-2", "o1", "o3"]
        filtered_models = [
            m for m in filtered_models
            if any(kw in m.get("id", "").lower() for kw in premium_keywords)
        ]
        console.print(f"\n[green]Showing {len(filtered_models)} premium models[/green]\n")
    
    elif filter_choice == "5":
        # Search
        search_term = Prompt.ask("[yellow]Enter search term[/yellow]").lower()
        filtered_models = [
            m for m in filtered_models
            if search_term in m.get("id", "").lower() or
               search_term in m.get("name", "").lower()
        ]
        console.print(f"\n[green]Found {len(filtered_models)} matching models[/green]\n")
    
    if not filtered_models:
        console.print("[red]No models match your filter. Showing all models.[/red]\n")
        filtered_models = function_calling_models
    
    # Sort by cost (cheapest first)
    filtered_models.sort(key=lambda m: float(m.get("pricing", {}).get("prompt", "999")))
    
    # Limit display to 50 models for readability
    display_models = filtered_models[:50]
    if len(filtered_models) > 50:
        console.print(f"[yellow]Showing first 50 of {len(filtered_models)} models[/yellow]\n")
    
    # Create table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Model ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Context", justify="right")
    table.add_column("Cost/1M", justify="right")
    
    for idx, model in enumerate(display_models, 1):
        model_id = model.get("id", "unknown")
        model_name = model.get("name", "Unknown")
        context_length = model.get("context_length", 0)
        
        pricing = model.get("pricing", {})
        prompt_cost = float(pricing.get("prompt", 0))
        completion_cost = float(pricing.get("completion", 0))
        
        # Format context length
        if context_length >= 1000000:
            context_str = f"{context_length//1000000}M"
        elif context_length >= 1000:
            context_str = f"{context_length//1000}K"
        else:
            context_str = str(context_length)
        
        # Format cost
        if prompt_cost == 0 and completion_cost == 0:
            cost_str = "[green]FREE[/green]"
        else:
            input_cost = prompt_cost * 1000000
            output_cost = completion_cost * 1000000
            cost_str = f"${input_cost:.2f}/${output_cost:.2f}"
        
        # Shorten model name if too long
        if len(model_name) > 30:
            model_name = model_name[:27] + "..."
        
        table.add_row(
            str(idx),
            model_id,
            model_name,
            context_str,
            cost_str
        )
    
    console.print(table)
    
    # Get selection
    console.print("\n[dim]Recommended: 1 (cheapest), or search for specific model[/dim]")
    choice = Prompt.ask(
        "[yellow]Select model number[/yellow]",
        default="1"
    )
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(display_models):
            selected = display_models[idx]
            console.print(f"\n[green]✓ Selected: {selected['name']} ({selected['id']})[/green]")
            return selected["id"]
        else:
            console.print("[red]Invalid selection. Using first model.[/red]")
            return display_models[0]["id"]
    except ValueError:
        console.print("[red]Invalid input. Using first model.[/red]")
        return display_models[0]["id"]


class OpenRouterProvider:
    """OpenRouter provider using OpenAI SDK."""
    
    def __init__(self, api_key: str, model_id: str):
        self.api_key = api_key
        self.model_id = model_id
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/yourusername/codeagent",
                "X-Title": "CodeAgent",
            }
        )
        
        console.print(f"[dim]Using model: {model_id}[/dim]\n")
    
    def generate_content(
        self,
        messages: List[Any],
        tools: Optional[List[Any]] = None,
        system_instruction: Optional[str] = None,
    ) -> Any:
        """Generate content via OpenRouter."""
        # Convert messages to OpenAI format
        openai_messages = []
        
        # Add system message if provided
        if system_instruction:
            openai_messages.append({
                "role": "system",
                "content": system_instruction
            })
        
        # Convert Gemini-style messages to OpenAI format
        for msg in messages:
            # Handle both dict and MockContent objects
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                parts = msg.get("parts", [])
            else:
                role = getattr(msg, "role", "user")
                parts = getattr(msg, "parts", [])
            
            # Handle different message types
            if role == "tool":
                # Tool response
                for part in parts:
                    if hasattr(part, "function_response"):
                        openai_messages.append({
                            "role": "tool",
                            "tool_call_id": part.function_response.name,
                            "content": str(part.function_response.response.get("result", ""))
                        })
            else:
                # Regular message or function call
                content_parts = []
                tool_calls = []
                
                for part in parts:
                    if hasattr(part, "text"):
                        content_parts.append(part.text)
                    elif hasattr(part, "function_call"):
                        import json
                        tool_calls.append({
                            "id": f"call_{part.function_call.name}",
                            "type": "function",
                            "function": {
                                "name": part.function_call.name,
                                "arguments": json.dumps(dict(part.function_call.args))
                            }
                        })
                
                msg_dict = {
                    "role": "assistant" if role == "model" else role,
                }
                
                if content_parts:
                    msg_dict["content"] = " ".join(content_parts)
                
                if tool_calls:
                    msg_dict["tool_calls"] = tool_calls
                
                openai_messages.append(msg_dict)
        
        # Build request parameters
        params = {
            "model": self.model_id,
            "messages": openai_messages,
        }
        
        # Add tools if provided
        if tools:
            openai_tools = self._convert_tools_to_openai(tools)
            params["tools"] = openai_tools
            params["tool_choice"] = "auto"
        
        # Make API call
        try:
            response = self.client.chat.completions.create(**params)
            return self._convert_response_to_gemini_format(response)
        except Exception as e:
            console.print(f"[red]API Error: {e}[/red]")
            raise
    
    def _convert_tools_to_openai(self, gemini_tools: List[Any]) -> List[Dict[str, Any]]:
        """Convert Gemini tool format to OpenAI format."""
        openai_tools = []
        
        for tool in gemini_tools:
            if hasattr(tool, "function_declarations"):
                for func_decl in tool.function_declarations:
                    openai_tools.append({
                        "type": "function",
                        "function": {
                            "name": func_decl.name,
                            "description": func_decl.description,
                            "parameters": func_decl.parameters
                        }
                    })
        
        return openai_tools
    
    def _convert_response_to_gemini_format(self, openai_response: Any) -> Any:
        """Convert OpenAI response to Gemini-like format for compatibility."""
        # Create a mock Gemini response structure
        class MockResponse:
            def __init__(self):
                self.candidates = []
                self.text = ""
        
        class MockCandidate:
            def __init__(self):
                self.content = MockContent()
        
        class MockContent:
            def __init__(self):
                self.parts = []
                self.role = "model"
        
        class MockPart:
            def __init__(self):
                self.text = ""
                self.function_call = None
        
        class MockFunctionCall:
            def __init__(self, name, args):
                self.name = name
                self.args = args
        
        response = MockResponse()
        candidate = MockCandidate()
        
        choice = openai_response.choices[0]
        message = choice.message
        
        # Handle text content
        if message.content:
            part = MockPart()
            part.text = message.content
            candidate.content.parts.append(part)
            response.text = message.content
        
        # Handle function calls
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                part = MockPart()
                part.function_call = MockFunctionCall(
                    name=tool_call.function.name,
                    args=json.loads(tool_call.function.arguments)
                )
                candidate.content.parts.append(part)
        
        response.candidates = [candidate]
        return response


def initialize_openrouter(api_key: Optional[str] = None) -> OpenRouterProvider:
    """
    Initialize OpenRouter provider with model selection.
    
    Args:
        api_key: OpenRouter API key (or reads from OPENROUTER_API_KEY env var)
    
    Returns:
        OpenRouterProvider instance
    """
    # Get API key
    if api_key is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        console.print("[red]✗ OPENROUTER_API_KEY not set![/red]")
        console.print("[yellow]Get your free API key at: https://openrouter.ai/keys[/yellow]")
        console.print("[yellow]Then add to .env file: OPENROUTER_API_KEY=your-key-here[/yellow]\n")
        raise ValueError("OPENROUTER_API_KEY not set")
    
    console.print("[cyan]Initializing OpenRouter...[/cyan]\n")
    
    # Fetch available models
    models = fetch_openrouter_models(api_key)
    
    if not models:
        console.print("[yellow]Using fallback model: deepseek/deepseek-chat[/yellow]\n")
        model_id = "deepseek/deepseek-chat"
    else:
        # Let user select model
        model_id = select_model_interactive(models)
    
    # Create provider
    return OpenRouterProvider(api_key, model_id)