import os

from google.genai import types


def write_file(working_directory, file_path, content):
    try:
        # Create the full path
        full_path = os.path.join(working_directory, file_path)
        
        # Get absolute paths for validation
        abs_full_path = os.path.abspath(full_path)
        abs_working_dir = os.path.abspath(working_directory)
        
        # Ensure the path stays within the working directory
        if not abs_full_path.startswith(abs_working_dir + os.sep) and abs_full_path != abs_working_dir:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        
        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(abs_full_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        # Write the content to the file
        with open(abs_full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    
    except Exception as e:
        return f"Error: {str(e)}"
    
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites content to a file, constrained to the working directory. Creates the file if it doesn't exist.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)