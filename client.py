import socket
import threading
import sys
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def receive_messages(conn: socket.socket, stop_event: threading.Event) -> None:
    """
    Continuously receives and displays messages from the server.
    If the connection is lost or closed, notify the user and set stop_event.
    """
    while not stop_event.is_set():
        try:
            data = conn.recv(1024)
            if not data:
                # Connection closed by server
                logging.info("Connection closed by the server.")
                stop_event.set()
                break

            message = data.decode().rstrip("\n")
            # Print the received message on a new line
            sys.stdout.write(f"\n{message}\nYou> ")
            sys.stdout.flush()

        except Exception as e:
            logging.warning(f"Connection lost. Error: {e}")
            stop_event.set()
            break


def main():
    """
    The main entry point for the PyChat client.
    Prompts the user for server IP and desired username, then connects to the chat server.
    Handles sending and receiving messages until the user quits or the connection is lost.
    """

    print("Welcome to PyChat Client!")
    print("You will be prompted for the server IP and a desired username.\n")

    # Prompt for server details
    server_ip = input("Enter the server IP address: ").strip() or "127.0.0.1"
    desired_username = input("Enter your desired username: ").strip() or "User"

    # Server port must match the server configuration
    server_port = 42069

    # Attempt to connect to the server
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.connect((server_ip, server_port))
    except Exception as e:
        logging.error(f"Failed to connect to {server_ip}:{server_port}. Error: {e}")
        sys.exit(1)

    # Send the desired username to the server
    try:
        conn.sendall(f"{desired_username}\n".encode())
    except Exception as e:
        logging.error(f"Failed to send username to server: {e}")
        sys.exit(1)

    # Receive the assigned username from the server
    try:
        assigned_line = conn.recv(1024).decode().strip()
    except Exception as e:
        logging.error(f"Failed to receive assigned username from server: {e}")
        sys.exit(1)

    if not assigned_line.startswith("Your username is:"):
        logging.error("Unexpected response from server when assigning username.")
        sys.exit(1)

    assigned_username = assigned_line.replace("Your username is:", "").strip()

    # Display welcome information
    print("\n" + "=" * 50)
    print(f"Welcome, {assigned_username}!")
    print("You are now connected to the chat.")
    print("Type your message and press Enter to send.")
    print("Type /quit to leave the chat.")
    print("=" * 50 + "\n")

    # Event to signal when we should stop reading/writing
    stop_event = threading.Event()

    # Start the message receiver thread
    receiver = threading.Thread(
        target=receive_messages, args=(conn, stop_event), daemon=True
    )
    receiver.start()

    # Initial prompt
    sys.stdout.write("You> ")
    sys.stdout.flush()

    # Main send loop
    while not stop_event.is_set():
        try:
            # Using sys.stdin.readline() to handle Ctrl+D gracefully
            msg = sys.stdin.readline()
            if msg == "":
                # EOF encountered (e.g., user pressed Ctrl+D)
                msg = "/quit"
        except KeyboardInterrupt:
            # If user hits Ctrl+C, treat it as /quit
            msg = "/quit"
        except Exception as e:
            logging.warning(f"Error reading input: {e}")
            msg = "/quit"

        msg = msg.strip()
        if stop_event.is_set():
            break

        if msg.lower() == "/quit":
            # Inform the server we are quitting
            try:
                conn.sendall(msg.encode())
            except Exception:
                pass
            break

        # Send message to the server
        try:
            conn.sendall((msg + "\n").encode())
        except Exception as e:
            logging.warning(f"Failed to send message to server: {e}")
            stop_event.set()
            break

        # Reprint prompt after sending
        sys.stdout.write("You> ")
        sys.stdout.flush()

    # Cleanup
    stop_event.set()
    try:
        conn.close()
    except Exception:
        pass
    print("\n[SYSTEM] Disconnected. Bye!")
    sys.exit(0)


if __name__ == "__main__":
    main()