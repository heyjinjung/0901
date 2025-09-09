# Script to add debug logging to auth_service.py
import os

# Path to auth_service.py
auth_service_path = '/app/app/services/auth_service.py'

# Read the file
with open(auth_service_path, 'r') as f:
    content = f.read()

# Find the verify_token method
verify_token_start = content.find('def verify_token')
if verify_token_start == -1:
    print("verify_token method not found")
    exit(1)

# Find the start of the method body (after the first line)
method_body_start = content.find('\n', verify_token_start) + 1

# Insert debug logging at the beginning of the method body
debug_logging = '''        print("=== DEBUG: verify_token called ===")
        print(f"Token: {token[:30]}...")
        try:
            # Debug: Try decoding without verification
            import json, base64
            token_parts = token.split('.')
            if len(token_parts) == 3:
                header_raw, payload_raw, sig = token_parts
                try:
                    header_json = base64.b64decode(header_raw + "=" * ((4 - len(header_raw) % 4) % 4)).decode('utf-8')
                    payload_json = base64.b64decode(payload_raw + "=" * ((4 - len(payload_raw) % 4) % 4)).decode('utf-8')
                    print(f"Debug header: {header_json}")
                    print(f"Debug payload: {payload_json}")
                except Exception as e:
                    print(f"Debug decode error: {e}")
        except Exception as debug_e:
            print(f"Debug error: {debug_e}")
'''

# Insert the debug logging
modified_content = content[:method_body_start] + debug_logging + content[method_body_start:]

# Write the modified file
with open(auth_service_path, 'w') as f:
    f.write(modified_content)

print("Added debug logging to auth_service.py")
