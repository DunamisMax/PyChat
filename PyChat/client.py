# client.py

import socket
import threading
import sys


def receive_messages(client_socket):
    """
    Listens for messages from the server and prints them.
    """
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                # Print the incoming message and re-display the prompt
                print(f"\r{message.decode('utf-8').strip()}\n> ", end="", flush=True)
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
            if message.lower() == "quit":
                client_socket.sendall(message.encode("utf-8"))
                client_socket.close()
                print("[INFO] Disconnected from server.")
                break
            else:
                client_socket.sendall(message.encode("utf-8"))
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")
            client_socket.close()
            break


def main():
    """
    Main function to run the client.
    """
    # Ask the user for the server IP address, port, and nickname
    host = input("Enter the server IP address: ") or "0.0.0.0"
    port_input = input("Enter the server port: ") or "42069"
    nickname = input("Enter your nickname: ") or "Anonymous"
    if not nickname:
        nickname = "Anonymous"

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

    # Send the nickname to the server
    client_socket.sendall(f"{nickname}".encode("utf-8"))

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
