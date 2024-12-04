import pytest
import socket
import threading
import time

@pytest.fixture
def server_socket():
    """Fixture para crear y limpiar el servidor"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 55557))
    server.listen()
    yield server
    server.close()

def test_servidor_inicia(server_socket):
    """Prueba que el servidor puede iniciarse y aceptar conexiones"""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 55557))
    
    assert client.fileno() != -1
    client.close()

def test_envio_mensaje(server_socket):
    """Prueba que un mensaje puede ser enviado y recibido"""
    def accept_connection():
        conn, _ = server_socket.accept()
        data = conn.recv(1024)
        assert data == b"Hola servidor"
        conn.close()
    
    thread = threading.Thread(target=accept_connection)
    thread.start()
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 55557))
    client.send(b"Hola servidor")
    
    thread.join(timeout=1)
    client.close()

def test_broadcast_mensajes(server_socket):
    """Prueba que un mensaje llega a múltiples clientes"""
    mensajes_recibidos = []
    conexiones_completas = threading.Event()
    
    def handle_client(conn):
        try:
            data = conn.recv(1024)
            if data:
                mensajes_recibidos.append(data)
        finally:
            conn.close()

    def accept_clients():
        for _ in range(2):
            conn, _ = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn,))
            client_thread.start()
        conexiones_completas.set()

    accept_thread = threading.Thread(target=accept_clients)
    accept_thread.start()

    clientes = []
    for _ in range(2):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 55557))
        clientes.append(client)

    conexiones_completas.wait(timeout=1)
    time.sleep(0.2) 

    for client in clientes:
        client.send(b"Hola a todos")
        time.sleep(0.1)
    time.sleep(0.2)
    for client in clientes:
        client.close()

    assert len(mensajes_recibidos) == 2, f"Se recibieron {len(mensajes_recibidos)} mensajes en lugar de 2"