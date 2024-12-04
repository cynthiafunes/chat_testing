import threading
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 55556))
server.listen()

clientes = []
usuarios = []

def broadcast(mensaje, cliente_emisor):
    for cliente in clientes:
        if cliente != cliente_emisor:
            cliente.send(mensaje)

def manejo(cliente):
    while True:
        try:
            mensaje = cliente.recv(1024)
            broadcast(mensaje,cliente)
        except: 
            indice = clientes.index(cliente)
            clientes.remove(cliente)
            cliente.close()
            usuario = usuarios[indice]
            broadcast(f'- {usuario} abandonó el chat -'.encode('utf-8'), None)
            usuarios.remove(usuario)
            print(f"{usuario} se ha desconectado")
            break 

def recepcion():
    while True:
        cliente, direccion = server.accept()
        print(f'Conectado con {direccion}')

        cliente.send('usuario'.encode('utf-8'))
        usuario = cliente.recv(1024).decode('utf-8')
        usuarios.append(usuario)
        clientes.append(cliente)

        print(f'Usuario = {usuario}')
        broadcast(f'- {usuario} se ha unido al chat -'.encode('utf-8'),cliente)
        cliente.send('Conectado al servidor'.encode('utf-8'))

        hilo = threading.Thread(target=manejo, args=(cliente,))
        hilo.start()

print("El servidor está escuchando..")
recepcion()