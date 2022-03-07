import socket
import select

#This code bases on this youtube tutorial https://www.youtube.com/watch?v=CV7_stUWvBQ

# variables
HEADER_LENGHT = 10
IP = socket.gethostname()
PORT = 9000

# setting the server up
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind(('', PORT))

server_socket.listen(10)

sockets_list = [server_socket]
clients = {}

print(f"Listening connections on {IP}:{PORT}...")


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGHT)

        if not len(message_header):
            return False

        message_lenght = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_lenght)}

    except:
        return False


def main():
    while True:
        read_socket, _, exception_sockets = select.select(
            sockets_list, [], sockets_list)

        for notified_socket in read_socket:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()

                user = receive_message(client_socket)
                if user is False:
                    continue

                sockets_list.append(client_socket)

                clients[client_socket] = user

                print(
                    f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")

            else:
                message = receive_message(notified_socket)

                if message and message['data'].decode("utf-8") == '/q':

                    print(
                        f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                    message = receive_message(notified_socket)

                    for client_socket in clients:
                        #We want to check if current client is different from notified and if so then send the message. We dont want to send the message to its original sender right back
                        if client_socket != notified_socket:
                            client_socket.send(
                                user['header'] + user['data'] + message['header'] + message['data'])
                    sockets_list.remove(notified_socket)
                    continue

                user = clients[notified_socket]

                if message:
                    print(
                        f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

                    for client_socket in clients:
                        #We want to check if current client is different from notified and if so then send the message. We dont want to send the message to its original sender right back
                        if client_socket != notified_socket:
                            client_socket.send(
                                user['header'] + user['data'] + message['header'] + message['data'])

        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]


main()