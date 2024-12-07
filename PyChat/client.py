# client.py

import socket
import threading
import sys

MAX_MESSAGE_SIZE = 1024  # 1KB


def receive_messages(client_socket):
    """
    Listens for messages from the server and prints them.
    """
    while True:
        try:
            message = client_socket.recv(MAX_MESSAGE_SIZE)
            if message:
                decoded_message = message.decode("utf-8").strip()
                if decoded_message.startswith("[SERVER]"):
                    # Display server messages distinctly
                    print(f"\r\033[93m{decoded_message}\033[0m\n> ", end="", flush=True)
                else:
                    # Print regular messages
                    print(f"\r{decoded_message}\n> ", end="", flush=True)
            else:
                # Server closed the connection
                print("\n[INFO] Connection closed by server.")
                client_socket.close()
                break
        except Exception as e:
            print(f"\n[ERROR] An error occurred while receiving messages: {e}")
            client_socket.close()
            break


def send_messages(client_socket):
    """
    Reads user input and sends messages to the server.
    """
    while True:
        try:
            message = input("> ")
            if message.lower() == "quit":
                client_socket.sendall(message.encode("utf-8"))
                client_socket.close()
                print("[INFO] Disconnected from server.")
                break
            elif message.lower() == "/help":
                print(
                    "\nAvailable Commands:\n - quit: Disconnect from the chat\n - /help: Show this help message\n"
                )
            else:
                # Sanitize message
                sanitized_message = "".join(ch for ch in message if ch.isprintable())

                # Limit message size
                encoded_message = sanitized_message.encode("utf-8")
                if len(encoded_message) > MAX_MESSAGE_SIZE:
                    print(
                        "[WARNING] Message too long. Please limit your message to 1KB."
                    )
                    continue

                client_socket.sendall(encoded_message)
        except KeyboardInterrupt:
            client_socket.sendall("quit".encode("utf-8"))
            client_socket.close()
            print("\n[INFO] Disconnected from server.")
            break
        except Exception as e:
            print(f"\n[ERROR] An error occurred while sending messages: {e}")
            client_socket.close()
            break


def main():
    """
    Main function to run the client.
    """
    # Ask the user for the server IP address, port, and nickname
    host = input("Enter the server IP address [localhost]: ") or "localhost"
    port_input = input("Enter the server port [42069]: ") or "42069"
    nickname = input("Enter your nickname [Anonymous]: ") or "Anonymous"

    try:
        port = int(port_input)
    except ValueError:
        print("[ERROR] Port must be an integer.")
        sys.exit()

    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server
    try:
        client_socket.connect((host, port))
        print(f"[CONNECTED] Connected to server at {host}:{port}")
    except ConnectionRefusedError:
        print(f"[ERROR] Unable to connect to server at {host}:{port}")
        sys.exit()
    except socket.gaierror:
        print(f"[ERROR] Invalid server IP address: {host}")
        sys.exit()
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        sys.exit()

    # Send the nickname to the server
    try:
        client_socket.sendall(nickname.encode("utf-8"))
    except Exception as e:
        print(f"[ERROR] Failed to send nickname: {e}")
        client_socket.close()
        sys.exit()

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
