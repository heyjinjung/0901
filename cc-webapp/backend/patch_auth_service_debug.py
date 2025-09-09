
import os
import sys

# Path to the auth_service.py file
auth_service_path = "app/services/auth_service.py"

# Read the original file
with open(auth_service_path, "r") as file:
    content = file.read()

# Add debug import
if "import logging" not in content:
    content = "import logging\n" + content

# Patch the verify_token function with debug logs
if "verify_token" in content:
    # Find the verify_token function
    start_index = content.find("def verify_token")
    if start_index != -1:
        # Find where to insert our debug logs (after the try: statement)
        try_index = content.find("try:", start_index)
        if try_index != -1:
            # Find the indentation level
            indentation = "    "  # Default indentation
            next_line_index = content.find("\n", try_index) + 1
            if next_line_index != 0:
                next_line_end = content.find("\n", next_line_index)
                if next_line_end != -1:
                    indentation_end = next_line_index
                    while content[indentation_end].isspace():
                        indentation_end += 1
                    indentation = content[next_line_index:indentation_end]
            
            # Insert debug logs after the try: statement
            debug_logs = f"\n{indentation}logging.info(f'Attempting to verify token: {{token}}')\n"
            debug_logs += f"{indentation}logging.info(f'Using secret key: {{SECRET_KEY}}')\n"
            debug_logs += f"{indentation}logging.info(f'Using algorithm: {{ALGORITHM}}')\n"
            
            content = content[:try_index + 5] + debug_logs + content[try_index + 5:]
    
    # Also add logging in the except block
    except_index = content.find("except", start_index)
    if except_index != -1:
        next_line_index = content.find("\n", except_index) + 1
        if next_line_index != 0:
            # Find the indentation level
            indentation_end = next_line_index
            while content[indentation_end].isspace():
                indentation_end += 1
            indentation = content[next_line_index:indentation_end]
            
            # Insert debug logs in the except block
            debug_logs = f"\n{indentation}logging.error(f'Token verification error: {{e}}')\n"
            
            content = content[:next_line_index] + debug_logs + content[next_line_index:]

# Write the modified content back to the file
with open(auth_service_path, "w") as file:
    file.write(content)

print("Added debug logging to auth_service.py")
