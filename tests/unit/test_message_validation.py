import pytest
import socket
import threading
import time

def test_validacion_mensaje_vacio():
    """Prueba que el servidor rechaza mensajes vacios"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 55557))
    server.listen()
    
    def handle_client(conn):
        try:
            data = conn.recv(1024)
            if len(data.strip()) == 0:
                conn.send(b"ERROR")
            else:
                conn.send(b"OK")
        except Exception as e:
            print(f"Error en handle_client: {e}")
        finally:
            conn.close()

    server_thread = threading.Thread(target=lambda: handle_client(server.accept()[0]))
    server_thread.daemon = True
    server_thread.start()

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(1) 
        client.connect(('127.0.0.1', 55557))
        
        client.send(b"   ")
        response = client.recv(1024)
        assert response == b"ERROR"
    finally:
        client.close()
        server.close()
        server_thread.join(timeout=1)