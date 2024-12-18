import pytest
import socket
import threading
import time

@pytest.fixture
def integration_server():
    """Fixture para pruebas de integración"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 55557))
    server.listen()
    yield server
    server.close()

def test_multiple_clients_chat(integration_server):
    """Prueba la interacción entre múltiples clientes en el chat"""
    mensajes_recibidos = []
    
    def handle_client(conn):
        try:
            while True:
                data = conn.recv(1024)
                if data:
                    mensajes_recibidos.append(data)
                    conn.send(b"OK")
        finally:
            conn.close()

    def accept_clients():
        for _ in range(3):  
            conn, _ = integration_server.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn,))
            client_thread.daemon = True
            client_thread.start()

    accept_thread = threading.Thread(target=accept_clients)
    accept_thread.daemon = True
    accept_thread.start()

    try:
        clients = []
        for i in range(3):
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('127.0.0.1', 55557))
            client.settimeout(1)
            clients.append(client)
            time.sleep(0.1)

        mensaje1 = b"Hola desde cliente 1"
        clients[0].send(mensaje1)
        response = clients[0].recv(1024)
        assert response == b"OK"
        
        mensaje2 = b"Hola desde cliente 2"
        clients[1].send(mensaje2)
        response = clients[1].recv(1024)
        assert response == b"OK"

        time.sleep(0.1)

        assert len(mensajes_recibidos) == 2
        assert mensajes_recibidos[0] == mensaje1
        assert mensajes_recibidos[1] == mensaje2

    finally:
        for client in clients:
            client.close()
        integration_server.close()

def test_message_integrity(integration_server):
    """Prueba que los mensajes no se pierden ni se duplican"""
    mensajes_recibidos = []
    
    def accept_and_handle():
        for _ in range(2):
            conn, _ = integration_server.accept()
            data = conn.recv(1024)
            mensajes_recibidos.append(data)
            conn.send(b"OK")
            conn.close()

    server_thread = threading.Thread(target=accept_and_handle)
    server_thread.daemon = True
    server_thread.start()

    clients = []
    messages = [b"Test1", b"Test2"]
    
    for msg in messages:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(1)
        client.connect(('127.0.0.1', 55557))
        client.send(msg)
        assert client.recv(1024) == b"OK"
        clients.append(client)

    assert len(mensajes_recibidos) == 2
    assert set(mensajes_recibidos) == set(messages)

    for c in clients:
        c.close()
    integration_server.close()

def test_client_disconnection(integration_server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 55557))
    
    client.shutdown(socket.SHUT_RDWR)
    client.close()
    
    conn, _ = integration_server.accept()
    resultado = conn.recv(1024) == b"" 
    conn.close()
    
    assert resultado, "La desconexión no fue detectada"

def test_casos_negativos(integration_server):
    """Prueba casos de error y situaciones negativas"""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with pytest.raises(ConnectionRefusedError):
        client.connect(('127.0.0.1', 55558))
    client.close()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 55557))
    client.close()
    
    with pytest.raises(OSError):
        client.send(b"mensaje despues de desconexion")

    integration_server.close()