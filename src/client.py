import socket
import threading

usuario = input("Elige tu usuario: ")

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(('127.0.0.1', 55556))

def recepcion():
    while True:
        try:
            mensaje = cliente.recv(1024).decode('utf-8')
            if mensaje == 'usuario':
                cliente.send(usuario.encode('utf-8'))
            else:
                print(mensaje)
        except:
            print("Ocurrió un error, intentando reconectar..")
            try:
                cliente.connect(('127.0.0.1', 55556))
                cliente.send(usuario.encode('utf-8'))
            except:
                print("Fallo al reconectar al servidor. Saliendo del chat.")
                cliente.close()
                break

def escribir():
    while True:
        mensaje = f'{usuario}: {input("")}'
        cliente.send(mensaje.encode('utf-8'))

thread_recepcion = threading.Thread(target=recepcion)
thread_recepcion.start()

thread_escribir = threading.Thread(target=escribir)
thread_escribir.start()