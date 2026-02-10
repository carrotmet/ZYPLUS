import urllib.request
import json
import time

# Wait for service to start
print("Waiting for service to start...")
time.sleep(3)

# Test root endpoint
print("\n=== Testing API Endpoints ===")
try:
    req = urllib.request.Request('http://localhost:8000/')
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode())
        print('Root endpoint: OK')
        print(json.dumps(data, ensure_ascii=False, indent=2))
except Exception as e:
    print(f'Root endpoint error: {e}')

# Initialize database
print("\n=== Initializing Database ===")
try:
    data = json.dumps({})
    data = data.encode('utf-8')
    
    req = urllib.request.Request(
        'http://localhost:8000/api/init-data',
        data=data,
        headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode())
        print('Init data: SUCCESS')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
except urllib.error.HTTPError as e:
    print(f'HTTP Error {e.code}: {e.reason}')
    error_body = e.read().decode()
    print(f'Error details: {error_body}')
except Exception as e:
    print(f'Error: {e}')
