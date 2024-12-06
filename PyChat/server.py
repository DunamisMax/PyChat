# server.py
import socket
import threading

# Server configuration
HOST = "0.0.0.0"  # Accept connections on all IPv4 addresses
PORT = 42069  # Port to listen on (must match client's PORT)

# Dictionary to keep track of connected clients {socket: nickname}
clients = {}


def broadcast(message, sender_socket=None):
    """
    Sends a message to all connected clients.
    If sender_socket is provided, the message will not be sent back to the sender.
    """
    for client_socket in clients:
        if client_socket != sender_socket:
            try:
                client_socket.sendall(message.encode())
            except:
                # If sending fails, remove the client
                remove_client(client_socket)


def handle_client(client_socket, client_address):
    """
    Handles communication with a connected client.
    """
    print(f"[NEW CONNECTION] {client_address} connected.")

    try:
        # Receive the nickname from the client
        nickname_data = client_socket.recv(1024)
        nickname = nickname_data.decode().strip()
        if not nickname:
            nickname = "Anonymous"
        # Add the client to the clients dictionary
        clients[client_socket] = nickname
        print(f"[NICKNAME] {client_address} is now known as {nickname}")
        # Notify all clients that a new user has joined
        broadcast(f"[{nickname}] has joined the chat.")

        while True:
            # Receive message from client
            message_data = client_socket.recv(1024)
            if message_data:
                message = message_data.decode().strip()
                # Print message to server console
                print(f"[{nickname}] - {message}")
                # Broadcast the message to other clients
                broadcast(f"[{nickname}] {message}", sender_socket=client_socket)
            else:
                # No message indicates disconnection
                remove_client(client_socket)
                break
    except ConnectionResetError:
        # Handle abrupt disconnection
        remove_client(client_socket)
    except Exception as e:
        print(f"[ERROR] An error occurred with {client_address}: {e}")
        remove_client(client_socket)


def remove_client(client_socket):
    """
    Removes a client from the clients dictionary and closes the connection.
    """
    nickname = clients.get(client_socket, "Unknown")
    if client_socket in clients:
        del clients[client_socket]
        client_socket.close()
        print(f"[DISCONNECTED] {nickname} has disconnected.")
        # Notify all clients that the user has left
        broadcast(f"[{nickname}] has left the chat.")


def start_server():
    """
    Starts the server and listens for incoming connections.
    """
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow the server to reuse the address
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the address and port
    server_socket.bind((HOST, PORT))

    # Listen for incoming connections
    server_socket.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    try:
        while True:
            # Accept a new client connection
            client_socket, client_address = server_socket.accept()

            # Start a new thread to handle the client
            client_thread = threading.Thread(
                target=handle_client, args=(client_socket, client_address)
            )
            client_thread.daemon = (
                True  # Optional: allows thread to exit when main thread exits
            )
            client_thread.start()

            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server is shutting down.")
    finally:
        # Close all client sockets
        for client_socket in clients:
            client_socket.close()
        server_socket.close()


if __name__ == "__main__":
    print("[STARTING] Server is starting...")
    start_server()
