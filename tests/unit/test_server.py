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

def test_manejo_desconexion(server_socket):
    """Prueba que el servidor maneja correctamente la desconexión de un cliente"""
    desconexiones = []
    
    def handle_client(conn):
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
        except:
            pass
        finally:
            desconexiones.append(True)
            conn.close()

    def accept_connection():
        conn, _ = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.daemon = True
        client_thread.start()

    accept_thread = threading.Thread(target=accept_connection)
    accept_thread.start()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 55557))
    time.sleep(0.1)
    client.close()

    time.sleep(0.2)
    assert len(desconexiones) == 1, "No se detectó la desconexión del cliente"

def test_recepcion_multiples_clientes(server_socket):
    """Prueba que el servidor puede recibir múltiples clientes"""
    conexiones = []
    clientes_conectados = threading.Event()
    
    def handle_client(conn):
        try:
            usuario = conn.recv(1024).decode('utf-8')
            assert usuario.startswith('usuario'), "No se recibió el formato correcto de usuario"
        finally:
            conn.close()

    def accept_clients():
        for _ in range(3): 
            conn, _ = server_socket.accept()
            conexiones.append(conn)
            client_thread = threading.Thread(target=handle_client, args=(conn,))
            client_thread.start()
        clientes_conectados.set()

    accept_thread = threading.Thread(target=accept_clients)
    accept_thread.start()

    clientes = []
    for i in range(3):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 55557))
        client.send(f"usuario{i}".encode('utf-8'))
        clientes.append(client)
        time.sleep(0.1)

    assert clientes_conectados.wait(timeout=2), "No todos los clientes se conectaron a tiempo"
    assert len(conexiones) == 3, f"Se esperaban 3 conexiones, se recibieron {len(conexiones)}"

    for client in clientes:
        client.close()
    for conn in conexiones:
        conn.close()