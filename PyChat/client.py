# client.py
import socket
import threading
import sys

# Client configuration
HOST = '0.0.0.0'  # The server's hostname or IP address
PORT = 42069         # The port used by the server

def receive_messages(client_socket):
    """
    Listens for messages from the server and prints them.
    """
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                print(f"\n{message.decode().strip()}")
                print("> ", end='', flush=True)
            else:
                # Server closed the connection
                print("\n[INFO] Connection closed by server.")
                client_socket.close()
                break
        except ConnectionAbortedError:
            # The client has closed the connection
            break
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")
            client_socket.close()
            break

def send_messages(client_socket):
    """
    Reads user input and sends messages to the server.
    """
    while True:
        try:
            message = input("> ")
            if message.lower() == 'quit':
                client_socket.close()
                print("[INFO] Disconnected from server.")
                break
            else:
                client_socket.sendall(message.encode())
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")
            client_socket.close()
            break

def main():
    """
    Main function to run the client.
    """
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server
    try:
        client_socket.connect((HOST, PORT))
        print(f"[CONNECTED] Connected to server at {HOST}:{PORT}")
    except ConnectionRefusedError:
        print(f"[ERROR] Unable to connect to server at {HOST}:{PORT}")
        sys.exit()

    # Optionally, set a nickname
    nickname = input("Enter your nickname: ")
    if not nickname:
        nickname = "Anonymous"

    # Send the nickname to the server (optional feature)
    client_socket.sendall(f"[{nickname}] has joined the chat.".encode())

    # Start threads for receiving and sending messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True  # Allows thread to exit when main thread exits
    receive_thread.start()

    send_thread = threading.Thread(target=send_messages, args=(client_socket,))
    send_thread.daemon = True
    send_thread.start()

    # Keep the main thread running, wait for threads to finish
    receive_thread.join()
    send_thread.join()

if __name__ == "__main__":
    main()