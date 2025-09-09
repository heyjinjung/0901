import os
import json

def extract_auth_service():
    # Get the verify_token function from auth_service.py
    with open('/app/app/services/auth_service.py', 'r') as f:
        content = f.read()
    
    # Print environment variables for JWT
    print('Environment variables:')
    print(f"JWT_SECRET_KEY: {os.environ.get('JWT_SECRET_KEY')}")
    print(f"JWT_ALGORITHM: {os.environ.get('JWT_ALGORITHM')}")
    
    # Print the verify_token function
    print('\nAuth service verification code:')
    if 'def verify_token' in content:
        start_index = content.index('def verify_token')
        end_index = content.index('\n    @staticmethod', start_index)
        verify_token_code = content[start_index:end_index]
        print(verify_token_code)
    else:
        print('verify_token function not found')

extract_auth_service()
