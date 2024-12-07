# server.py

import socket
import threading
import argparse
import sys
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("chat_server.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# Dictionary to keep track of connected clients {socket: (nickname, address)}
clients = {}

# Rate limiting configurations
RATE_LIMIT = 5  # max messages
RATE_LIMIT_PERIOD = 10  # time window in seconds

# Maximum message size in bytes
MAX_MESSAGE_SIZE = 1024  # 1KB

# Maximum concurrent connections
MAX_CONNECTIONS = 100


def broadcast(message, sender_socket=None):
    """
    Sends a message to all connected clients.
    If sender_socket is provided, the message will not be sent back to the sender.
    """
    for client_socket in list(clients.keys()):
        if client_socket != sender_socket:
            try:
                client_socket.sendall(message.encode("utf-8"))
            except Exception as e:
                logging.error(
                    f"Error sending message to {clients[client_socket][0]}: {e}"
                )
                # If sending fails, remove the client
                remove_client(client_socket)


def handle_client(client_socket, client_address):
    """
    Handles communication with a connected client.
    """
    logging.info(f"[NEW CONNECTION] {client_address} connected.")

    # Rate limiting data: {timestamp: message count}
    message_times = []

    try:
        # Receive the nickname from the client
        nickname_data = client_socket.recv(1024)
        nickname = nickname_data.decode("utf-8").strip()
        if not nickname:
            nickname = "Anonymous"

        # Check if nickname is already taken
        nicknames = [info[0] for info in clients.values()]
        if nickname in nicknames:
            client_socket.sendall(
                "[SERVER] Nickname already taken. Please reconnect with a different nickname.".encode(
                    "utf-8"
                )
            )
            client_socket.close()
            return

        # Add the client to the clients dictionary
        clients[client_socket] = (nickname, client_address)
        logging.info(f"[NICKNAME] {client_address} is now known as {nickname}")

        # Notify all clients that a new user has joined
        broadcast(f"[{nickname}] has joined the chat.")
        client_socket.sendall(
            "[SERVER] You have joined the chat. Type 'quit' to exit.".encode("utf-8")
        )

        while True:
            # Receive message from client
            message_data = client_socket.recv(MAX_MESSAGE_SIZE)
            if message_data:
                # Limit message size
                if len(message_data) > MAX_MESSAGE_SIZE:
                    client_socket.sendall(
                        "[SERVER] Message too long. Please limit your messages to 1KB.".encode(
                            "utf-8"
                        )
                    )
                    continue

                message = message_data.decode("utf-8").strip()

                # Sanitize message (for this example, we'll just strip control characters)
                sanitized_message = "".join(ch for ch in message if ch.isprintable())

                # Rate limiting
                current_time = time.time()
                # Remove timestamps older than RATE_LIMIT_PERIOD
                message_times = [
                    t for t in message_times if current_time - t < RATE_LIMIT_PERIOD
                ]
                if len(message_times) >= RATE_LIMIT:
                    client_socket.sendall(
                        "[SERVER] Message rate limit exceeded. Please slow down.".encode(
                            "utf-8"
                        )
                    )
                    continue
                else:
                    message_times.append(current_time)

                if sanitized_message.lower() == "quit":
                    # Client initiated disconnect
                    remove_client(client_socket)
                    break
                else:
                    # Log the message
                    logging.info(f"[{nickname}] {sanitized_message}")
                    # Broadcast the message to other clients
                    broadcast(
                        f"[{nickname}] {sanitized_message}", sender_socket=client_socket
                    )
            else:
                # No message indicates disconnection
                remove_client(client_socket)
                break
    except ConnectionResetError:
        # Handle abrupt disconnection
        remove_client(client_socket)
    except Exception as e:
        logging.error(f"An error occurred with {client_address}: {e}")
        remove_client(client_socket)


def remove_client(client_socket):
    """
    Removes a client from the clients dictionary and closes the connection.
    """
    nickname = clients.get(client_socket, ("Unknown", None))[0]
    if client_socket in clients:
        del clients[client_socket]
        client_socket.close()
        logging.info(f"[DISCONNECTED] {nickname} has disconnected.")
        # Notify all clients that the user has left
        broadcast(f"[{nickname}] has left the chat.")


def start_server(host, port):
    """
    Starts the server and listens for incoming connections.
    """
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow the server to reuse the address
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the address and port
    try:
        server_socket.bind((host, port))
    except OSError as e:
        logging.error(f"Could not bind to {host}:{port}. Error: {e}")
        sys.exit()

    # Listen for incoming connections
    server_socket.listen()
    logging.info(f"[LISTENING] Server is listening on {host}:{port}")

    try:
        while True:
            # Accept a new client connection
            client_socket, client_address = server_socket.accept()

            # Check for maximum connections
            if len(clients) >= MAX_CONNECTIONS:
                client_socket.sendall(
                    "[SERVER] Server is full. Try again later.".encode("utf-8")
                )
                client_socket.close()
                logging.warning(
                    f"[CONNECTION REJECTED] {client_address} - Server is full."
                )
                continue

            # Start a new thread to handle the client
            client_thread = threading.Thread(
                target=handle_client, args=(client_socket, client_address)
            )
            client_thread.daemon = True  # Allows thread to exit when main thread exits
            client_thread.start()

            logging.info(f"[ACTIVE CONNECTIONS] {len(clients)}/{MAX_CONNECTIONS}")
    except KeyboardInterrupt:
        logging.info("[SHUTDOWN] Server is shutting down.")
    finally:
        # Close all client sockets
        for client_socket in list(clients.keys()):
            client_socket.close()
        server_socket.close()


if __name__ == "__main__":
    logging.info("[STARTING] Server is starting...")

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Chat server")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Server IP address to bind to"
    )
    parser.add_argument(
        "--port", type=int, default=42069, help="Server port to listen on"
    )
    args = parser.parse_args()

    HOST = args.host
    PORT = args.port

    start_server(HOST, PORT)
