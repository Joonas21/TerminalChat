import socket
import errno
import sys

#This code bases on this youtube tutorial https://www.youtube.com/watch?v=ytu2yV3Gn1I

# variables
HEADER_LENGHT = 10
IP = "127.0.0.1"
PORT = 9000


def main():
    print(f"Welcome to terminal chat!\n")
    my_username = input("Give username: ")
    IP = input("Give room ip (default is 127.0.0.1): ")
    print(
        f"\nYou have connected to {IP}. To update the chat, press ENTER, to leave type /q, to PM someone type @username at the start of the message.\n")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)

    encoded_username = my_username.encode("utf-8")
    username_header = f"{len(encoded_username):<{HEADER_LENGHT}}".encode("utf-8")
    client_socket.send(username_header + encoded_username)

#Here we wanna both send and receive messages

    while True:
        message = input(f"<{my_username}> ")

        #Checks if the message actually contains something, not only pressed enter on empty row

        if message:

            message = message.encode("utf-8")
            message_header = f"{len(message):<{HEADER_LENGHT}}".encode("utf-8")
            client_socket.send(message_header + message)

            if message.decode("utf-8") == "/q":
                print("You have left the chat.")
                message = "has left the chat"
                message = message.encode("utf-8")
                message_header = f"{len(message):<{HEADER_LENGHT}}".encode("utf-8")
                client_socket.send(message_header + message)
                sys.exit()

       #We are basicly fetching for messages till we get an error that's why we use try except here

        try:
            while True:
                username_header = client_socket.recv(HEADER_LENGHT)
                if not len(username_header):
                    print("Connection closed by the server")
                    sys.exit()

                #We determine the lenght of the username so we know how long of a message we are about to receive from the server

                username_lenght = int(username_header.decode("utf-8").strip())
                username = client_socket.recv(username_lenght).decode("utf-8")

                message_header = client_socket.recv(HEADER_LENGHT)
                message_lenght = int(message_header.decode("utf-8").strip())
                message = client_socket.recv(message_lenght).decode("utf-8")

                splitmessage = message.split()
                if message == "has left the chat":
                    print(f"User {username} has left the chat.")

                elif (splitmessage[0][0] == "@") and (splitmessage[0] != "@"+my_username):
                    pass

                elif (splitmessage[0][0] == "@") and (splitmessage[0] == "@"+my_username):
                    message = "PM:"
                    for piece in splitmessage:
                        if piece[0] == "@":
                            continue
                        else:
                            message = message + " " + piece
                            print(f"<{username}> {message}")

                else:
                    print(f"<{username}> {message}")

        #We are excepting this error as it show for us that theres no more messages to receive

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print(str(e))
                sys.exit()
            continue

        #This is the actual error handling

        except Exception as e:
            print(str(e))
            sys.exit()


main()