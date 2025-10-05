import os
from google.genai import types

from codeagent.config import MAX_FILE_CHARS

def get_file_content(working_directory, file_path):
    try:
        full_path = os.path.join(working_directory, file_path)
        abs_full_path = os.path.abspath(full_path)
        abs_working_dir = os.path.abspath(working_directory)
        
        if not abs_full_path.startswith(abs_working_dir + os.sep) and abs_full_path != abs_working_dir:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.isfile(abs_full_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        
        with open(abs_full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) > MAX_FILE_CHARS:
            content = content[:MAX_FILE_CHARS]
            content += f'[...File "{file_path}" truncated at {MAX_FILE_CHARS} characters]'
        
        return content
    
    except Exception as e:
        return f"Error: {str(e)}"


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads and returns the contents of a file, constrained to the working directory. Files longer than 10000 characters will be truncated.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)