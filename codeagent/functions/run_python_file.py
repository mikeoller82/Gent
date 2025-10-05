import os
import subprocess

from google.genai import types


def run_python_file(working_directory, file_path, args=[]):
    try:
        # Create the full path
        full_path = os.path.join(working_directory, file_path)
        
        # Get absolute paths for validation
        abs_full_path = os.path.abspath(full_path)
        abs_working_dir = os.path.abspath(working_directory)
        
        # Ensure the path stays within the working directory
        if not abs_full_path.startswith(abs_working_dir + os.sep) and abs_full_path != abs_working_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        # Check if file exists
        if not os.path.exists(abs_full_path):
            return f'Error: File "{file_path}" not found.'
        
        # Check if it's a Python file
        if not file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file.'
        
        # Run the Python file with subprocess
        result = subprocess.run(
            ['python', abs_full_path] + args,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=abs_working_dir
        )
        
        # Format the output
        output_parts = []
        
        if result.stdout:
            output_parts.append(f"STDOUT:\n{result.stdout}")
        
        if result.stderr:
            output_parts.append(f"STDERR:\n{result.stderr}")
        
        if result.returncode != 0:
            output_parts.append(f"Process exited with code {result.returncode}")
        
        if not output_parts:
            return "No output produced."
        
        return "\n".join(output_parts)
    
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file with optional command-line arguments, constrained to the working directory. Captures stdout and stderr.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional list of command-line arguments to pass to the Python file.",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["file_path"],
    ),
)