import socket
import os
from datetime import datetime

HOST = '127.0.0.1'
PORT = 8080

STATIC_DIR = 'static'
LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'server.log')

# Создание папки logs
os.makedirs(LOG_DIR, exist_ok=True)


def log_request(method, path, status):
    with open(LOG_FILE, 'a', encoding='utf-8') as log:
        log.write(
            f'[{datetime.now()}] {method} {path} -> {status}\n'
        )


def build_response(status_code, body, content_type='text/html'):
    status_messages = {
        200: 'OK',
        404: 'Not Found'
    }

    status_text = status_messages.get(status_code, 'OK')

    response = (
        f'HTTP/1.1 {status_code} {status_text}\n'
        f'Content-Type: {content_type}; charset=utf-8\n\n'
        f'{body}'
    )

    return response.encode('utf-8')


def get_file_content(path):
    full_path = os.path.join(STATIC_DIR, path.strip('/'))

    if os.path.isfile(full_path):
        with open(full_path, 'r', encoding='utf-8') as file:
            return file.read(), 200
    else:
        return """
        <h1>404 Not Found</h1>
        <p>Страница не найдена</p>
        """, 404


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f'Server started: http://{HOST}:{PORT}')

while True:
    client_socket, client_address = server_socket.accept()

    request = client_socket.recv(1024).decode('utf-8')

    if not request:
        client_socket.close()
        continue

    request_line = request.split('\n')[0]
    method, path, _ = request_line.split()

    print(f'Request: {method} {path}')

    if path == '/':
        path = '/index.html'

    content, status = get_file_content(path)

    if path.endswith('.css'):
        content_type = 'text/css'
    else:
        content_type = 'text/html'

    response = build_response(status, content, content_type)

    client_socket.sendall(response)

    log_request(method, path, status)

    client_socket.close()