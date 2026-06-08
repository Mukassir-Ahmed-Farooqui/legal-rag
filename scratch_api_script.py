import urllib.request
import json
import random
import tempfile, os

email = f'test{random.randint(1,10000)}@example.com'
password = 'password123'
print('Registering user', email)
req_reg = urllib.request.Request('http://localhost:8000/api/v1/auth/register', data=json.dumps({'email': email, 'password': password, 'full_name': 'Test User'}).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    urllib.request.urlopen(req_reg)
except Exception: pass

req_login = urllib.request.Request('http://localhost:8000/api/v1/auth/login', data=json.dumps({'email': email, 'password': password}).encode('utf-8'), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req_login) as response:
    token = json.loads(response.read()).get('access_token')

fd, path = tempfile.mkstemp()
with os.fdopen(fd, 'w') as f:
    f.write('hello world')

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = (
    b'--' + boundary.encode() + b'\r\n' +
    b'Content-Disposition: form-data; name="file"; filename="test.pdf"\r\n' +
    b'Content-Type: application/pdf\r\n\r\n' +
    b'hello world\r\n' +
    b'--' + boundary.encode() + b'--\r\n'
)
req_up = urllib.request.Request('http://localhost:8000/api/v1/upload', data=body, headers={'Authorization': f'Bearer {token}', 'Content-Type': f'multipart/form-data; boundary=' + boundary})
try:
    with urllib.request.urlopen(req_up) as r_up:
        print('Upload:', r_up.read())
except Exception as e: print('Upload err:', getattr(e, 'read', lambda: b'')())

req_docs = urllib.request.Request('http://localhost:8000/api/v1/documents', headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req_docs) as r_docs:
    docs = json.loads(r_docs.read())
    doc_ids = [d['doc_id'] for d in docs]
    print(f'Docs: {doc_ids}')
    
    req_chat = urllib.request.Request('http://localhost:8000/api/v1/chats', data=json.dumps({'selected_doc_ids': doc_ids}).encode('utf-8'), headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req_chat) as r_chat:
            print('Chat create:', r_chat.read())
    except Exception as e:
        print('Chat error:', getattr(e, 'read', lambda: b'')())
