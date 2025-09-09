import os

def extract_config():
    # Get the SECRET_KEY and ALGORITHM variables from auth_service.py
    with open('/app/app/services/auth_service.py', 'r') as f:
        content = f.read()
    
    # Find the SECRET_KEY line
    import re
    secret_key_match = re.search(r'SECRET_KEY\s*=\s*(.*)', content)
    if secret_key_match:
        print(f'SECRET_KEY definition: {secret_key_match.group(0)}')
    else:
        print('SECRET_KEY not found')
    
    # Find the ALGORITHM line
    algorithm_match = re.search(r'ALGORITHM\s*=\s*(.*)', content)
    if algorithm_match:
        print(f'ALGORITHM definition: {algorithm_match.group(0)}')
    else:
        print('ALGORITHM not found')

extract_config()
